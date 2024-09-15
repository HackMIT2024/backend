from dotenv import load_dotenv
import os
import base64


load_dotenv()

class ImageToText:
    def __init__(self, imagePath):
        #convert to url 
        with open(imagePath, "rb") as image_file:
            self.imageEncoded = base64.b64encode(image_file.read()).decode('utf-8')

    async def convert_image_to_text(self):
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
                                "url": f"data:image/jpeg;base64,{self.imageEncoded}",
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