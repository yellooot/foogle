import os.path

try:
    import chardet
    import docx2txt
    import PyPDF2
except ImportError:
    exit("Please make sure that all required modules are installed.")
import math
import pathlib
from collections import defaultdict, deque
from copy import copy

SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".rtf", ".txt"}


class Foogle:
    def __init__(self, directory):
        directory = pathlib.Path(directory)
        self._files = list()
        for extension in SUPPORTED_EXTENSIONS:
            self._files.extend(list(directory.rglob(f"*{extension}")))
        self._id_by_path = dict()
        self._path_by_id = dict()
        self._postings = defaultdict(list)
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
            case ".txt":
                with open(path, "r", encoding=self._get_encoding(path)) as f:
                    return f.read()
            case ".docx":
                return docx2txt.process(path)
            case ".pdf":
                with open(path, "rb") as f:
                    pdfdoc = PyPDF2.PdfReader(f)
                    return "\n".join([page.extract_text()
                                      for page in pdfdoc.pages])
            case ".rtf":
                with open(path, "r", encoding=self._get_encoding(path)) as f:
                    return f.read()

    def _index(self):
        for file in self._files:
            data = self._read_file(file)
            document_id = self._id_by_path[file]
            terms = "".join([s.lower() for s in
                             filter(lambda x: x.isalnum() or x.isspace(),
                                    data)]).split()
            for term in terms:
                self._tf[(term, document_id)] += 1
                self._postings[term].append(document_id)
            terms_set = set(terms)
            for term in terms_set:
                self._tf[(term, document_id)] /= len(terms)

    def _search(self, postfix_query):
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
                _stack.append(set(self._postings[token]))
        return _stack[0]

    def search(self, postfix_query):
        ids = self._search(postfix_query)
        return [self._path_by_id[_id] for _id in ids]

    def _relevant(self, postfix_query, k=3):
        if k > 10:
            k = 10
        terms = set(term for term in list(postfix_query)
                    if term not in ["&", "|", "!"])
        documents = self._search(postfix_query)
        score = defaultdict(int)
        for document in documents:
            for term in terms:
                score[document] += self.get_tf_idf(document, term)
        return sorted(documents, key=lambda d: -score[d])[:k]

    def relevant(self, postfix_query, k=3):
        return [self._path_by_id[_id] for _id
                in self._relevant(postfix_query, k)]

    def get_tf_idf(self, document_id, term):
        if document_id not in self._postings[term]:
            return 0
        return self._tf[(term, document_id)] \
            * math.log(len(self._files) / len(set(self._postings[term])), 10)
