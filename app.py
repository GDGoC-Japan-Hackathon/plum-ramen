import os

import sqlalchemy
from fastapi import FastAPI
from google.cloud.sql.connector import Connector, IPTypes

app = FastAPI()
connector = Connector(refresh_strategy="LAZY")


def getconn():
    return connector.connect(
        os.environ["INSTANCE_CONNECTION_NAME"],
        "pg8000",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        db=os.environ["DB_NAME"],
        ip_type=IPTypes.PUBLIC,
    )


engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/users")
def get_users():
    with engine.connect() as conn:
        rows = conn.execute(
            sqlalchemy.text("SELECT id, name FROM users ORDER BY id")
        ).mappings().all()

    return {"items": [dict(row) for row in rows]}

