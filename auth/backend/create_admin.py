# create_admin.py
from backend.database import SessionLocal
from backend.models import User, Role
from backend.auth import hash_password

db = SessionLocal()

email = "sathishjos76@gmail.com"
password = "Mithwin@162815"

# Get or create Admin role
role = db.query(Role).filter_by(name="Admin").first()
if not role:
    role = Role(name="Admin")
    db.add(role)
    db.commit()
    db.refresh(role)

# Get or create Admin user
user = db.query(User).filter_by(email=email).first()
if not user:
    user = User(email=email, hashed_password=hash_password(password), role_id=role.id)
    db.add(user)
    db.commit()
    print("✅ Admin user created!")
else:
    user.hashed_password = hash_password(password)
    user.role_id = role.id
    db.commit()
    print("✅ Admin user updated!")
