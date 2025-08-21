from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("realistic_restaurant_reviews.csv") # add our documents .csv files
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest") # define embedding modell

db_location = "./chrome_langchain_db"
add_documents = not os.path.exists(db_location) # check if db exists
# prepare data and convert to documents
if add_documents:
    documents = []
    ids = []
    # Choose what data to use from the document
    for i, row in df.iterrows():
        document = Document(
            page_content=row["Title"] + " " + row["Review"],
            metadata={"rating": row["Rating"], "date": row["Date"]},
            id=str(i)
        )
        ids.append(str(i))
        documents.append(document)
# if documents are loaded- initialize vectore_store
vector_store = Chroma(
    collection_name="restaurant_reviews",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)
# retriever lets us look up documents and lets us add these documents to our prompt
retriever = vector_store.as_retriever(
    search_kwargs={"k": 5} # number of reviews passed in the prompt
)

