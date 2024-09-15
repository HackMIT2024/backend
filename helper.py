import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def eventDesciptor(audioDescription: str, healthData: str, streetName: str, userPhone: str, imageDescription= None):
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
        "role": "user",
        "content": f"You are a specialist in describing this emergency service on behalf of the user so that this message can be forwarded to emergency responders. Based on the users data such as the image of their situation, their voice audio describing their situation, their health data, their location, and their phone number, generate a description on behalf of the user from the user's viewpoint.\n\n\nEmergency Image Description:\n{imageDescription}\n\nAudio Transcription:\n{audioDescription}\n\nLocation: \n{streetName}\n\nPhone Number: {userPhone}\n\nHealthData: \{healthData}\n\n\n"
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


def sendEmergencyMsg(message: str):
    from twilio.rest import Client

    # Your Account SID and Auth Token from Twilio Console
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    # Initialize the client
    client = Client(account_sid, auth_token)

    # Send SMS
    message = client.messages.create(
        body=message,  # The content of the SMS
        from_='+18777161342',  # Your Twilio number
        to='+16462296260'  # The recipient's phone number
    )
    sms_sid = message.sid
    print(f"Message sent with SID: {sms_sid}")




def getUpdatedHealthDataMsg(eventDescription: str, previousHealthData: str, updatedHealthData: str, previousLocation: str, updatedLocation: str):
    import json
    import requests

    stream = False
    url = "https://proxy.tune.app/chat/completions"
    headers = {
        "Authorization": "sk-tune-oWo6z7fh4BXVi3lgFdNqABen3ewrw6zrpt2",
        "Content-Type": "application/json",
    }
    data = {
    "temperature": 0.8,
        "messages":  [
    {
        "role": "user",
        "content": f"Here is the previous message that was sent to the emergency service, I want you to develop a new message that could be sent to the healthcare services based on the users updated health data. For example, if their location has changed, then indicate that in the new message that will be generated. Additionally, if there is a change in any of their health stats such as the heart beat, notify that as well. Please only highlight things that have changed and do not repeat the summary again.Respond in plain text in 2-3 lines of only stats or location that has changed. If there is no change, resopond with 'No change'\n\n\nEventDescription:\n{eventDescription}\n\n Previous Health Data:\n{previousHealthData}\n\n UpdatedHealth Data:\n{updatedHealthData}"
    }
    ],
        "model": "rohan/tune-gpt-4o",
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