#!/usr/bin/python3
""" City Module for HBNB project """
import os
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base


class City(BaseModel, Base):
    """ The city class, contains state ID and name """
    __tablename__ = 'cities'
    state_id = Column(
        String(60), ForeignKey('states.id'), nullable=False
    ) if os.getenv('HBNB_TYPE_STORAGE') == 'db' else ''
    name = Column(
        String(128), nullable=False
    ) if os.getenv('HBNB_TYPE_STORAGE') == 'db' else ''
    state = relationship(
        'State', backref='states.id'
    ) if os.getenv('HBNB_TYPE_STORAGE') == 'db' else None
    places = relationship(
        'Place',
        cascade='all, delete, delete-orphan',
        backref='places.id'
    ) if os.getenv('HBNB_TYPE_STORAGE') == 'db' else None
