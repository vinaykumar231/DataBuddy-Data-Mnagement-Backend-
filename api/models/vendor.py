from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Vendor(Base):
    __tablename__ = 'vendor_name'

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('users.user_id')) 
    name = Column(String(255), nullable=False)  
    contact = Column(String(255), nullable=True)  
    email = Column(String(255), nullable=True)  

    user = relationship("DataBuddY", back_populates="vendor_name")

    
    