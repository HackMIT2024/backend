#1. convert image into text
#3. Get first message that needs to be sent to the emer services
#4. based on what the emer services need, go back and forth to the llm to get nextResponses using fetch ai agent


from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
import twilio
from twilio.rest import Client
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

async def convert_image_to_text(imageUrl: str):
    import json
    import requests

    stream = False
    url = "https://proxy.tune.app/chat/completions"
    headers = {
        "Authorization": os.getenv("GROQ_MULTIMODAL"),
        "Content-Type": "application/json",
    }
    data = {
    "temperature": 0.8,
        "messages":  [
    {
        "role": "system",
        "content": "Describe this emergency situation image.",
        "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": imageUrl,
                        },
                    },
                ],
    }
    ],
        "model": "nikhildhoka8/groq-multimodal",
        "stream": stream,
        "frequency_penalty":  0,
        "max_tokens": 900
    }
    response = requests.post(url, headers=headers, json=data)
    if stream:
        for line in response.iter_lines():
            if line:
                l = line[6:]
                if l != b'[DONE]':
                    print(json.loads(l))
    else:
        print(response.json()["choices"][0]["message"]["content"])

    return response.json()["choices"][0]["message"]["content"]
  

# Main FastAPI Endpoint
@app.post("/emergency")
async def emergency_endpoint(
    imageUrl: str = Form(...),
    audio: str = Form (...),
    healthData: str = Form(...),
    location: str = Form(...),
    userPhone: str = Form(...)
):
    # Your function logic here
    # if image is uploaded, convert to text
    if imageUrl is not None:
        image_text = await convert_image_to_text(imageUrl)
        print(f"Image Text: {image_text}")
    # get first response from llm
    
    return {"status": "Emergency services contacted"}