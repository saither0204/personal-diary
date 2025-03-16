import spacy

nlp = spacy.load('en_core_web_sm')

def tokenize(text):
    return [token.text for token in nlp(text)]


def get_user_input():
    user_input = input("Please enter your query: ")
    return user_input


if __name__ == '__main__':
    text = get_user_input()
    print(tokenize(text))

    print(nlp.pipe_names)