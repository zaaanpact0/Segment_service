from fastapi import FastAPI
from database import Base, engine
from models import User, Segment, UserSegment
from routers import users, segments

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(segments.router)