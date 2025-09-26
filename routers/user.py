from fastapi import APIRouter, HTTPException
import logging

from database import user_table, database
from models.user import UserIn
from security import get_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", status_code=200)
async def register(user: UserIn):
	if await get_user(user.email):
		raise HTTPException(status_code=400, detail="Email already registered")
	# Use email as username to satisfy NOT NULL constraint
	query = user_table.insert().values(email=user.email, username=user.email)
	last_record_id = await database.execute(query)
	
	logger.debug(f"User registered with ID: {last_record_id}")
	return {"detail": "User registered successfully", "user_id": last_record_id}