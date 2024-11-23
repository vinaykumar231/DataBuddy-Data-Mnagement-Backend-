from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session, joinedload
from auth.auth_bearer import JWTBearer, get_admin,get_admin_or_worker, get_current_user
from ..models.add_material import save_upload_file
from database import get_db
from dotenv import load_dotenv
import os
import shutil
import uuid
from ..models import DataBuddY, Material_Name, Vendor, SiteAddress,Addmaterial
from datetime import date
import pytz

load_dotenv()
router = APIRouter()

base_url_path = os.getenv("BASE_URL_PATH")

@router.post("/add_materials_data/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def create_material(
    Date: date = Form(...),
    Vendor_name: str = Form(...),
    challan_number: str = Form(...),
    site_address: str = Form(...),
    material: str = Form(...),
    quantity: float = Form(...),
    quantity_unit: str = Form(...),
    invoice: UploadFile = File(...),
    truck: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user),
):
    try:
        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in the database")

        material_name = db.query(Material_Name).filter(Material_Name.name == material).first()
        if not material_name:
            raise HTTPException(status_code=404, detail="Material not found")

        vendor_name = db.query(Vendor).filter(Vendor.name == Vendor_name).first()
        if not vendor_name:
            raise HTTPException(status_code=404, detail="Vendor not found")

        site_addess = db.query(SiteAddress).filter(SiteAddress.site_address == site_address).first()
        if not site_addess:
            raise HTTPException(status_code=404, detail="Site address not found")

        invoice_url = save_upload_file(invoice)
        truck_url = save_upload_file(truck)
        
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        add_material_db = Addmaterial(
            user_id=current_user.user_id,
            Date=Date,
            Vendor_name=Vendor_name,
            challan_number=challan_number,
            site_address=site_address,
            material=material,
            quantity=quantity,
            quantity_unit=quantity_unit,
            invoice=invoice_url,
            truck=truck_url,
            created_on=ist_now,
        )
        db.add(add_material_db)
        db.commit()
        db.refresh(add_material_db)

        return {"message": "Material added successfully" ,"material_data":add_material_db}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add material: {str(e)}")
    
@router.put("/verify_material/{material_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def verify_material(material_id: int, db: Session = Depends(get_db)):
    try:
        material = db.query(Addmaterial).filter(Addmaterial.id == material_id).first()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found for the given user_id")
        
        material.is_verified = True
        material.status = 'verified'  
        db.commit()  
        
        db.refresh(material)
        
        invoice_url = f"{base_url_path}/{material.invoice}"
        truck_url = f"{base_url_path}/{material.truck}"

        material_data = {
            "material_id": material.id,
            "user_id": material.user_id,
            "Date": material.Date,
            "Vendor_name": material.Vendor_name,
            "challan_number": material.challan_number,
            "site_address": material.site_address,
            "material": material.material,
            "quantity": material.quantity,
            "quantity_unit": material.quantity_unit,
            "invoice_url": invoice_url,
            "truck_url": truck_url,
            "is_verified":material.is_verified,
            "status":material.status,
            "created_on": material.created_on,
            "updated_on": material.updated_on,
        }

        return material_data
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to verify material: {str(e)}")
    

@router.get("/get_materials_data/{material_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def get_material(
    material_id: int, 
    db: Session = Depends(get_db), 
    current_user: DataBuddY = Depends(get_current_user)
):
    try:
        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in database")

        material = db.query(Addmaterial).filter(Addmaterial.id == material_id, Addmaterial.is_verified == True, Addmaterial.user_id == current_user.user_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Material data not found")

        invoice_url = f"{base_url_path}/{material.invoice}"
        truck_url = f"{base_url_path}/{material.truck}"

        material_data = {
            "material_id": material.id,
            "user_id": material.user_id,
            "Date": material.Date,
            "Vendor_name": material.Vendor_name,
            "challan_number": material.challan_number,
            "site_address": material.site_address,
            "material": material.material,
            "quantity": material.quantity,
            "quantity_unit": material.quantity_unit,
            "invoice_url": invoice_url,
            "truck_url": truck_url,
            "is_verified":material.is_verified,
            "status":material.status,
            "created_on": material.created_on,
            "updated_on": material.updated_on,
        }

        return material_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material data: {str(e)}")
    
@router.get("/get_all_materials_data_for_worker/", response_model=None,  dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def get_all_materials(db: Session = Depends(get_db), current_user: DataBuddY = Depends(get_current_user)):
    try:
        materials = db.query(Addmaterial).filter(Addmaterial.user_id== current_user.user_id).all()
        if not materials:
            raise HTTPException(status_code=404, detail="Material data not found")

        material_list = []

        for material in materials:
            invoice_url = f"{base_url_path}/{material.invoice}"  
            truck_url = f"{base_url_path}/{material.truck}"  

            material_data = {
                "material_id": material.id,
                "user_id": material.user_id,
                "Date": material.Date,
                "Vendor_name": material.Vendor_name,
                "challan_number": material.challan_number,
                "site_address": material.site_address,
                "material": material.material,
                "quantity": material.quantity,
                "quantity_unit": material.quantity_unit,
                "invoice_url": invoice_url,
                "truck_url": truck_url,
                "status":material.status,
                "created_on": material.created_on,
                "updated_on": material.updated_on,
            }

            material_list.append(material_data)

        return material_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material data: {str(e)}")


@router.get("/get_all_materials_data/", response_model=None,  dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_all_materials_for_admin(db: Session = Depends(get_db)):
    try:
        materials = db.query(Addmaterial).options(joinedload(Addmaterial.user)).all()
        if not materials:
            raise HTTPException(status_code=404, detail="Material data not found")

        material_list = []

        for material in materials:
            invoice_url = f"{base_url_path}/{material.invoice}"  
            truck_url = f"{base_url_path}/{material.truck}"  

            material_data = {
                "material_id": material.id,
                "user_id": material.user_id,
                "worker_name":material.user.user_name,
                "Date": material.Date,
                "Vendor_name": material.Vendor_name,
                "challan_number": material.challan_number,
                "site_address": material.site_address,
                "material": material.material,
                "quantity": material.quantity,
                "quantity_unit": material.quantity_unit,
                "invoice_url": invoice_url,
                "invoice_url": invoice_url,
                "status":material.status,
                "truck_url": truck_url,
                "created_on": material.created_on,
                "updated_on": material.updated_on,
            }

            material_list.append(material_data)

        return material_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material data: {str(e)}")

    

@router.put("/update_material_data/{material_id}/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def update_material(
    material_id: int,
    Date: Optional[date] = Form(None),
    Vendor_name: Optional[str] = Form(None),
    challan_number: Optional[str] = Form(None),
    site_address: Optional[str] = Form(None),
    material: Optional[str] = Form(None),
    sand_quantity: Optional[float] = Form(None),
    sand_unit: Optional[str] = Form("kg"),
    diesel_quantity: Optional[float] = Form(None),
    diesel_unit: Optional[str] = Form("L"),
    invoice: Optional[UploadFile] = File(None),
    truck: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user),
):
    try:
        existing_material = db.query(Addmaterial).filter(Addmaterial.id == material_id).first()
        if not existing_material:
            raise HTTPException(status_code=404, detail="Material not found ")

        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in the database")
        
        if not invoice or not invoice.filename:
            raise HTTPException(status_code=404, detail="Please provide the invoice image again")

        if not truck or not truck.filename:
            raise HTTPException(status_code=404, detail="Please provide the truck image again")


        invoice_url = existing_material.invoice
        if invoice is not None:
            invoice_url = save_upload_file(invoice)

        truck_url = existing_material.truck
        if truck is not None:
            truck_url = save_upload_file(truck)

        if Date is not None:
            existing_material.Date = Date
        if Vendor_name is not None:
            existing_material.Vendor_name = Vendor_name
        if challan_number is not None:
            existing_material.challan_number = challan_number
        if site_address is not None:
            existing_material.site_address = site_address
        if material is not None:
            existing_material.material = material
        if sand_quantity is not None:
            existing_material.sand_quantity = sand_quantity
        if sand_unit is not None:
            existing_material.sand_unit = sand_unit
        if diesel_quantity is not None:
            existing_material.diesel_quantity = diesel_quantity
        if diesel_unit is not None:
            existing_material.diesel_unit = diesel_unit
        if invoice_url is not None:
            existing_material.invoice = invoice_url
        if truck_url is not None:
            existing_material.truck = truck_url

        existing_material.updated_on = func.now()

        db.commit()
        db.refresh(existing_material)

        return {"message": "Material updated successfully", "material_data": existing_material}

    except HTTPException as e:
        raise e 
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update material: {str(e)}")

    
@router.delete("/add_materials/{material_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Addmaterial).filter(Addmaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    db.delete(material)
    db.commit()
    return {"message": "Material deleted successfully"}


    