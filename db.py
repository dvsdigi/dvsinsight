from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import os

DB_FILE = os.environ.get('STUDENTS_DB', 'students.db')
engine = create_engine(f'sqlite:///{DB_FILE}', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    student_name = Column(String, nullable=True)
    embedding_json = Column(Text, nullable=False)  # store list as json
    reference_image = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
