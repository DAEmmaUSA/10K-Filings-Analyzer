import os
import streamlit as st
from constants import PERSIST_DIRECTORY
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from create_db import create_DB  # ✅ Import the DB creation function

load_dotenv()

def check_vector_db_exists(symbol):
    """Check if vector database exists for the given symbol"""
    folder_path = f"{PERSIST_DIRECTORY}/{symbol}/item_7"

    # Check if directory exists
    if not os.path.exists(folder_path):
        return False, f"Directory {folder_path} does not exist"

    # Check if required FAISS files exist
    required_files = ["index.faiss", "index.pkl"]
    missing_files = []

    for file in required_files:
        file_path = os.path.join(folder_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)

    if missing_files:
        return False, f"Missing FAISS files: {', '.join(missing_files)}"

    return True, "Vector database exists"

def create_tools(symbol):
    """Create tools for the given symbol, automatically creating DB if missing"""

    # Check if vector DB exists
    db_exists, message = check_vector_db_exists(symbol)

    if not db_exists:
        st.warning(f"⚠️ Vector database not found for {symbol}. Creating it now...")
        result = create_DB(symbol)

        if not result.startswith("Success"):
            st.error(f"❌ Failed to create vector database: {result}")
            return None

        st.success(f"✅ Vector database created for {symbol}")

    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            batch_size=16,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        folder_path = f"{PERSIST_DIRECTORY}/{symbol}/item_7"

        db = FAISS.load_local(
            folder_path=folder_path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

        st.success(f"✅ Successfully loaded vector database for {symbol}")
        return db

    except Exception as e:
        st.error(f"❌ Error loading vector database: {str(e)}")
        return None

def create_tools_without_vector_db(symbol):
    """Create basic tools that don't require vector database"""
    st.info(f"🔧 Creating basic tools for {symbol} without vector search")

    # Return basic tools that don't need vector database
    basic_tools = {
        "symbol": symbol,
        "has_vector_db": False,
        "message": "Basic tools without vector search"
    }

    return basic_tools

def list_available_symbols():
    """List all symbols that have vector databases"""
    if not os.path.exists(PERSIST_DIRECTORY):
        return []

    symbols = []
    for item in os.listdir(PERSIST_DIRECTORY):
        symbol_path = os.path.join(PERSIST_DIRECTORY, item)
        if os.path.isdir(symbol_path):
            db_exists, _ = check_vector_db_exists(item)
            if db_exists:
                symbols.append(item)

    return symbols
