"""
Database connection and session management
"""

from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.pool import StaticPool

# Create the declarative base for models
Base = declarative_base()

def init_db(app):
    """Initialize database connection"""
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///telegraph_messenger.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create engine with proper SQLite configuration
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        engine = create_engine(
            app.config['SQLALCHEMY_DATABASE_URI'],
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=app.config.get('SQLALCHEMY_ECHO', False)
        )
    else:
        engine = create_engine(
            app.config['SQLALCHEMY_DATABASE_URI'],
            echo=app.config.get('SQLALCHEMY_ECHO', False)
        )

    # Create all tables
    Base.metadata.create_all(engine)

    # Create scoped session
    SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # Store in app context
    app.db_session = SessionLocal
    app.db_engine = engine

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        SessionLocal.remove()

def get_db():
    """Get database session"""
    if 'db_session' not in g:
        g.db_session = current_app.db_session()
    return g.db_session

def get_engine():
    """Get database engine"""
    return current_app.db_engine