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
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

class NewPlaylist(Base):
    __tablename__ = "new_tracks"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
Base.metadata.create_all(engine)