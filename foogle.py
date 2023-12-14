import math
import os.path

try:
    import chardet
    import docx2txt
    import PyPDF2
except ImportError:
    exit("Please make sure that all required modules are installed.")
import pathlib
from collections import defaultdict, deque
from copy import copy


class Foogle:
    SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".rtf", ".txt"}

    def __init__(self, directory):
        directory = pathlib.Path(directory)
        self._files = list()
        self._files_count_by_extension = defaultdict(int)
        for extension in Foogle.SUPPORTED_EXTENSIONS:
            self._files.extend(list(directory.rglob(f"*{extension}")))
        for file in self._files:
            self._files_count_by_extension[os.path.splitext(file)[1]] += 1
        self._id_by_path = dict()
        self._path_by_id = dict()
        self._postings = defaultdict(lambda: defaultdict(list))
        self._tf = defaultdict(float)
        for i, file in enumerate(self._files):
            self._id_by_path[file] = i
            self._path_by_id[i] = file
        self._directory = directory
        self._index()

    @staticmethod
    def _get_encoding(file_path):
        with open(file_path, "rb") as file:
            detector = chardet.UniversalDetector()
            for line in file:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
            return detector.result["encoding"]

    def _read_file(self, path):
        _, extension = os.path.splitext(path)
        match extension:
            case ".txt" | ".rtf":
                with open(path, "r", encoding=self._get_encoding(path)) as f:
                    return f.read()
            case ".docx":
                return docx2txt.process(path)
            case ".pdf":
                with open(path, "rb") as f:
                    return "\n".join([page.extract_text()
                                      for page in PyPDF2.PdfReader(f).pages])

    def _index(self):
        for file in self._files:
            extension = os.path.splitext(file)[1]
            data = self._read_file(file)
            document_id = self._id_by_path[file]
            terms = "".join([s.lower() for s in
                             filter(lambda x: x.isalnum() or x.isspace(),
                                    data)]).split()
            for term in terms:
                self._tf[(term, document_id)] += 1
                self._postings[term][extension].append(document_id)
            terms_set = set(terms)
            for term in terms_set:
                self._tf[(term, document_id)] /= len(terms)

    def _search(self, postfix_query, extension):
        _query = copy(postfix_query)
        _stack = deque()
        while _query:
            token = _query.popleft()
            if token == "&":
                first, second = _stack.pop(), _stack.pop()
                _stack.append(first.intersection(second))
            elif token == "|":
                first, second = _stack.pop(), _stack.pop()
                _stack.append(first.union(second))
            elif token == "!":
                _stack.append(set(self._path_by_id.keys()) - _stack.pop())
            else:
                _stack.append(set(self._postings[token][extension]))
        return _stack[0]

    def search(self, postfix_query, extensions):
        result = []
        for extension in extensions:
            result += [self._path_by_id[_id]
                       for _id in self._search(postfix_query, extension)]
        return result

    def _search_with_extensions(self, postfix_query, extensions):
        documents = set()
        for ext in extensions:
            documents = documents.union(self._search(postfix_query, ext))

        return documents

    def _relevant(self, postfix_query, extensions, k=3):
        if k > 50:
            k = 50
        terms = set(term for term in list(postfix_query)
                    if term not in ["&", "|", "!"])

        documents = self._search_with_extensions(postfix_query, extensions)

        score = defaultdict(int)
        for document in documents:
            for term in terms:
                score[document] += self.get_tf_idf(document, term, extensions)
        return sorted(documents, key=lambda d: -score[d])[:k]

    def relevant(self, postfix_query, extensions, k=3):
        return [self._path_by_id[_id] for _id
                in self._relevant(postfix_query, extensions, k)]

    def get_tf_idf(self, document_id, term, extensions):
        all_files_count = sum([self._files_count_by_extension[ext]
                               for ext in extensions])
        good_files_count = sum([len(set(self._postings[term][ext]))
                                for ext in extensions])
        if not self._is_term_in_document(document_id, term, extensions):
            return 0
        tf = self._tf[(term, document_id)]
        idf = math.log(all_files_count / good_files_count, 10)
        return tf * idf

    def _is_term_in_document(self, document_id, term, extensions):
        for ext in extensions:
            if document_id in self._postings[term][ext]:
                return True
        return False
