from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, TIMESTAMP, func, Date
from database import Base
from sqlalchemy.orm import relationship
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
import os
import shutil
import uuid

class Addmaterial(Base):
    __tablename__ = "add_materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id')) 
    Date = Column(Date)  
    Vendor_name = Column(String(250))
    challan_number = Column(String(250))
    site_address = Column(String(250))
    material = Column(String(250))
    
    sand_quantity = Column(Float)  
    sand_unit = Column(String(10), default="kg")  
    
    diesel_quantity = Column(Float) 
    diesel_unit = Column(String(10), default="L")  
    
    invoice = Column(String(250))
    truck = Column(String(250))
    created_on = Column(DateTime, default=func.now())
    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    
    user = relationship("DataBuddY", back_populates="add_material")


def save_upload_file(upload_file: UploadFile) -> str:
    if not upload_file:
        return None

    try:
        unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
        file_path = os.path.join("static", "docs", unique_filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        return file_path.replace("\\", "/")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
