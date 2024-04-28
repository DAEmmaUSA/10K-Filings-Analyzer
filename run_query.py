from load_agent import load_agents
from tools import create_tools
from dotenv import load_dotenv
import langchain_visualizer

load_dotenv()
tools = create_tools()
agent = load_agents(tools)
async def search_agent_demo():
    # query = input("\nEnter a query: ")
    # What do you see as the biggest risk to the company?
    return agent.invoke("What do you see as the biggest risk to the company?")


langchain_visualizer.visualize(search_agent_demo)