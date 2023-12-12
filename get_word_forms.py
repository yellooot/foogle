print("Initialization. Please wait..")

RUSSIAN_ALPHABET = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
ENGLISH_ALPHABET = set("abcdefghijklmnopqrstuvwxyz")
ALPHABET = RUSSIAN_ALPHABET.union(ENGLISH_ALPHABET)

try:
    import pymorphy2
    from word_forms.word_forms import get_word_forms as get_english_forms
except ImportError:
    exit("Please make sure that all required modules are installed.")

def get_word_forms(word):
    if len(set(word) - ALPHABET):
        return list([word])
    if len(set(word) - RUSSIAN_ALPHABET) == 0:
        morph = pymorphy2.MorphAnalyzer()
        lexeme = morph.parse(word)[0].lexeme
        return set([_form[0] for _form in lexeme]).union({word})
    elif len(set(word) - ENGLISH_ALPHABET) == 0:
        forms = get_english_forms(word)
        return forms["n"].union(forms["a"]).union(forms["v"]) \
            .union(forms["r"]).union({word})
    else:
        return list([word])
