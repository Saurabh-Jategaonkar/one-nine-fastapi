import json
import os
from typing import Literal, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException
import random
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

import requests
from datetime import datetime
from ctransformers import AutoModelForCausalLM, AutoConfig, Config

class Assistant(BaseModel):
    bot_name: str
    org_name: str
    description: str
    lp_text: str
    model_name: str
    password: str

class Prompt(BaseModel):
    prompt: str
    password: str

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
        "model_name": assistant.model_name,
        "password": assistant.password
    }
    print(result)
    if result['password'] == 'onenine_2349bjd':
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
                print(f"Model downloaded successfully.")
                result['is_downloaded'] = f"Model {output_file} downloaded successfully."
                result['bot_path'] = output_folder + "/mistral_model.gguf"
            else:
                print(f"Failed to download file.")
                result['is_downloaded'] = f"Failed to download file. Status code: {response.status_code}"
                result['bot_path'] = None
        else:
            return {'message': 'Please select a valid model.'}
    else:
        return {'message': 'Not authorized. Re-check the password.'}
    return result

@app.post("/prompt")
async def prompt(promptInput: Prompt):
    conf = AutoConfig(Config(temperature=0.8, repetition_penalty=1.1,
                            batch_size=52, max_new_tokens=1024,
                            context_length=2048))
    llm = AutoModelForCausalLM.from_pretrained("installed_models/testbot_20231107190105/mistral_model.gguf",
            model_type="mistral", config = conf)

    while(promptInput.prompt!="exit"):
        input_prompt = promptInput.prompt
        mistral_prompt = f"<s>[INST] {input_prompt} [/INST]"
        answer = llm(mistral_prompt, temperature = 0.7,
                repetition_penalty = 1.15,
                max_new_tokens = 2048)
        return {'message': answer}
