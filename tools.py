from constants import SOURCE_DIRECTORY, PERSIST_DIRECTORY
import os
from langchain.chains import RetrievalQA
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.agents import Tool
from langchain.prompts import PromptTemplate

'''
Prompt template is defined here
'''
prompt_template = """
Your name is Bob and you are a human not an AI assistant.
These are Management's Discussion and Analysis of Financial Condition and Results of Operations section of SEC 10-K annual filings by companies.
Sometimes referred as 10-K SEC filings.
Use the following Management's Discussion and Analysis of Financial Condition and Results of Operations sections of 10-K filings from various company filings to answer the question at the end.

{context}

Question: {question}
Helpful Answer:"""



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
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    # creating a tools list to be appended 
    tools=[]
    
    # defining the embeddings
    embeddings = CohereEmbeddings()
    
    # iterating through each file for retrieval
    db=Chroma(persist_directory=f"{PERSIST_DIRECTORY}/{symbol}/item_7", embedding_function=embeddings)
    retrievers=db.as_retriever()
    
    # appending tools for each retrieval
    tools.append(
            Tool(
                args_schema=DocumentInput,
                name="Financial_Analysis",
                description=f"useful when you want to answer questions about a document",
                func=RetrievalQA.from_chain_type(llm=llm, retriever=retrievers, chain_type_kwargs=chain_type_kwargs),
            )
        )

    return tools