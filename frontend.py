import streamlit as st
from tools import create_tools, create_tools_without_vector_db, list_available_symbols

def load_tools(symbol):
    """Load tools for the given symbol with comprehensive error handling"""
    
    if not symbol:
        st.warning("Please enter a stock symbol")
        return None
    
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

def show_database_creation_instructions(symbol):
    """Show instructions for creating the database"""
    st.markdown("### 🛠️ Database Creation Required")
    st.markdown(f"The vector database for **{symbol}** needs to be created first.")
    
    st.markdown("#### Step-by-step instructions:")
    st.markdown("1. **Open a terminal/command prompt**")
    st.markdown("2. **Navigate to your project directory**")
    st.markdown("3. **Run the database creation script:**")
    st.code("python create_db.py", language="bash")
    st.markdown("4. **Enter the symbol when prompted:**")
    st.code(symbol, language="text")
    st.markdown("5. **Wait for processing to complete** (this may take a few minutes)")
    st.markdown("6. **Refresh this page**")
    
    st.markdown("#### What the script does:")
    st.markdown("- Downloads and processes 10-K filings")
    st.markdown("- Extracts relevant sections (Items 1, 1A, 7, 7A, 8)")
    st.markdown("- Creates embeddings using OpenAI")
    st.markdown("- Saves the vector database for fast retrieval")

def main():
    st.set_page_config(
        page_title="10-K Filings Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 10-K Filings Analyzer")
    st.markdown("Analyze 10-K filings using AI-powered vector search")
    
    # Sidebar with available symbols
    with st.sidebar:
        st.header("Available Symbols")
        available_symbols = list_available_symbols()
        
        if available_symbols:
            st.success(f"✅ {len(available_symbols)} symbols ready:")
            for sym in available_symbols:
                st.write(f"• {sym}")
        else:
            st.info("No vector databases found")
            st.write("Create one using the main interface →")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input(
            "Enter Stock Symbol:",
            value="",
            placeholder="e.g., AAPL, MSFT, GOOGL",
            help="Enter the stock symbol to analyze its 10-K filings"
        ).strip().upper()
    
    with col2:
        if st.button("🔄 Refresh", help="Refresh the page"):
            st.rerun()
    
    if symbol:
        st.markdown("---")
        
        # Try to load tools
        agent = load_tools(symbol)
        
        if agent is not None:
            st.success(f"✅ Successfully loaded tools for **{symbol}**")
            
            # Your main app logic here
            st.markdown("### 💬 Ask Questions About the 10-K Filing")
            
            user_input = st.text_area(
                "Enter your question:",
                placeholder="e.g., What are the main risk factors? What was the revenue growth?",
                height=100
            )
            
            if st.button("🔍 Analyze", disabled=not user_input):
                if user_input:
                    with st.spinner("Analyzing..."):
                        try:
                            # Here you would use your agent to process the question
                            # response = agent.run(user_input)
                            # st.write(response)
                            
                            # Placeholder response
                            st.info("🚧 Analysis functionality will be implemented here")
                            st.write(f"Question: {user_input}")
                            st.write(f"Symbol: {symbol}")
                            
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                else:
                    st.warning("Please enter a question first")
        
        else:
            # Show database creation instructions
            show_database_creation_instructions(symbol)
    
    else:
        st.info("👆 Please enter a stock symbol to begin")
        
        # Show some example symbols
        st.markdown("### 💡 Popular Symbols to Try:")
        example_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"]
        cols = st.columns(len(example_symbols))
        
        for i, sym in enumerate(example_symbols):
            with cols[i]:
                if st.button(sym, key=f"example_{sym}"):
                    st.rerun()

if __name__ == "__main__":
    main()
