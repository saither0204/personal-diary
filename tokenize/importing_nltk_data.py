import nltk
from nltk.tokenize import word_tokenize
import spacy

# Load SpaCy's English model
nlp = spacy.load("en_core_web_sm")

def tokenize_with_nltk(user_input):
    try:
        tokens = word_tokenize(user_input)
        return tokens
    except Exception as e:
        print(f"Error occurred during NLTK tokenization: {e}")
        return None

def tokenize_with_spacy(user_input):
    try:
        doc = nlp(user_input)
        tokens = [token.text for token in doc]
        return tokens
    except Exception as e:
        print(f"Error occurred during SpaCy tokenization: {e}")
        return None

def get_user_input():
    user_input = input("Please enter your query: ")
    return user_input

if __name__ == '__main__':
    user_input = get_user_input()
    
    # Tokenize with NLTK
    nltk_tokens = tokenize_with_nltk(user_input)
    if nltk_tokens:
        print("NLTK Tokens:", nltk_tokens)
    else:
        print("NLTK Tokenization failed.")
    
    # Tokenize with SpaCy
    spacy_tokens = tokenize_with_spacy(user_input)
    if spacy_tokens:
        print("SpaCy Tokens:", spacy_tokens)
    else:
        print("SpaCy Tokenization failed.")