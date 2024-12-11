from datetime import datetime, time, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
import pandas as pd
import pytz
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
from fastapi.responses import FileResponse
import time
from ..models.excel_file_dowloaded import Excel_file

load_dotenv()
router = APIRouter()

base_url_path = os.getenv("BASE_URL_PATH")


def generate_file_path():
    # Get the current timestamp and format it as 'dd-mm-yyyy_HH-MM-SS'
    timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    file_name = f"download_{timestamp}.xlsx"
    file_path = os.path.join("static", "excel_file", file_name).replace("\\", "/")
    return file_path

def format_date(date):
    return date.strftime('%d-%m-%y') if date else None

def format_date3(date):
    return date.strftime('%d-%m-%y %H:%M:%S') if date else None

def fetch_data_and_export_to_excel(file_path: str):
    db: Session = next(get_db()) 

    query = db.query(Addmaterial).all()

    
    data = []
    utc_now = pytz.utc.localize(datetime.utcnow())
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    for item in query:
        data.append({
            # "id": item.id,
            # "user_id": item.user_id,
            "Date": format_date(item.Date),
            "Vendor_name": item.Vendor_name,
            "challan_number": item.challan_number,
            "site_address": item.site_address,
            "material": item.material,
            "quantity": item.quantity,
            "quantity_unit": item.quantity_unit,
            # "invoice": item.invoice,
            # "truck": item.truck,
            "is_verified": item.is_verified,
            "status": item.status,
            "created_on": format_date3(item.created_on),
            "updated_on": format_date3(item.updated_on),
        })
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False, engine='openpyxl')
    excel_db=Excel_file(
        excel_fie_path=file_path,
        created_on=ist_now,
    )
    db.add(excel_db)
    db.commit()
    db.refresh(excel_db)  
    print(f"Data exported successfully to {file_path}")


@router.get("/export_excel_file")
def export_data(db: Session = Depends(get_db)):
    file_path = generate_file_path()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    fetch_data_and_export_to_excel(file_path)
    file= FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=os.path.basename(file_path))
    return file

@router.get("/get_excel_file_url")
def get_excel_file_url(db:Session=Depends(get_db)):
    try:
        existing_file=db.query(Excel_file).all()
        all_data=[]
        for file in existing_file:
            file_urls = f"{base_url_path}/{file.excel_fie_path}" if file.excel_fie_path else None
            data={
                "file_path":file_urls,
                "created_on":format_date3(file.created_on),
            }
            all_data.append(data)
        return  all_data
    except:
        raise HTTPException(status_code=404, detail="file Not found")
   

###############################################################################################################################################################

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
        
        existing_site = db.query(Vendor).filter(Vendor.name == vendor_name_data.name).first()
        if existing_site:
            raise HTTPException(status_code=400, detail=f"Material '{vendor_name_data.name}' already exists in the database.")

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


