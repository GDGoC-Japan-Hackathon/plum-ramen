import os
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes

def create_engine():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return sqlalchemy.create_engine(database_url)

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

    return sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)

engine = create_engine()
