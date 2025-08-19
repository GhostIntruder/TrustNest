from secureNest_backend import app, db
from sqlalchemy import text

with app.app_context():
    print("Beginning database reset...")
    
    # 1. Drop a specific custom type if it exists to prevent errors on drop_all()
    try:
        db.session.execute(text("DROP TYPE IF EXISTS originality_status_enum CASCADE"))
        db.session.commit()
        print("Dropped enum type successfully")
    except Exception as e:
        print(f"Error dropping enum: {e}")
        db.session.rollback()
    
    # 2. Drop all tables
    db.drop_all()
    print("All tables dropped.")
    
    # 3. Create all tables again
    db.create_all()
    print("All tables created.")
    
    print("Database reset complete!")