from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import Base, engine, SessionLocal
from backend.models import User, Role
from backend.auth import verify_password, create_token, hash_password
from backend.roles import get_db, require_role, require_role_any, get_current_user
from backend.utils import extract_text_from_pdf, extract_text_from_image, extract_text_from_docx
from backend.rag import store_document, query_documents


app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # CORS for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class UserRegister(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    return {"message": "Registered. Wait for Admin approval."}

@app.post("/login")
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    if not user.role_id:
        raise HTTPException(status_code=403, detail="Not yet approved by admin")
    access_token = create_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "role": current_user.role.name}

@app.post("/admin/approve")
def approve_user(email: str, role_name: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("Admin"))):
    user = db.query(User).filter(User.email == email).first()
    role = db.query(Role).filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)
    user.role_id = role.id
    db.commit()
    return {"message": f"User {email} approved as {role_name}"}

@app.delete("/admin/delete-user")
def delete_user(email: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("Admin"))):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": f"✅ User '{email}' deleted successfully"}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role_any(["Admin", "User"])),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    ext = file.filename.split('.')[-1].lower()

    if ext == "pdf":
        text = extract_text_from_pdf(contents)
    elif ext in ["jpg", "jpeg", "png"]:
        text = extract_text_from_image(contents)
    elif ext == "docx":
        text = extract_text_from_docx(contents)
    elif ext == "txt":
        text = contents.decode()
    else:
        raise HTTPException(400, "Unsupported file format")

    store_document(file.filename, text)
    return {"msg": f"✅ File '{file.filename}' uploaded successfully"}

@app.get("/query")
def query_llm(q: str, current_user: User = Depends(require_role_any(["Admin", "User"])), db: Session = Depends(get_db)):
    try:
        response = query_documents(q)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
