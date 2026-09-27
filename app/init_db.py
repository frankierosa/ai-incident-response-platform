from app.core.database import Base, engine
from app.models.incident import Incident


# Initialize the database by creating all tables defined in the SQLAlchemy models. This function uses the metadata from the Base class to create the necessary tables in the database, ensuring that the schema is set up correctly before the application starts.
def init_db():
    Base.metadata.create_all(bind=engine)

# If this script is run as the main program, call the init_db function to initialize the database. This allows for easy setup of the database schema when starting the application or during development.ß
if __name__ == "__main__":
    init_db()