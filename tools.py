from constants import SOURCE_DIRECTORY, PERSIST_DIRECTORY
import os
from langchain.chains import RetrievalQA
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
# from langchain_cohere import CohereEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.agents import Tool
from langchain.prompts import PromptTemplate

'''
Prompt template is defined here
'''
prompt_template = """
Hello, your name is Bob. You are a financial analyst with expertise in reviewing and interpreting SEC 10-K annual filings.
You have the following sections available for analysis: Item 1 (Business Overview), Item 1A (Risk Factors), Item 7 (Management’s Discussion and Analysis of Financial Condition and Results of Operations),
Item 7A (Quantitative and Qualitative Disclosures About Market Risk), and Item 8 (Financial Statements and Supplementary Data).
Please provide financial insight based on the context provided below:

{context}

Question: {question}
Helpful Answer:
"""

'''
We use the user defined prompt template and pass it to the chain type kwargs
'''
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
chain_type_kwargs = {"prompt": PROMPT}

'''
Defining a user defined class for the Document comparison agent
'''
class DocumentInput(BaseModel):
    question: str = Field()


'''
A function which does retreval and create tools for each retriever 
using Langchain
'''
def create_tools(symbol):
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
    # creating a tools list to be appended 
    tools = []
    
    # defining the embeddings
    embeddings = OpenAIEmbeddings()
    
    # iterating through each file for retrieval
    db = Chroma(persist_directory=f"{PERSIST_DIRECTORY}/{symbol}/item_7", embedding_function=embeddings)
    retrievers = db.as_retriever()
    
    # appending tools for each retrieval
    tools.append(
            Tool(
                args_schema = DocumentInput,
                name = "Financial_Analysis",
                description = f"useful when you want to answer questions about a document",
                func = RetrievalQA.from_chain_type(llm=llm, retriever=retrievers, chain_type_kwargs=chain_type_kwargs),
            )
        )

    return tools