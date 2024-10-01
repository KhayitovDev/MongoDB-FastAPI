from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
from typing import List, Optional
import asyncio

# Pydantic model for the response
class DataModel(BaseModel):
    id: str  # Use a string for ObjectId
    first_name: str
    last_name: str
    age: Optional[int] = None  # Optional field
    email: str
    gender: str
    phone: str
    invest_id: str

MONGO_DETAILS = "mongodb://localhost:27017"

DATABASE_NAME = "Phone"
SOURCE_COLLECTION = "phones"

DESTINATION_DATABASE = "Inserted-Phones"
DESTINATION_COLLECTION = "numbers"

app = FastAPI()

client = AsyncIOMotorClient(MONGO_DETAILS)
database_one = client[DATABASE_NAME]
database_two = client[DESTINATION_DATABASE]
source_collection = database_one[SOURCE_COLLECTION]
destination_collection = database_two[DESTINATION_COLLECTION]

async def fetch_data(phone_numbers: List[str]):
    """Fetch data based on phone numbers."""
    existing_numbers = await source_collection.find({"phone": {"$in": phone_numbers}}).to_list(length=None)
    return existing_numbers

async def process_and_insert_data(phone_numbers: List[str], invest_id: str):
    """Process fetched data and insert it into the destination collection."""
    documents = await fetch_data(phone_numbers)

    for document in documents:
        phone_number = document['phone']
        
        # Check if the phone number already exists in the destination collection
        exists_in_destination = await destination_collection.find_one({"phone": phone_number})

        if not exists_in_destination:
            document["invest_id"] = invest_id
            #document["id"] = str(document.pop("_id"))  # Convert ObjectId to string and rename
            await destination_collection.insert_one(document)

    return {"message": "Data moved successfully."}

@app.get("/investigation/{invest_id}/numbers", response_model=List[DataModel])
async def get_numbers_by_invest_id(invest_id: str):
    """Retrieve all information associated with a specific investigation ID."""
    documents = await destination_collection.find({"invest_id": invest_id}).to_list(length=None)
    print(documents)

    if not documents:
        raise HTTPException(status_code=404, detail="No records found for this investigation ID.")

    # Create a list of DataModel objects from the documents
    investigation_data = []
    for doc in documents:
        # Create DataModel instance with explicit field assignments
        data_entry = DataModel(
            # Convert ObjectId to string
            first_name=doc.get('first_name', ''),  # Use get to provide a default value
            last_name=doc.get('last_name', ''),
            age=doc.get('age', None),  # Optional fields can default to None
            email=doc.get('email', ''),
            gender=doc.get('gender', ''),
            phone=doc.get('phone', ''),
            invest_id=doc.get('invest_id', '')
        )
        investigation_data.append(data_entry)

    return investigation_data


# For direct function usage outside of FastAPI
if __name__ == "__main__":
    import asyncio

    # Replace this with your actual phone numbers
    phone_numbers = ["+63 442 493 4432"]
    
    # Run the fetch_data function
    asyncio.run(fetch_data(phone_numbers))
