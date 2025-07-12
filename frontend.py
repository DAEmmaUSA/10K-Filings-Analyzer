import streamlit as st
import os
import sys
import time
from tools import create_tools, create_tools_without_vector_db, list_available_symbols, check_vector_db_exists

def create_database_in_streamlit(symbol):
    """Create database directly in Streamlit with progress tracking"""
    try:
        # Import the database creation function
        from create_db import create_DB
        
        # Create progress indicators
        progress = st.progress(0)
        status = st.empty()
        
        # Step 1: Initialize
        status.info("🔄 Initializing database creation...")
        progress.progress(10)
        time.sleep(0.5)
        
        # Step 2: Loading documents
        status.info("📥 Loading and processing 10-K filings...")
        progress.progress(30)
        
        # Call your database creation function
        result = create_DB(symbol)
        
        # Step 3: Creating embeddings
        progress.progress(70)
        status.info("🧮 Creating embeddings with OpenAI...")
        time.sleep(1)
        
        # Step 4: Saving database
        progress.progress(90)
        status.info("💾 Saving vector database...")
        time.sleep(0.5)
        
        # Step 5: Complete
        progress.progress(100)
        status.success("✅ Database created successfully!")
        
        # Verify the database was created
        db_exists, message = check_vector_db_exists(symbol)
        if db_exists:
            st.success(f"🎉 Vector database for {symbol} is ready!")
            return True
        else:
            st.error(f"❌ Database creation may have failed: {message}")
            return False
            
    except ImportError as e:
        st.error("❌ Could not import create_db module")
        st.error(f"Make sure create_db.py is in your project directory: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Error creating database: {str(e)}")
        
        # Show detailed error info
        with st.expander("🔍 Error Details"):
            st.write(f"Error type: {type(e).__name__}")
            st.write(f"Error message: {str(e)}")
            st.write(f"Symbol: {symbol}")
        
        return False

def load_tools(symbol):
    """Load tools for the given symbol with comprehensive error handling"""
    
    if not symbol:
        st.warning("Please enter a stock symbol")
        return None
    
    # Check if database exists first
    db_exists, message = check_vector_db_exists(symbol)
    
    if not db_exists:
        return None  # Database doesn't exist, will be handled by main()
    
    with st.spinner(f"Loading tools for {symbol}..."):
        try:
            tools = create_tools(symbol)
            return tools
            
        except Exception as e:
            st.error(f"❌ Unexpected error loading tools for {symbol}")
            st.error(f"Error: {str(e)}")
            
            # Show debug info
            with st.expander("🔍 Debug Information"):
                st.write(f"Symbol: {symbol}")
                st.write(f"Error type: {type(e).__name__}")
                st.write(f"Error message: {str(e)}")
            
            return None

def show_database_status(symbol):
    """Show the current status of the database for a symbol"""
    db_exists, message = check_vector_db_exists(symbol)
    
    if db_exists:
        st.success(f"✅ Vector database ready for {symbol}")
        return True
    else:
        st.warning(f"⚠️ Vector database not found for {symbol}")
        st.info(f"Details: {message}")
        return False

def show_environment_info():
    """Show environment information for debugging"""
    with st.expander("🔍 Environment Information"):
        st.write(f"**Current directory:** {os.getcwd()}")
        st.write(f"**Python executable:** {sys.executable}")
        st.write(f"**Platform:** {sys.platform}")
        
        # Check if key files exist
        files_to_check = ['create_db.py', 'tools.py', 'constants.py']
        for file in files_to_check:
            exists = os.path.exists(file)
            st.write(f"**{file}:** {'✅ Found' if exists else '❌ Missing'}")
        
        # Check directories
        try:
            from constants import PERSIST_DIRECTORY, SOURCE_DIRECTORY
            st.write(f"**PERSIST_DIRECTORY:** {PERSIST_DIRECTORY}")
            st.write(f"**SOURCE_DIRECTORY:** {SOURCE_DIRECTORY}")
            st.write(f"**PERSIST_DIRECTORY exists:** {'✅ Yes' if os.path.exists(PERSIST_DIRECTORY) else '❌ No'}")
            st.write(f"**SOURCE_DIRECTORY exists:** {'✅ Yes' if os.path.exists(SOURCE_DIRECTORY) else '❌ No'}")
        except ImportError:
            st.write("❌ Could not import constants")

def main():
    st.set_page_config(
        page_title="10-K Filings Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 10-K Filings Analyzer")
    st.markdown("Analyze 10-K filings using AI-powered vector search")
    
    # Sidebar with available symbols and environment info
    with st.sidebar:
        st.header("📋 Available Symbols")
        available_symbols = list_available_symbols()
        
        if available_symbols:
            st.success(f"✅ {len(available_symbols)} symbols ready:")
            for sym in sorted(available_symbols):
                st.write(f"• {sym}")
        else:
            st.info("No vector databases found")
            st.write("Create one using the main interface →")
        
        st.markdown("---")
        
        # Environment info
        show_environment_info()
    
    # Main interface
    st.markdown("### 🎯 Enter Stock Symbol")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol = st.text_input(
            "Stock Symbol:",
            value="",
            placeholder="e.g., AAPL, MSFT, GOOGL",
            help="Enter the stock symbol to analyze its 10-K filings",
            label_visibility="collapsed"
        ).strip().upper()
    
    with col2:
        if st.button("🔄 Refresh", help="Refresh the page"):
            st.rerun()
    
    if symbol:
        st.markdown("---")
        
        # Check database status
        database_ready = show_database_status(symbol)
        
        if not database_ready:
            st.markdown("### 🛠️ Database Creation Required")
            st.markdown(f"The vector database for **{symbol}** needs to be created first.")
            
            # Two-column layout for options
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 🚀 Create Database Now")
                st.markdown("Click the button below to create the database directly in this app:")
                
                if st.button(f"🚀 Create Database for {symbol}", type="primary", use_container_width=True):
                    success = create_database_in_streamlit(symbol)
                    if success:
                        st.balloons()  # Celebration animation
                        time.sleep(2)
                        st.rerun()  # Refresh the page to show the new database
                
                st.markdown("**⏱️ Estimated time:** 2-5 minutes")
                st.markdown("**💰 Cost:** ~$0.01-0.05 in OpenAI API usage")
            
            with col2:
                st.markdown("#### 💡 What This Does")
                st.markdown("""
                - Downloads 10-K filings
                - Extracts key sections
                - Creates AI embeddings
                - Builds searchable database
                """)
            
            # Show detailed info
            with st.expander("📋 Database Creation Details"):
                st.markdown("""
                **What gets processed:**
                - **Item 1:** Business description
                - **Item 1A:** Risk factors  
                - **Item 7:** Management discussion & analysis
                - **Item 7A:** Quantitative disclosures
                - **Item 8:** Financial statements
                
                **Processing steps:**
                1. Load recent 10-K filings (last 3 years)
                2. Extract relevant sections from HTML
                3. Split into manageable chunks
                4. Create embeddings using OpenAI
                5. Save to FAISS vector database
                
                **Requirements:**
                - OpenAI API key (for embeddings)
                - Internet connection
                - ~2-5 minutes processing time
                """)
        
        else:
            # Database exists, try to load tools
            agent = load_tools(symbol)
            
            if agent is not None:
                st.success(f"✅ Successfully loaded tools for **{symbol}**")
                
                # Main analysis interface
                st.markdown("### 💬 Ask Questions About the 10-K Filing")
                
                # Example questions
                with st.expander("💡 Example Questions"):
                    st.markdown("""
                    - What are the main risk factors?
                    - What was the revenue growth last year?
                    - How does the company describe its competitive position?
                    - What are the key business segments?
                    - What major investments or acquisitions were made?
                    """)
                
                user_input = st.text_area(
                    "Enter your question:",
                    placeholder="e.g., What are the main risk factors facing the company?",
                    height=100
                )
                
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    analyze_button = st.button("🔍 Analyze", disabled=not user_input, use_container_width=True)
                
                with col2:
                    if not user_input:
                        st.info("👆 Enter a question above to analyze the 10-K filing")
                
                if analyze_button and user_input:
                    with st.spinner("🔍 Analyzing 10-K filing..."):
                        try:
                            # Here you would use your agent to process the question
                            # response = agent.run(user_input)
                            # st.markdown("### 📊 Analysis Result")
                            # st.write(response)
                            
                            # Placeholder response for now
                            st.markdown("### 📊 Analysis Result")
                            st.info("🚧 **Analysis functionality will be implemented here**")
                            
                            with st.expander("🔍 Debug Info"):
                                st.write(f"**Question:** {user_input}")
                                st.write(f"**Symbol:** {symbol}")
                                st.write(f"**Agent loaded:** {agent is not None}")
                                
                        except Exception as e:
                            st.error(f"❌ Error during analysis: {str(e)}")
            
            else:
                st.error("❌ Could not load tools despite database existing")
                st.info("💡 Try refreshing the page or recreating the database")
                
                if st.button("🔄 Recreate Database"):
                    success = create_database_in_streamlit(symbol)
                    if success:
                        st.rerun()
    
    else:
        st.info("👆 Please enter a stock symbol to begin")
        
        # Show popular symbols as clickable buttons
        st.markdown("### 💡 Popular Symbols")
        st.markdown("Click on any symbol below to get started:")
        
        # Group symbols in rows
        symbols_data = [
            {"symbol": "AAPL", "name": "Apple", "emoji": "🍎"},
            {"symbol": "MSFT", "name": "Microsoft", "emoji": "💻"},
            {"symbol": "GOOGL", "name": "Google", "emoji": "🔍"},
            {"symbol": "AMZN", "name": "Amazon", "emoji": "📦"},
            {"symbol": "TSLA", "name": "Tesla", "emoji": "🚗"},
            {"symbol": "META", "name": "Meta", "emoji": "📱"},
        ]
        
        # Create 3 columns for 2 rows of symbols
        cols = st.columns(3)
        
        for i, symbol_info in enumerate(symbols_data):
            with cols[i % 3]:
                if st.button(
                    f"{symbol_info['emoji']} {symbol_info['symbol']}\n{symbol_info['name']}", 
                    key=f"example_{symbol_info['symbol']}",
                    use_container_width=True
                ):
                    # Update the text input and rerun
                    st.session_state.symbol_input = symbol_info['symbol']
                    st.rerun()

if __name__ == "__main__":
    main()
