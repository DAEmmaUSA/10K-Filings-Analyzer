import streamlit as st
import asyncio
from load_agent import load_agents
from tools import create_tools
from ingest import create_DB
from downloader import download
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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

# def run_async(coroutine):
#     # Create a new event loop
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     result = loop.run_until_complete(coroutine)
#     loop.close()
#     return result

def main():
    st.title("Financial Document Analyzer")

    # User input for the company symbol
    symbol = st.text_input("Enter the company symbol (e.g., AAPL):")

    queries = {
    "Overview": f"""
Based on the comprehensive review of the latest 10-K filing of {symbol}, identify and analyze three positive and three negative aspects regarding the company's prospects. Organize your analysis in the following format:

1. **Positive Insights**:
   - **Strengths and Opportunities**: Detail three major strengths or opportunities that {symbol} is poised to capitalize on.
   - **Potential Positive Outcomes**: Discuss the possible beneficial outcomes if these strengths and opportunities are effectively leveraged.

2. **Negative Insights**:
   - **Challenges and Threats**: Enumerate three significant challenges or threats facing {symbol}.
   - **Potential Negative Consequences**: Explore the potential adverse impacts these challenges could have on {symbol}'s future performance.
    """
    ,
    "Business and Risk": f"""
Using the combined information from Item 1 (Business Overview), Item 1A (Risk Factors), Item 7 (Management’s Discussion and Analysis), Item 7A (Quantitative and Qualitative Disclosures About Market Risk), and Item 8 (Financial Statements) from the latest 10-K filing of {{symbol}}, perform a detailed analysis to provide:

1. **Business and Financial Overview**:
   - **Core Business Operations**: Summarize the main activities and market positions outlined in Item 1.
   - **Financial Health**: From Item 8, highlight key financial metrics and year-over-year changes.
   - **Management Analysis**: Extract key insights from Item 7 about financial trends, operational challenges, and management's strategic focus.

2. **Integrated Risk Profile**:
   - **Risk Landscape**: Using information from Item 1A and Item 7A, identify and describe the major operational and market risks.
   - **Impact and Mitigation**: Discuss the potential impacts of these risks on the business and financial performance, and outline the risk mitigation strategies provided by management across these sections.

Provide this analysis in a structured format, aiming to offer stakeholders a clear and concise overview of both opportunities and threats, as well as the company’s preparedness to handle its market and operational challenges.
"""
    ,
    "Strategic Outlook and Future Projections": f"""
With reference to the information available in Item 1 (Business Overview), Item 1A (Risk Factors), Item 7 (Management’s Discussion and Analysis), Item 7A (Quantitative and Qualitative Disclosures About Market Risk), and Item 8 (Financial Statements) of {{symbol}}'s recent 10-K filing, synthesize a strategic report that addresses:

1. **Strategic Positioning and Opportunities**:
   - **Market Dynamics**: Analyze the business landscape as described in Item 1 and Item 7, focusing on competitive positioning and market opportunities.
   - **Operational Strengths**: Highlight operational strengths and efficiencies that bolster the company's market position.

2. **Future Financial Prospects**:
   - **Financial Projections**: Discuss future financial prospects based on trends and data from Item 7 and Item 8.
   - **Risk and Opportunities Balance**: Weigh the financial risks (Item 1A and 7A) against potential opportunities, and discuss how the company plans to leverage its strengths to mitigate these risks and capitalize on market trends.

This analysis should offer a forward-looking perspective, aiming to provide potential investors and company stakeholders with a deep understanding of the company’s strategic initiatives, market risks, and financial outlook.
"""
}
    if st.button("Fetch and Analyze"):
        # Load data
        if symbol not in agents:
            download(symbol)
            create_DB(symbol)
        agent = load_tools(symbol)
        responses = {}
        # Run queries and store responses
        for key, query in queries.items():
            if key not in st.session_state or st.session_state.query != query:
                response = run_agent_query(agent, query)
                st.session_state[key] = response
                st.session_state.query = query
            responses[key] = st.session_state[key]

        # Display insights from the agent
        for key, response in responses.items():
            st.write(f"Analysis for **{key}** from recent 10-K filing of **{symbol}**:")
            st.write(response['output'])

if __name__ == "__main__":
    main()
