import enum
from collections import deque
from copy import copy

from exceptions import *


class Operator(enum.Enum):
    NOT = 0
    AND = 1
    OR = 2


class Query:
    def __init__(self, query):
        self._tokens = []
        try:
            self._get_tokens(query)
            self._parse()
        except Exception:
            raise FoogleBadQueryError()

    def _get_tokens(self, query):
        self._tokens = "".join([s.lower() for s in filter(
            lambda x: x.isalnum() or x.isspace() or x in ["(", ")"], query)]) \
            .replace("(", " ( ") \
            .replace(")", " ) ") \
            .split()

    def _parse(self):
        _queue = deque()
        _stack = deque()
        for token in self._tokens:
            if token not in ["and", "or", "not", "(", ")"]:
                _queue.append(token)
            elif token == "not":
                _stack.append(token)
            elif token == "or":
                while _stack and (_stack[-1] == "and"
                                  or _stack[-1] == "not"):
                    _queue.append(_stack.pop())
                _stack.append(token)
            elif token == "and":
                while _stack and (_stack[-1] == "not"):
                    _queue.append(_stack.pop())
                _stack.append(token)
            elif token == "(":
                _stack.append(token)
            elif token == ")":
                while _stack and _stack[-1] != "(":
                    _queue.append(_stack.pop())
                if not _stack:
                    raise FoogleSyntaxError("Mismatched parentheses.")
                _stack.pop()
        while _stack:
            element = _stack.pop()
            if element == "(":
                raise FoogleSyntaxError("Mismatched parentheses.")
            _queue.append(element)
        self._query = _queue
        self._validate_parsed_query(copy(_queue))

    @property
    def data(self):
        return self._query

    @staticmethod
    def _validate_parsed_query(_queue):
        _stack = deque()
        while _queue:
            element = _queue[0]
            if element in ["and", "or"]:
                if len(_stack) < 2:
                    raise FoogleBadQueryError()
                _stack.pop()
                _stack.pop()
                _queue.popleft()
                _stack.append("0")
            elif element == "not":
                if len(_stack) == 0:
                    raise FoogleBadQueryError()
                _stack.pop()
                _queue.popleft()
                _stack.append("0")
            else:
                _stack.append(_queue.popleft())
        if len(_stack) != 1:
            raise FoogleBadQueryError()
    # def parse(self):
    #     _stack = deque()
    #     _queue = deque()
    #     for token in self._tokens:
