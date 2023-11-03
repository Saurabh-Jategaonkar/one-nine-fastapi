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

@app.post("/install2")
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
        os.makedirs(output_folder, exist_ok=True)
        
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

@app.post("/install")
async def install(assistant: Assistant):
    result = {
        "bot_name": assistant.bot_name,
        "org_name": assistant.org_name,
        "description": assistant.description,
        "lp_text": assistant.lp_text,
        "model_name": assistant.model_name
    }
    # print(result)
    model_details = {
        "install_path": f"installed_models/{result['bot_name']}/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    }

    if result['model_name'] == 'mistral':
        model_url = """https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"""
        
        # sub_url = """https://cdn-lfs.huggingface.co/repos/46/12/46124cd8d4788fd8e0879883abfc473f247664b987955cc98a08658f7df6b826/14466f9d658bf4a79f96c3f3f22759707c291cac4e62fea625e80c7d32169991?response-content-disposition=attachment%3B+filename*%3DUTF-8%27%27mistral-7b-instruct-v0.1.Q4_K_M.gguf%3B+filename%3D%22mistral-7b-instruct-v0.1.Q4_K_M.gguf%22%3B&Expires=1699224602&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTY5OTIyNDYwMn19LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2RuLWxmcy5odWdnaW5nZmFjZS5jby9yZXBvcy80Ni8xMi80NjEyNGNkOGQ0Nzg4ZmQ4ZTA4Nzk4ODNhYmZjNDczZjI0NzY2NGI5ODc5NTVjYzk4YTA4NjU4ZjdkZjZiODI2LzE0NDY2ZjlkNjU4YmY0YTc5Zjk2YzNmM2YyMjc1OTcwN2MyOTFjYWM0ZTYyZmVhNjI1ZTgwYzdkMzIxNjk5OTE%7EcmVzcG9uc2UtY29udGVudC1kaXNwb3NpdGlvbj0qIn1dfQ__&Signature=biPUUjzhlWyV4QsOnOELpmuEQbz0yn-FSI7i98uLd5f4QWFOk0SckRX7voqPjkWAb7GdUJ29yWFR5h15qC0ez4l-EpEo96ZLQEQ4yHY5gaH7XttUI0EUzjgmWk60nvl5Qi%7EKPrnFFVVEzjWIGFlLJ9BsZuNmb%7E6MxBtXgocE4CLOBbzHsVgMGpHe5xByFYOvvHDc7qC2-rcMT2riHjPcA-XTydx63PqfaL2WjB%7Ec3LBqVWwq%7EXMOOyT%7EL4j-al2jucgbSGXbuj1d3OIZE7QYhTiibL8w2fYE4TiVOpVQUTUp-QEBfSLq0fuZ7Po2bWQuKy%7EizMdSKznAw8JdtPYEoA__&Key-Pair-Id=KVTP0A1DKRTAX"""
        try:
            subprocess.run(f"cd installed_models && mkdir {result['bot_name']}", shell=True, check=True)

            directory_path = f"installed_models/{result['bot_name']}"
            result['subprocess'] = subprocess.run(f'cd {directory_path} && wget {model_url}', shell=True, check=True)

            if (result['subprocess']) == 0:
                result['bot_path'] = model_details['install_path']
                result['is_downloaded'] = True
            else:
                result['bot_path'] = 'No Path. Download failed.'
                result['is_downloaded'] = False
                return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return {'message': f'Error while downloading the model: {e}'}
    
    else:
        return {'message': 'Please select a model.'}

    return result