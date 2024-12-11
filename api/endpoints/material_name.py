from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session, joinedload
from api.schemas import MaterialCreateSchema
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

@router.post("/create_new_material_name/", response_model=None,dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def create_material(
    material_data: MaterialCreateSchema,
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user),
):
    try:
        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in the database")
        
        existing_material = db.query(Material_Name).filter(Material_Name.name == material_data.name).first()
        if existing_material:
            raise HTTPException(status_code=400, detail=f"Material '{material_data.name}' already exists in the database.")

        new_material = Material_Name(
            name=material_data.name,
            quantity=material_data.quantity,
            description=material_data.description,
            admin_id=current_user.user_id  
        )

        db.add(new_material)
        db.commit()
        db.refresh(new_material)  

        return new_material  

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create material: {str(e)}")
    
@router.get("/get_material/{material_id}",response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user),
):
    try:
        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in the database")

        material = db.query(Material_Name).filter(Material_Name.id == material_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Material data not found")
        
        return material

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material: {str(e)}")
    
@router.get("/get_all_materials", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def get_all_materials(
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user),
):
    try:
        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in the database")

        materials = db.query(Material_Name).all()
        if not materials:
            raise HTTPException(status_code=404, detail="No material data found")
        
        return materials

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get materials: {str(e)}")


@router.put("/update_material/{material_id}",response_model=None,  dependencies=[Depends(JWTBearer()), Depends(get_admin_or_worker)])
def update_material(
    material_id: int,
    material_data: MaterialCreateSchema,  
    db: Session = Depends(get_db),
    current_user: DataBuddY = Depends(get_current_user),
):
    try:
        user = db.query(DataBuddY).filter(DataBuddY.user_id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in the database")

        material = db.query(Material_Name).filter(Material_Name.id == material_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Material data not found")
        
        material.name = material_data.name
        material.quantity = material_data.quantity
        material.description = material_data.description

        db.commit()
        db.refresh(material)  

        return material

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update material: {str(e)}")
    
@router.delete("/delete_materials_name/{material_name_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_material(material_name_id: int, db: Session = Depends(get_db)):
    material_anme = db.query(Material_Name).filter(Material_Name.id == material_name_id).first()
    if not material_anme:
        raise HTTPException(status_code=404, detail="Material_name not found")

    db.delete(material_anme)
    db.commit()
    return {"message": "Material_name deleted successfully"}

