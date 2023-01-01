import jaconv
import re
import random


GOJUON = [
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    'が', 'ぎ', 'ぐ', 'げ', 'ご',
    'さ', 'し', 'す', 'せ', 'そ',
    'ざ', 'じ', 'ず', 'ぜ', 'ぞ',
    'た', 'ち', 'つ', 'て', 'と',
    'だ', 'ぢ', 'づ', 'で', 'ど',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ',
    'ば', 'び', 'ぶ', 'べ', 'ぼ',
    'ま', 'み', 'む', 'め', 'も',    
    'や',       'ゆ',       'よ',
    'ら', 'り', 'る', 'れ', 'ろ',
    'わ',
    'ゔ'
]

GOJUON_INITIAL = [
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    # 'が', 'ぎ', 'ぐ', 'げ', 'ご',
    'さ', 'し', 'す', 'せ', 'そ',
    # 'ざ', 'じ', 'ず', 'ぜ', 'ぞ',
    'た', 'ち', 'つ', 'て', 'と',
    # 'だ', 'ぢ', 'づ', 'で', 'ど',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    # 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ',
    # 'ば', 'び', 'ぶ', 'べ', 'ぼ',
    'ま', 'み', 'む', 'め', 'も',    
    'や',       'ゆ',       'よ',
    'ら', 'り', 'る', 'れ', 'ろ',
    'わ'
    # 'わ', 'ゐ', 'ゑ', 'を', 'ん']
]

KOMOJI_CONVERSION = {
    'ぁ': "あ", 'ぃ': "い", 'ぅ': "う", 'ぇ': "え", 'ぉ': "お",
    'ゃ': "や", 'ゅ': "ゆ", 'ょ': "よ", 'っ': "つ"
}

SPECIAL_RULES = {
    "ゐ": "い",
    "ゑ": "え",
    "を": "お",
    "づ": "ず",
    "ぢ": "じ",
}

KANA_RANKING = [
    'ゔ',
    'ず',
    'ぞ',
    'ぬ',
    'ぜ',
    'ぺ',
    'ざ',
    'ぽ',
    'げ',
    'ぴ',
    'ぷ',
    'へ',
    'ぎ',
    'る',
    'ぐ',
    'ね',
    'べ',
    'ぼ',
    'が',
    'び',
    'ぱ',
    'め',
    'れ',
    'け',
    'ご',
    'ぶ',
    'ど',
    'で',
    'む',
    'の',
    'ろ',
    'わ',
    'ば',
    'だ',
    'そ',
    'ゆ',
    'ら',
    'て',
    'り',
    'つ',
    'よ',
    'せ',
    'も',
    'ほ',
    'に',
    'ち',
    'や',
    'え',
    'じ',
    'ひ',
    'す',
    'う',
    'く',
    'と',
    'な',
    'ふ',
    'き',
    'み',
    'は',
    'こ',
    'ま',
    'さ',
    'た',
    'お',
    'し',
    'い',
    'か',
    'あ'
]

def sort_kana_by_difficulty(word):
    try:
        index = KANA_RANKING.index(get_last_char(word))
    except ValueError as e:
        return -1
    return index

def random_initial():
    random.choice(GOJUON_INITIAL)

CHOICES = (   2,    3,    4,    5,    6,    7,    8)
WEIGHTS = (0.05, 0.20, 0.25, 0.25, 0.15, 0.05, 0.05)

def random_length():
    return random.choices(CHOICES, weights=WEIGHTS, k=1)[0]

def special_rules(text: str) -> str:
    for k, v in SPECIAL_RULES.items():
        text = text.replace(k, v)
    return text

def convert_komoji(text: str) -> str:
    for k, v in KOMOJI_CONVERSION.items():
        text = text.replace(k, v)
    return text

def strip_chouon(text: str) -> str:
    return text.strip("ー")

def apply_rules(text: str) -> str:
    return special_rules(convert_komoji(strip_chouon(text)))

def get_last_char(word: str):
    word = apply_rules(jaconv.kata2hira(word))
    return word and word[-1]

def preprocess_input(inputed: str):
    return jaconv.kata2hira(inputed)


kana_pattern = re.compile(r'^[ァ-ヺぁ-ゖー]*$')
non_kana_pattern = re.compile(r'[^\u3041-\u3096\u30A1-\u30FAゔー]+')


def preprocess_dict_word(word: str):
    return jaconv.kata2hira(non_kana_pattern.sub('', word))


def kana_only(word) -> bool:
    return bool(kana_pattern.match(word))
