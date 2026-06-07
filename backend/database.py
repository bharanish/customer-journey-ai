from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql://admin:password@localhost:5432/customer_ai"
)

engine = create_engine(DATABASE_URL)
