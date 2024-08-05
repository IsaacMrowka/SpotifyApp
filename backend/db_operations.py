from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

db_url = "sqlite:///myspotifydatabase.db"

engine = create_engine(db_url)
Base = declarative_base()

class Track(Base):
    __tablename__ = "liked_tracks"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

class Recommendations(Base):
    __tablename__ = "track_recommendations"
    index = Column(Integer, index=True)
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

class TruePlaylist(Base):
    __tablename__ = "true_tracks"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

class FalsePlaylist(Base):
    __tablename__ = "false_tracks"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

class EndpointRequest(Base):
    __tablename__ = "counter"
    index = Column(Integer, primary_key=True)

class Search(Base):
    __tablename__ = "data_query"
    id = Column(String, primary_key=True)
    
Base.metadata.create_all(engine)