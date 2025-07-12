import os
import streamlit as st
from constants import PERSIST_DIRECTORY
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

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
    """Create tools for the given symbol, handling missing vector database gracefully"""
    
    # Check if vector database exists first
    db_exists, message = check_vector_db_exists(symbol)
    
    if not db_exists:
        st.error(f"❌ Vector database not found for {symbol}")
        st.error(f"Details: {message}")
        st.info("💡 **How to fix this:**")
        st.info("1. Run the database creation script:")
        st.code("python create_db.py", language="bash")
        st.info(f"2. Enter '{symbol}' when prompted")
        st.info("3. Wait for processing to complete")
        st.info("4. Refresh this page")
        
        # Return None to indicate failure
        return None
    
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            batch_size=16,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        folder_path = f"{PERSIST_DIRECTORY}/{symbol}/item_7"
        
        # Attempt to load the FAISS database
        db = FAISS.load_local(
            folder_path=folder_path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        
        st.success(f"✅ Successfully loaded vector database for {symbol}")
        
        # Return the database or your actual tools
        return db
        
    except Exception as e:
        st.error(f"❌ Error loading vector database for {symbol}")
        st.error(f"Error details: {str(e)}")
        st.info("💡 **Troubleshooting:**")
        st.info("1. The vector database may be corrupted")
        st.info("2. Try recreating it by running:")
        st.code("python create_db.py", language="bash")
        st.info(f"3. Enter '{symbol}' when prompted")
        return None

def create_tools_without_vector_db(symbol):
    """Create basic tools that don't require vector database"""
    st.info(f"🔧 Creating basic tools for {symbol} without vector search")
    
    # Return basic tools that don't need vector database
    # This is a fallback for when vector DB is not available
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
