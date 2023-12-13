print("Initialization. Please wait..")

RUSSIAN_ALPHABET = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
ENGLISH_ALPHABET = set("abcdefghijklmnopqrstuvwxyz")

try:
    import pymorphy3
    from word_forms.word_forms import get_word_forms as get_english_forms
except ImportError:
    exit("Please make sure that all required modules are installed.")


def get_word_forms(word: str) -> set[str]:
    if not len(set(word) - RUSSIAN_ALPHABET):
        morph = pymorphy3.MorphAnalyzer()
        lexeme = morph.parse(word)[0].lexeme
        return set([_form[0] for _form in lexeme]).union({word})
    elif not len(set(word) - ENGLISH_ALPHABET):
        forms = get_english_forms(word)
        return forms["n"].union(forms["a"]).union(forms["v"]) \
            .union(forms["r"]).union({word})
    return {word}
