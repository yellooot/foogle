import enum
from collections import deque
from copy import copy

from get_word_forms import get_word_forms
from exceptions import FoogleBadQueryError, FoogleSyntaxError


class Operator(enum.Enum):
    NOT = 0
    AND = 1
    OR = 2


class Query:
    def __init__(self, query, is_logical=True):
        self._tokens = []
        self._is_logical = is_logical
        try:
            self._get_tokens(query)
            self._add_inexact_forms()
            self._parse()
        except Exception:
            raise FoogleBadQueryError()

    @property
    def is_logical(self):
        return self._is_logical

    def _get_tokens(self, query):
        self._tokens = "".join([s.lower() for s in filter(
            lambda x: x.isalnum() or x.isspace() or x in ["(", ")", "~"],
            query)]) \
            .replace("(", " ( ") \
            .replace(")", " ) ") \
            .split()
        if self._is_logical:
            _tokens = []
            for token in self._tokens:
                match token:
                    case "and":
                        _tokens.append("&")
                    case "or":
                        _tokens.append("|")
                    case "not":
                        _tokens.append("!")
                    case _:
                        _tokens.append(token)
            self._tokens = _tokens
        else:
            _tokens = ["&"] * (len(self._tokens) * 2 - 1)
            _tokens[0::2] = self._tokens
            self._tokens = _tokens

    def _parse(self):
        _queue = deque()
        _stack = deque()
        for token in self._tokens:
            if token not in ["&", "|", "!", "(", ")"]:
                _queue.append(token)
            elif token == "!":
                _stack.append(token)
            elif token == "|":
                while _stack and (_stack[-1] == "&"
                                  or _stack[-1] == "!"):
                    _queue.append(_stack.pop())
                _stack.append(token)
            elif token == "&":
                while _stack and (_stack[-1] == "!"):
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
            if element in ["&", "|"]:
                if len(_stack) < 2:
                    raise FoogleBadQueryError()
                _stack.pop()
                _stack.pop()
                _queue.popleft()
                _stack.append("0")
            elif element == "!":
                if len(_stack) == 0:
                    raise FoogleBadQueryError()
                _stack.pop()
                _queue.popleft()
                _stack.append("0")
            else:
                _stack.append(_queue.popleft())
        if len(_stack) != 1:
            raise FoogleBadQueryError()

    def _add_inexact_forms(self):
        new_tokens = deque()
        for token in self._tokens:
            if token in ["&", "|", "!"] or token[0] != "~":
                new_tokens.append(token)
            else:
                _word = token[1:]
                if len(_word) == 0:
                    continue
                forms = list(get_word_forms(_word))
                new_tokens.append("(")
                for i in range(len(forms) - 1):
                    new_tokens.append(forms[i])
                    new_tokens.append("|")
                new_tokens.append(forms[-1])
                new_tokens.append(")")
        self._tokens = new_tokens
