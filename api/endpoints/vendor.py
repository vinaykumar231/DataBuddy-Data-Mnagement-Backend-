from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session, joinedload
from api.schemas import vendorCreateSchema
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

@router.post("/create_new_vendor/", response_model=None,dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def create_material(
    vendor_name_data: vendorCreateSchema,
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user),
):
    try:
        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in the database")

        new_vendor = Vendor(
            admin_id=current_user.user_id,
            name=vendor_name_data.name,
            contact=vendor_name_data.contact,
            email=vendor_name_data.email,
             
        )

        db.add(new_vendor)
        db.commit()
        db.refresh(new_vendor)  

        return new_vendor  

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create material: {str(e)}")
    
@router.get("/vendor/{vendor_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_Vendor(vendor_id: int, db: Session = Depends(get_db)):
     try:
        vendor_db = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor_db:
            raise HTTPException(status_code=404, detail=f"vendor with ID {vendor_id} not found.")
        return vendor_db
     except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vendor: {str(e)}")
     
@router.get("/vendor_all_data/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def get_all_Vendor(db: Session = Depends(get_db)):
    try:
        Vendor_db = db.query(Vendor).all()
        if not Vendor_db:
            raise HTTPException(status_code=404, detail="No Vendor found.")
        return Vendor_db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to getall Vendor: {str(e)}")
    
@router.put("/vendor_update/{Vendor_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def update_Vendor(
    Vendor_id: int,
    Vendor_data: vendorCreateSchema,
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user)
):
   try:
        vendor = db.query(Vendor).filter(Vendor.id == Vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail=f"Vendor with ID {Vendor_id} not found.")
        
        vendor.name = Vendor_data.name
        vendor.email = Vendor_data.email
        vendor.contact = Vendor_data.contact

        db.commit()
        db.refresh(vendor)
        return vendor
   except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to getall Vendor: {str(e)}")
   
@router.delete("/vendor_delete/{Vendor_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_Vendor(Vendor_id: int, db: Session = Depends(get_db)):
    vendor_db = db.query(Vendor).filter(Vendor.id == Vendor_id).first()
    if not vendor_db:
        raise HTTPException(status_code=404, detail="Vendor not found")

    db.delete(vendor_db)
    db.commit()
    return {"message": "Vendor deleted successfully"}



# huihiui


