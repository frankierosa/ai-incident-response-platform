from app.core.database import Base, engine
from app.models.incident import Incident



def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()