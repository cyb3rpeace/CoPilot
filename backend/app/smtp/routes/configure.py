from fastapi import APIRouter, HTTPException, Security, security, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.smtp.schema.configure import SMTPResponse

from app.auth.utils import AuthHandler
from app.db.db_session import session
from app.auth.models.users import SMTP, SMTPInput, User
from app.auth.services.universal import select_all_users, find_user
from loguru import logger

smtp_router = APIRouter()
auth_handler = AuthHandler()

@smtp_router.post('/{user_id}/register', response_model=SMTPResponse, status_code=200, description='Register new SMTP for user')
async def register(user_id: int, smtp: SMTPInput):
    users = select_all_users()
    logger.info(users)
    if not any(x.id == user_id for x in users):
        raise HTTPException(status_code=400, detail='User not found')
    # Check if SMTP already exists for user
    smtp_found = session.query(SMTP).filter(SMTP.user_id == user_id).first()
    if smtp_found:
        raise HTTPException(status_code=400, detail='SMTP already exists for user')
    hashed_pwd = auth_handler.get_password_hash(smtp.smtp_password)
    u = SMTP(email=smtp.email, smtp_password=hashed_pwd, smtp_server=smtp.smtp_server, smtp_port=smtp.smtp_port, user_id=user_id)
    session.add(u)
    session.commit()
    return {"message": "SMTP created successfully", "success": True}

@smtp_router.get('/{user_id}', response_model=SMTP, status_code=200, description='Get SMTP for user')
async def get_smtp(user_id: int):
    users = select_all_users()
    if not any(x.id == user_id for x in users):
        raise HTTPException(status_code=400, detail='User not found')
    smtp_found = session.query(SMTP).filter(SMTP.user_id == user_id).first()
    if not smtp_found:
        raise HTTPException(status_code=400, detail='SMTP not found for user')
    return smtp_found

@smtp_router.put('/{user_id}', response_model=SMTPResponse, status_code=200, description='Update SMTP for user')
async def update_smtp(user_id: int, smtp: SMTPInput):
    users = select_all_users()
    if not any(x.id == user_id for x in users):
        raise HTTPException(status_code=400, detail='User not found')
    smtp_found = session.query(SMTP).filter(SMTP.user_id == user_id).first()
    if not smtp_found:
        raise HTTPException(status_code=400, detail='SMTP not found for user')
    smtp_found.email = smtp.email
    smtp_found.smtp_server = smtp.smtp_server
    smtp_found.smtp_port = smtp.smtp_port
    smtp_found.smtp_password = auth_handler.get_password_hash(smtp.smtp_password)
    session.commit()
    return {"message": "SMTP updated successfully", "success": True}

@smtp_router.delete('/{user_id}', response_model=SMTPResponse, status_code=200, description='Delete SMTP for user')
async def delete_smtp(user_id: int):
    users = select_all_users()
    if not any(x.id == user_id for x in users):
        raise HTTPException(status_code=400, detail='User not found')
    smtp_found = session.query(SMTP).filter(SMTP.user_id == user_id).first()
    if not smtp_found:
        raise HTTPException(status_code=400, detail='SMTP not found for user')
    session.delete(smtp_found)
    session.commit()
    return {"message": "SMTP deleted successfully", "success": True}
