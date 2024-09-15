from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import shutil
from pathlib import Path
from ImageToText import ImageToText
from helper import eventDesciptor, sendEmergencyMsg, getUpdatedHealthDataMsg
import uuid
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

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
        
        #send message to emergency services
        sendEmergencyMsg(eventDescription)
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
        sendEmergencyMsg(updatedHealthDataMsg)
    else:
        print("Did not send message")
    return {"message": "Health Data Updated Successfully"}
