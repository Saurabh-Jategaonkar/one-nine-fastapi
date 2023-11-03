import json
import os
from typing import Literal, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException
import random
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from mangum import Mangum

import requests
from datetime import datetime


class Assistant(BaseModel):
    bot_name: str
    org_name: str
    description: str
    lp_text: str
    model_name: str

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to OneNine!"}

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
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_folder = f"installed_models/{result['bot_name']}_{timestamp}"
        output_file = os.path.join(output_folder, "mistral_model.gguf")

        os.makedirs(output_folder, exist_ok=False)
        
        response = requests.get(url)

        if response.status_code == 200:
            with open(output_file, 'wb') as file:
                file.write(response.content)
            print(f"File {output_file} downloaded successfully.")
            result['is_downloaded'] = f"File {output_file} downloaded successfully."
            result['bot_path'] = output_folder + "/mistral_model.gguf"
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            result['is_downloaded'] = f"Failed to download file. Status code: {response.status_code}"
            result['bot_path'] = None
    else:
        return {'message': 'Please select a valid model.'}
    return result