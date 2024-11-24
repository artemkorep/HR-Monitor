from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLDBURL = 'postgresql://username:password@db:5432/hrmonitor'

engine = create_engine(SQLDBURL)

session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()
