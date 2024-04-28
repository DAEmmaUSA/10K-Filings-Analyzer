import streamlit as st
import asyncio
from load_agent import load_agents
from tools import create_tools
from ingest import create_DB
from downloader import download
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Initialize environment and tools
from dotenv import load_dotenv
load_dotenv()

agents = {}

def load_tools(symbol):
    if symbol not in agents:  # Load agent if not already loaded
        tools = create_tools(symbol)
        agents[symbol] = load_agents(tools)
    return agents[symbol]

# Function to handle asynchronous agent invocation
def run_agent_query(agent, query):
    return agent.invoke(query)

def main():
    st.title("Financial Document Analyzer")

    # User input for the company symbol
    symbol = st.text_input("Enter the company symbol (e.g., AAPL):")

    if st.button("Fetch and Analyze"):
        # Load data
        if symbol not in agents:
            download(symbol)
            create_DB(symbol)
        agent = load_tools(symbol)

        # Example query to LangChain agent
        query = f"""
You are given the Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations from recent 10-K filing of {symbol}.
Provide the analysis in the following format:
1. **Key Risks**:
   - List and describe the biggest risks to {symbol} as identified in the filing.
   - Discuss any new risks that have emerged compared to the previous year.
   - Highlight any industry-specific risks if applicable.
2. **Impact of Risks**:
   - Explain how each identified risk could potentially impact {symbol}'s financial health and operational effectiveness.
3. **Management's Risk Mitigation Strategies**:
   - Summarize the strategies and measures management has discussed to mitigate these risks.
"""
        if 'response' not in st.session_state or st.session_state.query != query:
            # Run agent query and store result in session state
            st.session_state.response = run_agent_query(agent, query)
            st.session_state.query = query

        # Display insights from the agent
        st.write("LangChain LLM Analysis:")
        st.write(st.session_state.response['output'])

if __name__ == "__main__":
    main()
