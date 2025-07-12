import os
import logging
from constants import PERSIST_DIRECTORY, SOURCE_DIRECTORY, TMP_DIRECTORY
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv
from extractor import ItemExtractor

load_dotenv()

def get_recent_folders(dir_path, num_years=5):
    """Get the most recent folders from the directory"""
    if not os.path.exists(dir_path):
        logging.error(f"Directory {dir_path} does not exist")
        return []
    
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
    """Create FAISS vector database for the given symbol"""
    print("SOURCE_DIRECTORY:", SOURCE_DIRECTORY)
    logging.info(f"Loading documents from {SOURCE_DIRECTORY}/{symbol}/10-K/")
    
    # Path to the symbol's 10-K directory
    dir_path = os.path.join(SOURCE_DIRECTORY, symbol, "10-K")
    
    # Check if directory exists
    if not os.path.exists(dir_path):
        logging.error(f"Directory {dir_path} does not exist")
        return f"Error: Directory {dir_path} does not exist"
    
    recent_folders = get_recent_folders(dir_path, num_years=3)
    
    if not recent_folders:
        logging.error(f"No recent folders found for {symbol}")
        return f"Error: No recent folders found for {symbol}"
    
    print(f"Processing folders: {recent_folders}")
    
    all_docs = []
    
    for year_folder in recent_folders:
        year_folder_path = os.path.join(dir_path, year_folder)
        if not os.path.isdir(year_folder_path):
            logging.warning(f"Directory {year_folder_path} does not exist, skipping")
            continue
            
        doc_path = os.path.join(year_folder_path, "primary-document.html")
        if not os.path.exists(doc_path):
            logging.warning(f"Document {doc_path} does not exist, skipping")
            continue
            
        try:
            extractor = ItemExtractor(doc_path)
            # Extract the content for Items 1, 1a, 7, 7a and 8
            item_1_1a_text = extractor.extract_item_1_1a_content()
            item_7_7a_text = extractor.extract_item_7_7a_content()
            item_8_text = extractor.extract_item_8_content()
            all_item_text = item_1_1a_text + '\n' + item_7_7a_text + '\n' + item_8_text
            
            # Save the extracted content to a file
            file_name = f"{symbol}_{year_folder.split('-')[1]}.txt"
            ext_path = os.path.join(TMP_DIRECTORY, file_name)
            
            # Ensure TMP_DIRECTORY exists
            os.makedirs(TMP_DIRECTORY, exist_ok=True)
            
            extractor.save_content_to_file(all_item_text, ext_path)
            
            # Load the extracted content and split it into chunks
            if os.path.exists(ext_path):
                loader = TextLoader(ext_path)
                pages = loader.load_and_split()
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                docs = text_splitter.split_documents(pages)
                all_docs.extend(docs)
                print(f"Added {len(docs)} documents from {year_folder}")
            else:
                logging.warning(f"Extracted file {ext_path} was not created")
                
        except Exception as e:
            logging.error(f"Error processing {year_folder}: {str(e)}")
            continue
    
    if not all_docs:
        logging.error(f"No documents found for {symbol}")
        return f"Error: No documents found for {symbol}"
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        batch_size=16,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Debug print
    print(f"Number of documents: {len(all_docs)}")
    print(f"First doc type: {type(all_docs[0])}")
    
    # Convert to Document objects if needed
    if all_docs and isinstance(all_docs[0], str):
        all_docs = [Document(page_content=doc) for doc in all_docs]
    
    # Create FAISS vectorstore
    try:
        db = FAISS.from_documents(all_docs, embeddings)
        
        # Ensure the persist directory exists
        persist_path = f"{PERSIST_DIRECTORY}/{symbol}/item_7"
        os.makedirs(persist_path, exist_ok=True)
        
        db.save_local(persist_path)
        logging.info(f"Vector database created for {symbol} at {persist_path}")
        print(f"✅ Vector database successfully created for {symbol}")
        return f"Success: Vector database created for {symbol}"
        
    except Exception as e:
        logging.error(f"Error creating vector database: {str(e)}")
        return f"Error creating vector database: {str(e)}"

def main(symbol):
    """Main function to create database for a symbol"""
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    if not symbol:
        print("Error: Symbol cannot be empty")
        return
        
    print(f"Creating database for symbol: {symbol}")
    result = create_DB(symbol)
    print(f"Result: {result}")

if __name__ == "__main__":
    symbol = input("Enter the symbol: ").strip().upper()
    main(symbol)
