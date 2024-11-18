from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Material_Name(Base):
    __tablename__ = 'material_names'

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('users.user_id')) 
    name = Column(String(255), nullable=False) 
    quantity = Column(Integer, nullable=False)  
    description = Column(String(255), nullable=True)  

    user = relationship("DataBuddY", back_populates="material_name")
    

     
  