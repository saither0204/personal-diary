import nltk
from nltk.tokenize import word_tokenize

def tokenize_input(user_input):
    try:
        tokens = word_tokenize(user_input)
        return tokens
    except Exception as e:
        print(f"Error occurred during tokenization: {e}")
        return None

def get_user_input():
    user_input = input("Please enter your query: ")
    return user_input


if __name__ == '__main__':
    user_input = get_user_input()
    tokens = tokenize_input(user_input)
    if tokens:
        print(tokens)
    else:
        print("Tokenization failed.")