import sys
from peewee import chunked
from db import Word
import shiritori
from typing import List, Tuple
import csv
from tqdm import tqdm
import argparse


def filter_predicate(word: str) -> bool:
    word = shiritori.preprocess_dict_word(word)
    last_char = shiritori.get_last_char(word)
    return word and last_char


def filter_n(words: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Filter out words with n.

    Args:
        words (List[Tuple[str, str]]): List of (lemma, word).
    """
    return [
        (lemma, shiritori.preprocess_dict_word(word))
        for lemma, word in words
        if filter_predicate(word)
    ]
    

def load_words(words: List[Tuple[str, str]]):
    """Load words

    Args:
        words (List[(str, str)]): List of (lemma, word).
    """
    words = filter_n(words)
    with tqdm(total=len(words)) as pbar:
        for batch in chunked(words, 10000):
            Word.insert_many(
                [{'lemma': lemma, 'word': word} for lemma, word in batch]
            ).on_conflict_ignore().execute()
            pbar.update(len(batch))


def load_words_from_csv(path: str):
    """Load words from csv file, with title row.

    Args:
        path (str): Path to csv file.
    """
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        return load_words(filter_n(list(
            (row['lemma'], row['word']) for row in reader
        )[1:]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Load words into database.'
    )
    parser.add_argument("-w", "--word", nargs=2, action='append', help="Word to add.", metavar=("LEMMA", "WORD"))
    parser.add_argument("-c", "--csv", action='append', help="Path to CSV file.")
    args = parser.parse_args()

    if args.word:
        print(f"Loading {len(args.word)} word(s)...")
        load_words(args.word)
        print("Done.")
    
    if args.csv:
        for path in args.csv:
            print(f"Loading “{path}”...")
            load_words_from_csv(path)
            print("Done.")

    if not args.word and not args.csv:
        parser.print_help()
