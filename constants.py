import os

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# Define the folder for storing database
SOURCE_DIRECTORY = f"{ROOT_DIRECTORY}/sec-edgar-filings"

TMP_DIRECTORY = f"{ROOT_DIRECTORY}/tmp"

PERSIST_DIRECTORY = f"{ROOT_DIRECTORY}/embeddings"