from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from pydantic import BaseModel
from typing import Optional
import shutil
from pathlib import Path
from ImageToText import ImageToText
from helper import eventDesciptor, getUpdatedHealthDataMsg
import uuid
from pymongo import MongoClient
from bson import ObjectId
import httpx
import json
from uagents import Model
from uagents.envelope import Envelope
from uagents.query import query
from starlette.testclient import TestClient

AGENT_ADDRESS = "agent1qt6ehs6kqdgtrsduuzslqnrzwkrcn3z0cfvwsdj22s27kvatrxu8sy3vag0"


class TestRequest(Model):
    message: str


async def agent_query(req):
    response = await query(destination=AGENT_ADDRESS, message=req, timeout=15)
    if isinstance(response, Envelope):
        data = json.loads(response.decode_payload())
        return data["text"]
    return response

app = FastAPI()


internalRequestClient = TestClient(app)

# MongoDB connection setup
client = MongoClient("mongodb+srv://jesicahackmit:jesica@cluster01.ik8tfsj.mongodb.net/?retryWrites=true&w=majority")
db = client["quicksafe"]
collection = db["emergencyData"]

class UserData(BaseModel):
    id: str
    eventDescription: str
    healthData: str
    location: str
    userPhone: str

    def to_dict(self):
        return {
            "id": self.id,
            "eventDescription": self.eventDescription,
            "healthData": self.healthData,
            "location": self.location,
            "userPhone": self.userPhone
        }

@app.post("/emergency")
async def emergency_endpoint(
    image: Optional[UploadFile] = File(None),
    audio: str = Form(...),
    healthData: str = Form(...),
    location: str = Form(...),
    userPhone: str = Form(...)
):
    
    print ("audio: ", audio)
    print ("healthData: ", healthData)
    print ("location: ", location)
    print ("userPhone: ", userPhone)
    print ("image: ", image.filename)
    if image is not None:
        # Save the image to the /tmp directory and get the path of the image
        tmp_dir = Path("/tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)  # Ensure the /tmp directory exists
        
        # Save the uploaded image to the /tmp directory with its original filename
        image_path = tmp_dir / image.filename
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Pass the image path to the ImageToText object
        imgToTextObj = ImageToText(str(image_path))  # Convert Path to string
        image_text = await imgToTextObj.convert_image_to_text()

        # Call the eventDescriptor function
        eventDescription = eventDesciptor(audio, healthData, location, userPhone, image_text)
        
        #send message to emergency services via the /sendMsgToAgent route
        internalRequestClient.post("/sendMsgToAgent", json={"message": eventDescription})
        
        # Create the Pydantic class and save it to MongoDB
        incidentId = str(uuid.uuid4())
        user_data = UserData(
            id=incidentId,
            eventDescription=eventDescription,
            healthData=healthData,
            location=location,
            userPhone=userPhone
        )
        collection.insert_one(user_data.to_dict())
        
    return {"id": incidentId}

@app.post("/healthdata/{id}")
async def get_healthdata(id: str, updatedHealthData: str = Form(...), updatedLocation: str = Form(...)):
    previousHealthData = collection.find_one({"id": id})["healthData"]
    previousLocation = collection.find_one({"id": id})["location"]
    collection.update_one({"id": id}, {"$set": {"healthData": updatedHealthData}})
    collection.update_one({"id": id}, {"$set": {"location": updatedLocation}})
    #get event description for the id
    eventDescription = collection.find_one({"id": id})["eventDescription"]
    updatedHealthDataMsg = getUpdatedHealthDataMsg(eventDescription, previousHealthData, updatedHealthData, previousLocation, updatedLocation)
    print("updatedHealthDataMsg!!!: ", updatedHealthDataMsg)
    if updatedHealthDataMsg.lower() != "no change":
        print("Sent Updated Message")
        internalRequestClient.post("/sendMsgToAgent", json={"message": updatedHealthDataMsg})
    else:
        print("Did not send message")
    return {"message": "Health Data Updated Successfully"}


@app.post("/sendMsgToAgent")
async def make_agent_call(req: Request):
    model = TestRequest.parse_obj(await req.json())
    try:
        res = await agent_query(model)
        return f"successful call - agent response: {res}"
    except Exception:
        return "unsuccessful agent call"