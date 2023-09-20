import chromadb
import os
import openai
from fastapi import FastAPI, Form, Request, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import List, Dict, Union
from fastapi.staticfiles import StaticFiles




client = chromadb.PersistentClient(path=os.path.join(os.getcwd(), '..', 'chroma'))
#collection = client.get_collection(name="AthleanXTranscripts")
#client.list_collections()


app = FastAPI()
app.mount("/static", StaticFiles(directory="templates/static"), name="static")
templates = Jinja2Templates(directory="templates")

api_key_storage = {}  # Temporary storage for the API key. In a real-world scenario, consider using sessions or secure cookies.
collection= {}

def get_api_key():
    return api_key_storage.get("api_key", None)

def get_collection(expert: str = Form(...)):
    # Determine the collection based on the chosen expert
    if expert == "Andrew Huberman":
        collection = client.get_collection(name="HubermanTranscripts")
    elif expert == "Athlean-X":
        collection = client.get_collection(name="AthleanXTranscripts")
    elif expert == "Peter Attia":
        collection = client.get_collection(name="PeterAttiaTranscripts")
    elif expert == "Lex Fridman":
        collection = client.get_collection(name="LexFridmanTranscripts")
    elif expert == "Kurzgesagt":
        collection = client.get_collection(name="kurzgesagtTranscripts")
    elif expert == "AI Explained":
        collection = client.get_collection(name="AIExplainedTranscripts")
    else:
        raise ValueError(f"Unknown expert: {expert}")

    return collection

@app.post("/set_api_key/")
def set_api_key(request: Request, api_key: str = Form(...)):
    api_key_storage["api_key"] = api_key
    return RedirectResponse(url="/choose_expert", status_code=303)

@app.get("/choose_expert/")
def choose_expert_page(request: Request):
    return templates.TemplateResponse("choose_expert.html", {"request": request})

@app.post("/set_expert/")
def set_expert(request: Request, expert: str = Form(...)):
    # Determine the collection based on the chosen expert
    # Now, you can use the 'collection' variable to interact with your vector database
    # For example, if you're using a database client, you might do something like:
    # db_client.get_collection(collection).find(...)
    print(f"Received expert: {expert}")
    # For this example, we'll just return the chosen collection name
    return RedirectResponse(url=f"/chatbot/{expert}", status_code=303)


@app.get("/chatbot/{expert}")
def chatbot_page(request: Request, expert: str):
    return templates.TemplateResponse("chatbot.html", {"request": request, "expert": expert})

@app.post("/chatbot/{expert}/send_message")
def send_message(expert: str, body: Dict[str, Union[str, List[Dict[str, str]]]], api_key: str = Depends(get_api_key)):
    # For this example, I'm assuming `vector_results` is a string you have defined elsewhere.
    # You might need to adjust this part based on your actual implementation.
    user_message = body['user_message']
    conversation = body['conversation']
    print('conversation')
    print(conversation)
    collection = get_collection(expert)
    print(collection)
    vector_results=collection.query(
    query_texts=[user_message],
    n_results=10
)
    print(vector_results)
    openai.api_key=api_key
    MODEL_LLM='gpt-3.5-turbo-16k'
    completion = openai.ChatCompletion.create(
        model=MODEL_LLM,
        messages=[
            {"role": "system", "content": "You are a helpful assistant and are tasked with answering questions about a specific youtube channel. You will be given extracts from the transcripts of the videos in that channel and should only answer from those extracts. If you don't know, just say you don't know. You will write a concise paragraph answering the user question, and then another paragraph citing the titles of the videos of the cited extracts and start time. You have to convert the start time to minutes and seconds or hours minutes and seconds. Only put the converted start time. Do not forget to write the paragraph citing sources and where the user can find some of the information you summarized."},
            {"role": "user", "content": f"Here is the vector search information retrieved: {vector_results} Here is the user question: {user_message}. Here is the previous conversation history: {conversation}"},
        ],
        temperature=0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    chatbot_response = completion.choices[0].message['content']
    print(chatbot_response)
    return {"response": chatbot_response, "body": body}


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
