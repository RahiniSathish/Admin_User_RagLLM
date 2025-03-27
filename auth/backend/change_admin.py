
from backend.database import SessionLocal
from backend.models import User, Role

db = SessionLocal()
email = " "
user = db.query(User).filter_by(email=email).first()
role = db.query(Role).filter_by(name="Admin").first()
if not role:
    role = Role(name="Admin")
    db.add(role)
    db.commit()
    db.refresh(role)
if user:
    user.role_id = role.id
    db.commit()
    print(f"✅ '{email}' promoted to Admin.")
else:
    print("❌ User not found. Please register first.")
