import nltk
import os

# Set download directory to current working directory
current_dir = os.getcwd()
download_dir = os.path.join(current_dir, 'downloads')
if not os.path.exists(download_dir):
	os.makedirs(download_dir)
nltk.download('punkt', download_dir=download_dir)
nltk.download('averaged_perceptron_tagger', download_dir=download_dir)