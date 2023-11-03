import json
import os
from typing import Literal, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException
import random
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from mangum import Mangum

import subprocess
import requests

class Book(BaseModel):
    name: str
    genre: Literal["fiction", "non-fiction"]
    price: float
    book_id: Optional[str] = uuid4().hex

class Assistant(BaseModel):
    bot_name: str
    org_name: str
    description: str
    lp_text: str
    model_name: str

BOOKS_FILE = "books.json"
BOOKS = []

if os.path.exists(BOOKS_FILE):
    with open(BOOKS_FILE, "r") as f:
        BOOKS = json.load(f)

app = FastAPI()
handler = Mangum(app)


@app.get("/")
async def root():
    return {"message": "Welcome to my bookstore app!"}


@app.get("/random-book")
async def random_book():
    return random.choice(BOOKS)

@app.get("/list-books")
async def list_books():
    return {"books": BOOKS}

@app.get("/book_by_index/{index}")
async def book_by_index(index: int):
    if index < len(BOOKS):
        return BOOKS[index]
    else:
        raise HTTPException(404, f"Book index {index} out of range ({len(BOOKS)}).")

@app.post("/add-book")
async def add_book(book: Book):
    book.book_id = uuid4().hex
    json_book = jsonable_encoder(book)
    BOOKS.append(json_book)

    with open(BOOKS_FILE, "w") as f:
        json.dump(BOOKS, f)

    return {"book_id": book.book_id}

@app.get("/get-book")
async def get_book(book_id: str):
    for book in BOOKS:
        if book.book_id == book_id:
            return book

    raise HTTPException(404, f"Book ID {book_id} not found in database.")

@app.post("/install")
async def install(assistant: Assistant):
    result = {
        "bot_name": assistant.bot_name,
        "org_name": assistant.org_name,
        "description": assistant.description,
        "lp_text": assistant.lp_text,
        "model_name": assistant.model_name
    }
    print(result)

    if result['model_name'] == 'mistral':
        url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
        output_folder = f"installed_models/{result['bot_name']}"
        output_file = os.path.join(output_folder, "mistral_model.gguf")
        os.makedirs(output_folder, exist_ok=False)
        
        response = requests.get(url)

        if response.status_code == 200:
            with open(output_file, 'wb') as file:
                file.write(response.content)
            print(f"File {output_file} downloaded successfully.")
            result['is_downloaded'] = f"File {output_file} downloaded successfully."
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            result['is_downloaded'] = f"Failed to download file. Status code: {response.status_code}"
    else:
        return {'message': 'Please select a valid model.'}
    return result