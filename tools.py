from constants import SOURCE_DIRECTORY, PERSIST_DIRECTORY
import os
from langchain.chains import RetrievalQA
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS  # ✅ use FAISS instead of Chroma
from langchain.agents import Tool
from langchain.prompts import PromptTemplate

# Prompt template
prompt_template = """
Hello, your name is Bob. You are a financial analyst with expertise in reviewing and interpreting SEC 10-K annual filings.
You have the following sections available for analysis: Item 1 (Business Overview), Item 1A (Risk Factors), Item 7 (Management’s Discussion and Analysis of Financial Condition and Results of Operations),
Item 7A (Quantitative and Qualitative Disclosures About Market Risk), and Item 8 (Financial Statements and Supplementary Data).
Please provide financial insight based on the context provided below:

{context}

Question: {question}
Helpful Answer:
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
chain_type_kwargs = {"prompt": PROMPT}

class DocumentInput(BaseModel):
    question: str = Field()

def create_tools(symbol):
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
    tools = []
    
    embeddings = OpenAIEmbeddings()
    
    # ✅ Load FAISS vector store instead of Chroma
    db = FAISS.load_local(
        folder_path=f"{PERSIST_DIRECTORY}/{symbol}/item_7",
        embeddings=embeddings
    )
    
    retriever = db.as_retriever()
    
    tools.append(
        Tool(
            args_schema=DocumentInput,
            name="Financial_Analysis",
            description="Useful when you want to answer questions about a document",
            func=RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type_kwargs=chain_type_kwargs),
        )
    )

    return tools
