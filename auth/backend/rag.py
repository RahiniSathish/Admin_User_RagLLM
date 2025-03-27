from backend.models import Document
from backend.database import SessionLocal
from backend.llm import get_response
def store_document(name, content):
    db = SessionLocal()
    db.add(Document(name=name, content=content))
    db.commit()
    db.close()
def query_documents(question):
    db = SessionLocal()
    docs = db.query(Document).all()
    combined = "\n\n".join([d.content for d in docs])
    db.close()
    prompt = f"""Answer the question based on the following:
{combined}
Q: {question}
A:"""
    return get_response(prompt).content
