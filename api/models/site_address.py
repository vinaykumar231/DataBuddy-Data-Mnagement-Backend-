from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class SiteAddress(Base):
    __tablename__ = 'site_address'

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('users.user_id')) 
    site_name = Column(String(255), nullable=False)  
    site_address = Column(String(255), nullable=False)  
    

    user = relationship("DataBuddY", back_populates="site_address")
    


   
    