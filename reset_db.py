from secureNest_backend import app, db
from sqlalchemy import text

with app.app_context():
    print("Beginning database reset...")

    # 1. Drop a specific custom type if it exists (prevent enum conflicts)
    try:
        db.session.execute(text("DROP TYPE IF EXISTS originality_status_enum CASCADE"))
        db.session.commit()
        print("Dropped enum type successfully")
    except Exception as e:
        print(f"Error dropping enum: {e}")
        db.session.rollback()

    # 2. Drop all tables (models + alembic_version if tracked)
    db.drop_all()
    print("All tables dropped.")

    # 3. Explicitly drop alembic_version if it still exists
    try:
        db.session.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        db.session.commit()
        print("Dropped alembic_version table successfully")
    except Exception as e:
        print(f"Error dropping alembic_version: {e}")
        db.session.rollback()

    print("Database reset complete!")
