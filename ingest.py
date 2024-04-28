import os
import logging
from constants import PERSIST_DIRECTORY, SOURCE_DIRECTORY, TMP_DIRECTORY

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from extractor import Item7Extractor

load_dotenv()
print(PERSIST_DIRECTORY, SOURCE_DIRECTORY, TMP_DIRECTORY)

def get_recent_folders(dir_path, num_years=5):
    # List all subdirectories in the given directory
    all_entries = os.listdir(dir_path)

    all_folders = [entry for entry in all_entries if os.path.isdir(os.path.join(dir_path, entry)) and int(entry.split('-')[1]) < 25]

    # Extract years and sort them, assuming the folder format includes the year as shown
    # Folder format example: "0000320193-21-000105"
    # Extracts the '21' part as the year, assumes all years are from 2000 onwards
    sorted_folders = sorted(all_folders, key=lambda x: int('20' + x.split('-')[1]), reverse=True)

    # Get the most recent 'num_years' folders
    recent_folders = sorted_folders[:num_years]
    return recent_folders

def create_DB(symbol):
    logging.info(f"Loading documents from {SOURCE_DIRECTORY}/{symbol}/10-K/")
    # Path to the symbol's 10-K directory
    dir_path = os.path.join(SOURCE_DIRECTORY, symbol, "10-K")
    recent_folders = get_recent_folders(dir_path, num_years=3)
    print(recent_folders)
    # List all subdirectories in the 10-K directory
    all_docs = []
    for year_folder in recent_folders:
        year_folder_path = os.path.join(dir_path, year_folder)
        if not os.path.isdir(year_folder_path):
            raise(f"Directory {year_folder_path} does not exist")
        doc_path = os.path.join(year_folder_path, "primary-document.html")
        extractor = Item7Extractor(doc_path)
        item_7_text = extractor.extract_item_7_content()
        file_name = f"{symbol}_{year_folder.split('-')[1]}_item_7.txt"
        ext_path = os.path.join(TMP_DIRECTORY, file_name)
        extractor.save_content_to_file(item_7_text, ext_path)
        if os.path.exists(ext_path):  # Checking if the file exists
            print("File path:", ext_path)
            loader = TextLoader(ext_path)
            pages = loader.load_and_split()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(pages)
            all_docs.extend(docs)
    embeddings = CohereEmbeddings()
    db = Chroma.from_documents(all_docs, embeddings, persist_directory=f"{PERSIST_DIRECTORY}/{symbol}/item_7")
    return ""


def main(symbol):
    create_DB(symbol)


if __name__ == "__main__":
    symbol = input("Enter the symbol: ")
    main(symbol)