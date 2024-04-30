# 10K fillings llm analysis

This repository uses OpenAI embeddings and llm models 

## TO INSTALL ALL THE NECESSARY DEPENDENCIES
```pip install -r requirements.txt```

## TO GET NECESSARY 10K FILINGS FROM THE SEC EDGAR:
```python downloader.py```

## TO INGEST INTO THE DATABASE:
```python ingest.py```

## TO ASK QUERIES ON THE DOCUMENTS(experimental purpose please use the streamlit frontend for the chatbot):
```python run_query.py```

## TO ASK QUERIES WITH A STREAMLIT FRONTEND:
```streamlit run frontend.py```