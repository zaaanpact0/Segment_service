from database import Base, engine
from models import User, Segment, UserSegment
Base.metadata.create_all(bind=engine)