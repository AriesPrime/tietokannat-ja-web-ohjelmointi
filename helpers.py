import random

def get_random_word():
    with open('words.txt') as file:
        words = file.readlines()
    return random.choice(words).strip()

def is_valid_word(word):
    with open('words.txt') as file:
        valid_words = [line.strip() for line in file]
    return word in valid_words