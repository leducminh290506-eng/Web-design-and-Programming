import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine

# 1. Đọc DATABASE_URL từ môi trường
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")

# 2. Tạo engine với echo=True để in log SQL ra terminal
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

# 3. Session dependency cho mỗi request
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]