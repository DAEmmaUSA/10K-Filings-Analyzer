import os

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# Define the folder for downloading the data
SOURCE_DIRECTORY = f"{ROOT_DIRECTORY}/sec-edgar-filings"

# Define the folder for storing the temporary files
TMP_DIRECTORY = f"{ROOT_DIRECTORY}/tmp"

# Define the folder for storing database
PERSIST_DIRECTORY = f"{ROOT_DIRECTORY}/embeddings"