from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException,Form
from sqlalchemy.orm import Session
from auth.auth_bearer import JWTBearer, get_admin, get_current_user
from database import get_db, api_response
from ..models.user import DataBuddY
from ..schemas import LoginInput, ChangePassword, UserCreate, UpdateUser, UserType
import bcrypt
from .Email_config import send_email
import random
import pytz


router = APIRouter()

user_ops = DataBuddY()


def generate_token(data):
    exp = datetime.utcnow() + timedelta(days=1)
    token_payload = {'user_id': data['emp_id'], 'exp': exp}
    token = jwt.encode(token_payload, 'cat_walking_on_the street', algorithm='HS256')
    return token, exp


@router.post('/DataBuddYs/login/')
async def DataBuddYs(credential: LoginInput):
    try:
        response = user_ops.DataBuddYs_login(credential)
        return response
    except HTTPException as e:
        raise
    except Exception as e:
        return HTTPException(status_code=500, detail=f"login failed: {str(e)}")


@router.post("/insert/DataBuddY_register/")
def DataBuddY_register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        if not DataBuddY.validate_email(data.user_email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        if not DataBuddY.validate_password(data.user_password):
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        if not DataBuddY.validate_phone_number(data.phone_no):
            raise HTTPException(status_code=400, detail="phone number must be 10 digit")

        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        hashed_password = bcrypt.hashpw(data.user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        usr = DataBuddY(
            user_name=data.user_name,
            user_email=data.user_email,
            user_password=hashed_password,
            user_type=data.user_type, 
            phone_no=data.phone_no,
            created_on=ist_now,
            updated_on=ist_now
        )
        db.add(usr)
        db.commit()

        response = api_response(200, message="User Created successfully")
        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=f"{e}")


@router.get("/get_my_profile")
def get_current_user_details(current_user: DataBuddY = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_details = {
            # "user_id": current_user.user_id,
            "username": current_user.user_name,
            "email": current_user.user_email,
            "user_type": current_user.user_type,
            "phone_no" : current_user.phone_no,

        }
        return api_response(data=user_details, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



#######################################################################################

@staticmethod
def validate_password(password):
        return len(password) >= 8


@router.put("/change_password/{user_id}")
async def change_password(current_password: str, new_password: str, confirm_new_password: str, current_user: DataBuddY = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if new_password != confirm_new_password:
            raise HTTPException(status_code=400, detail="New passwords do not match")

        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {current_user.user_id} not found")

        if not bcrypt.checkpw(current_password.encode('utf-8'), user.user_password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Wrong current password")

        if not user_ops.validate_password(new_password):
            raise HTTPException(status_code=400, detail="Invalid new password")
        
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.user_password = hashed_new_password

        db.commit()
        contact = "900-417-3181"
        email_contact = "vinay@example.com"

        reset_email_body = f"""
        <p>Dear User,</p>
        <p>Your password has been successfully changed.</p>
        <p>If you did not request this change, please contact support at {contact} or email us at {email_contact}.</p>
        <p>Thank you!</p>
        <br><br>
        <p>Best regards,</p>
        <p>Vinay Kumar</p>
        <p>MaitriAI</p>
        <p>900417181</p>
        """
        await send_email(
            subject="Password Change Confirmation",
            email_to=user.user_email,
            body=reset_email_body
        )
        return {"message": "Password changed successfully"}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



