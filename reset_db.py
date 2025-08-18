from secureNest_backend import app, db
from sqlalchemy import text

with app.app_context():
    # Drop the enum type if it exists
    try:
        db.session.execute(text("DROP TYPE IF EXISTS originality_status_enum"))
        db.session.commit()
        print("Dropped enum type successfully")
    except Exception as e:
        print(f"Error dropping enum: {e}")
        db.session.rollback()
    
    # Reset all tables
    db.drop_all()
    db.create_all()
    print("Database reset complete!")