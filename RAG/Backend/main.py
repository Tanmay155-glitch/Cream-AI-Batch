from fastapi import FastAPI
from pydantic import BaseModel

from backend import addData, getData, askQuestion

app = FastAPI(title="RAG Application")

class DocumentInput(BaseModel):
    documents: list[str]

class ChatInput(BaseModel):
    prompt: str


@app.get("/")
def home():
    return "Welcome to RAG Application!"


@app.post("/collection")
def storeData(data: DocumentInput):
    addData(data.documents)
    return {"message": "Documents stored successfully!"}


@app.get("/collection")
def getCollectionData():
    return getData()


@app.post("/chat")
def getResponse(query: ChatInput):
    response = askQuestion(query.prompt)
    return {"response": response}