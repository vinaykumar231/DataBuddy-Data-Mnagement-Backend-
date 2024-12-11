from sqlalchemy import Column, DateTime, Integer, String,ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Excel_file(Base):
    __tablename__ = 'excel_files_tb'

    id = Column(Integer, primary_key=True, autoincrement=True)
    excel_fie_path = Column(String(255), nullable=True)  
    created_on = Column(DateTime, default=func.now())

    

    
    