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
        
        existing_site = db.query(SiteAddress).filter(SiteAddress.site_name == site_name_data.site_name).first()
        if existing_site:
            raise HTTPException(status_code=400, detail=f"Material '{site_name_data.site_name}' already exists in the database.")


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
    
@router.get("/site_address/{site_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def get_site_address(site_id: int, db: Session = Depends(get_db)):
     try:
        site = db.query(SiteAddress).filter(SiteAddress.id == site_id).first()
        if not site:
            raise HTTPException(status_code=404, detail=f"Site address with ID {site_id} not found.")
        return site
     except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material: {str(e)}")
     
@router.get("/site_addresses", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def get_all_site_addresses(db: Session = Depends(get_db)):
    try:
        sites = db.query(SiteAddress).all()
        if not sites:
            raise HTTPException(status_code=404, detail="No site addresses found.")
        return sites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to getall site_addresses: {str(e)}")
    
@router.put("/site_address_update/{site_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def update_site_address(
    site_id: int,
    site_data: SiteCreateSchema,
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user)
):
   try:
        site = db.query(SiteAddress).filter(SiteAddress.id == site_id).first()
        if not site:
            raise HTTPException(status_code=404, detail=f"Site address with ID {site_id} not found.")
        
        site.site_name = site_data.site_name
        site.site_address = site_data.site_address

        db.commit()
        db.refresh(site)
        return site
   except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to getall site_addresses: {str(e)}")
   

@router.delete("/site_address_delete/{site_address_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_site_address(site_address_id: int, db: Session = Depends(get_db)):
    site_address = db.query(SiteAddress).filter(SiteAddress.id == site_address_id).first()
    if not site_address:
        raise HTTPException(status_code=404, detail="site address not found")

    db.delete(site_address)
    db.commit()
    return {"message": "Site Address deleted successfully"}


