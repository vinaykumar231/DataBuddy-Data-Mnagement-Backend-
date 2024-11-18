from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session, joinedload
from api.schemas import SiteCreateSchema
from auth.auth_bearer import JWTBearer, get_admin,get_admin_or_worker, get_current_user
from ..models.add_material import save_upload_file
from database import get_db
from dotenv import load_dotenv
import os
import shutil
import uuid
from ..models import DataBuddY, Material_Name, Vendor, SiteAddress,Addmaterial


load_dotenv()
router = APIRouter()

base_url_path = os.getenv("BASE_URL_PATH")

@router.post("/create_new_site_address/", response_model=None,dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def create_material(
    site_name_data: SiteCreateSchema,
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user),
):
    try:
        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in the database")

        site_address = SiteAddress(
            admin_id=current_user.user_id,
            site_name=site_name_data.site_name,
            site_address=site_name_data.site_address,
             
        )

        db.add(site_address)
        db.commit()
        db.refresh(site_address)  

        return site_address  

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create material: {str(e)}")