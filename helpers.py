import random

def load_words(file_path='words.txt'):
    try:
        with open(file_path, 'r') as file:
            words = [word.strip().lower() for word in file if len(word.strip()) == 5]
        return words
    except FileNotFoundError:
        print("Error: words.txt file not found.")
        return []

def get_random_word():
    return random.choice(valid_words) if valid_words else None

valid_words = load_words('words.txt')