import os
import logging
from constants import PERSIST_DIRECTORY, SOURCE_DIRECTORY, TMP_DIRECTORY

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
# from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from extractor import ItemExtractor

load_dotenv()

def get_recent_folders(dir_path, num_years=5):
    all_entries = os.listdir(dir_path)

    # Filter out only the folders after the year 2000
    # "0000320193-98-000105" -> not a valid year
    # "0000320193-21-000105" -> valid year
    all_folders = [entry for entry in all_entries if os.path.isdir(os.path.join(dir_path, entry)) and int(entry.split('-')[1]) < 25]

    # Extract years and sort them, assuming the folder format includes the year as shown
    # Folder format example: "0000320193-21-000105"
    # Extracts the '21' part as the year
    sorted_folders = sorted(all_folders, key=lambda x: int('20' + x.split('-')[1]), reverse=True)

    # Get the most recent 'num_years' folders
    recent_folders = sorted_folders[:num_years]
    return recent_folders

def create_DB(symbol):
    logging.info(f"Loading documents from {SOURCE_DIRECTORY}/{symbol}/10-K/")
    # Path to the symbol's 10-K directory
    dir_path = os.path.join(SOURCE_DIRECTORY, symbol, "10-K")
    recent_folders = get_recent_folders(dir_path, num_years=3)
    # print(recent_folders)
    all_docs = []
    for year_folder in recent_folders:
        year_folder_path = os.path.join(dir_path, year_folder)
        if not os.path.isdir(year_folder_path):
            raise(f"Directory {year_folder_path} does not exist")
        doc_path = os.path.join(year_folder_path, "primary-document.html")
        extractor = ItemExtractor(doc_path)

        # Extract the content for Items 1, 1a, 7, 7a and 8
        item_1_1a_text = extractor.extract_item_1_1a_content()
        item_7_7a_text = extractor.extract_item_7_7a_content()
        item_8_text = extractor.extract_item_8_content()
        all_item_text = item_1_1a_text + '\n' + item_7_7a_text + '\n' + item_8_text

        # Save the extracted content to a file
        file_name = f"{symbol}_{year_folder.split('-')[1]}.txt"
        ext_path = os.path.join(TMP_DIRECTORY, file_name)
        extractor.save_content_to_file(all_item_text, ext_path)

        # Load the extracted content and split it into chunks
        if os.path.exists(ext_path):
            # print("File path:", ext_path)
            loader = TextLoader(ext_path)
            pages = loader.load_and_split()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(pages)
            all_docs.extend(docs)
    embeddings = OpenAIEmbeddings()

    # Create a vector store from the documents
    db = FAISS.from_documents(all_docs, embeddings)
    logging.info(f"Vector database created for {symbol}")
    return ""


def main(symbol):
    create_DB(symbol)


if __name__ == "__main__":
    symbol = input("Enter the symbol: ")
    main(symbol)
