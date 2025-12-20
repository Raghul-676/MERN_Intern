import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Bajaj Insurance RAG"
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "bajaj_insurance")
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    INDEX_DIR: str = os.getenv("INDEX_DIR", "./indices")
    # Fixed JSON I/O behavior is enforced in api/json_gateway.py

settings = Settings()
