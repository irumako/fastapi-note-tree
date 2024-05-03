import motor.motor_asyncio

from .config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(str(settings.MONGODB_URL))
db = client.note
collection = db.get_collection("notes")
