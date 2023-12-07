try:
    import chardet
except ImportError:
    exit("Please install chardet module.")
import math
import pathlib
from collections import defaultdict, deque
from copy import copy


class Foogle:
    def __init__(self, directory):
        directory = pathlib.Path(directory)
        self._files = list(directory.rglob("*.txt"))
        self._id_by_path = dict()
        self._path_by_id = dict()
        self._postings = defaultdict(list)
        self._tf = defaultdict(float)
        for i, file in enumerate(self._files):
            self._id_by_path[file] = i
            self._path_by_id[i] = file
        self._directory = directory
        self.index()

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

    def index(self):
        for file in self._files:
            document_id = self._id_by_path[file]
            encoding = self._get_encoding(file)
            with open(file, "r", encoding=encoding) as f:
                terms = "".join([s.lower() for s in
                                 filter(lambda x: x.isalnum() or x.isspace(),
                                        f.read())]).split()
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

            if token == "and":
                first, second = _stack.pop(), _stack.pop()
                _stack.append(first.intersection(second))
            elif token == "or":
                first, second = _stack.pop(), _stack.pop()
                _stack.append(first.union(second))
            elif token == "not":
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
                    if term not in ["not", "and", "or"])
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
