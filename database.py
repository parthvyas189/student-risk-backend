import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# --- RENDER DEPLOYMENT FIX ---
# On Render, we can't upload the file easily, so we store the content in an Env Var
# and write it to a file when the app starts.
if os.getenv("SSL_CERT_CONTENT"):
    with open("ca.pem", "w") as f:
        f.write(os.getenv("SSL_CERT_CONTENT"))

ssl_args = {
    "ssl": {
        "ca": "./ca.pem"
    }
}

engine = create_engine(
    DATABASE_URL, 
    connect_args=ssl_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()