from sqlalchemy import create_engine

def get_engine():
    """
    Returns a SQLAlchemy engine connected to SQLite database.
    Change connection string for PostgreSQL later.
    """
    engine = create_engine("sqlite:///../data/food_waste.db", echo=False)
    return engine
