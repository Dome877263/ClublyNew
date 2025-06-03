from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pymongo
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
import uuid

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = pymongo.MongoClient(MONGO_URL)
db = client.clubly_db

# JWT configuration
JWT_SECRET = "clubly_secret_key_2024"
security = HTTPBearer()

# Pydantic models
class UserRegister(BaseModel):
    nome: str
    cognome: str
    email: str
    username: str
    password: str
    data_nascita: str
    citta: str
    ruolo: str = "cliente"

class UserLogin(BaseModel):
    email: str
    password: str

class Event(BaseModel):
    name: str
    date: str
    location: str
    organization: str
    start_time: str
    lineup: List[str] = []
    guests: List[str] = []
    total_tables: int = 0
    tables_available: int = 0
    max_party_size: int = 10
    image: Optional[str] = None

class Booking(BaseModel):
    event_id: str
    booking_type: str  # "lista" or "tavolo"
    party_size: int

class ChatMessage(BaseModel):
    chat_id: str
    sender_id: str
    sender_role: str
    message: str
    timestamp: Optional[str] = None

class Chat(BaseModel):
    booking_id: str
    client_id: str
    promoter_id: str
    event_id: str
    status: str = "active"  # active, closed

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_data: dict) -> str:
    payload = {
        **user_data,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token non valido")

def assign_promoter_to_event(event_id: str) -> str:
    """Trova un promoter disponibile per l'evento"""
    event = db.events.find_one({"id": event_id})
    if not event:
        return None
    
    # Trova un promoter della stessa organizzazione se possibile
    promoter = db.users.find_one({
        "ruolo": "promoter",
        "organization": event.get("organization"),
        "status": "available"
    })
    
    # Se non trova nessuno nella stessa organizzazione, prende qualsiasi promoter
    if not promoter:
        promoter = db.users.find_one({
            "ruolo": "promoter",
            "status": "available"
        })
    
    return promoter["id"] if promoter else None

# Initialize default data
def initialize_default_data():
    # Create default admin user if not exists
    if not db.users.find_one({"username": "admin"}):
        admin_user = {
            "id": str(uuid.uuid4()),
            "nome": "Admin",
            "cognome": "Clubly",
            "email": "admin@clubly.it",
            "username": "admin",
            "password": hash_password("admin123"),
            "ruolo": "clubly_founder",
            "data_nascita": "1990-01-01",
            "citta": "Milano",
            "created_at": datetime.utcnow()
        }
        db.users.insert_one(admin_user)
        print("Default admin user created")

    # Create sample promoters if none exist
    if not db.users.find_one({"ruolo": "promoter"}):
        sample_promoters = [
            {
                "id": str(uuid.uuid4()),
                "nome": "Marco",
                "cognome": "Rossi",
                "email": "marco.promoter@clubly.it",
                "username": "marco_promoter",
                "password": hash_password("Password1@"),
                "ruolo": "promoter",
                "data_nascita": "1995-03-15",
                "citta": "Milano",
                "organization": "Night Events Milano",
                "status": "available",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "nome": "Sara",
                "cognome": "Bianchi",
                "email": "sara.promoter@clubly.it",
                "username": "sara_promoter",
                "password": hash_password("Password1@"),
                "ruolo": "promoter",
                "data_nascita": "1993-07-22",
                "citta": "Roma",
                "organization": "Urban Nights",
                "status": "available",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "nome": "Alex",
                "cognome": "Verdi",
                "email": "alex.promoter@clubly.it",
                "username": "alex_promoter",
                "password": hash_password("Password1@"),
                "ruolo": "promoter",
                "data_nascita": "1992-11-08",
                "citta": "Torino",
                "organization": "Electronic Sessions",
                "status": "available",
                "created_at": datetime.utcnow()
            }
        ]
        db.users.insert_many(sample_promoters)
        print("Sample promoters created")

    # Create sample events if none exist
    if db.events.count_documents({}) == 0:
        sample_events = [
            {
                "id": str(uuid.uuid4()),
                "name": "NEON NIGHTS - Electronic Party",
                "date": "2024-04-15",
                "location": "Club Matrix, Milano",
                "organization": "Night Events Milano",
                "start_time": "23:00",
                "lineup": ["DJ Alex", "DJ Sarah", "MC John"],
                "guests": ["Special Guest TBA"],
                "total_tables": 20,
                "tables_available": 15,
                "max_party_size": 8,
                "image": "https://images.pexels.com/photos/11748607/pexels-photo-11748607.jpeg",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "RED PASSION - Hip Hop Night",
                "date": "2024-04-20",
                "location": "Warehouse Club, Roma",
                "organization": "Urban Nights",
                "start_time": "22:30",
                "lineup": ["DJ Mike", "DJ Luna"],
                "guests": ["Rapper Boss"],
                "total_tables": 15,
                "tables_available": 8,
                "max_party_size": 6,
                "image": "https://images.pexels.com/photos/15747701/pexels-photo-15747701.jpeg",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "TECHNO UNDERGROUND",
                "date": "2024-04-25",
                "location": "Deep Club, Torino",
                "organization": "Electronic Sessions",
                "start_time": "00:00",
                "lineup": ["DJ Techno", "DJ Beat", "DJ Flow"],
                "guests": [],
                "total_tables": 10,
                "tables_available": 10,
                "max_party_size": 12,
                "image": "https://images.unsplash.com/photo-1699871318112-188325a4a2c3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHwyfHxjbHVifGVufDB8fHxyZWR8MTc0ODk1ODc2M3ww&ixlib=rb-4.1.0&q=85",
                "created_at": datetime.utcnow()
            }
        ]
        db.events.insert_many(sample_events)
        print("Sample events created")

# Initialize data on startup
initialize_default_data()

# API Routes

@app.get("/")
async def root():
    return {"message": "Clubly API is running!"}

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user: UserRegister):
    # Check if user already exists
    if db.users.find_one({"$or": [{"email": user.email}, {"username": user.username}]}):
        raise HTTPException(status_code=400, detail="Utente già esistente")
    
    # Create new user
    user_data = {
        "id": str(uuid.uuid4()),
        "nome": user.nome,
        "cognome": user.cognome,
        "email": user.email,
        "username": user.username,
        "password": hash_password(user.password),
        "ruolo": user.ruolo,
        "data_nascita": user.data_nascita,
        "citta": user.citta,
        "created_at": datetime.utcnow()
    }
    
    db.users.insert_one(user_data)
    
    # Create JWT token
    token_data = {
        "id": user_data["id"],
        "email": user_data["email"],
        "username": user_data["username"],
        "ruolo": user_data["ruolo"]
    }
    token = create_jwt_token(token_data)
    
    return {
        "token": token,
        "user": {
            "id": user_data["id"],
            "nome": user_data["nome"],
            "cognome": user_data["cognome"],
            "email": user_data["email"],
            "username": user_data["username"],
            "ruolo": user_data["ruolo"],
            "citta": user_data["citta"]
        }
    }

@app.post("/api/auth/login")
async def login(user: UserLogin):
    # Find user in database
    db_user = db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    # Create JWT token
    token_data = {
        "id": db_user["id"],
        "email": db_user["email"],
        "username": db_user["username"],
        "ruolo": db_user["ruolo"]
    }
    token = create_jwt_token(token_data)
    
    return {
        "token": token,
        "user": {
            "id": db_user["id"],
            "nome": db_user["nome"],
            "cognome": db_user["cognome"],
            "email": db_user["email"],
            "username": db_user["username"],
            "ruolo": db_user["ruolo"],
            "citta": db_user["citta"]
        }
    }

@app.get("/api/user/profile")
async def get_profile(current_user = Depends(verify_jwt_token)):
    db_user = db.users.find_one({"id": current_user["id"]})
    if not db_user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    return {
        "id": db_user["id"],
        "nome": db_user["nome"],
        "cognome": db_user["cognome"],
        "email": db_user["email"],
        "username": db_user["username"],
        "ruolo": db_user["ruolo"],
        "citta": db_user["citta"]
    }

# Events endpoints
@app.get("/api/events")
async def get_events():
    events = list(db.events.find({}, {"_id": 0}).sort("date", 1))
    return events

@app.get("/api/events/{event_id}")
async def get_event(event_id: str):
    event = db.events.find_one({"id": event_id}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event

@app.post("/api/events")
async def create_event(event: Event, current_user = Depends(verify_jwt_token)):
    # Only clubly_founder can create events
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    event_data = {
        "id": str(uuid.uuid4()),
        **event.dict(),
        "created_at": datetime.utcnow(),
        "created_by": current_user["id"]
    }
    
    db.events.insert_one(event_data)
    return {"message": "Evento creato con successo", "event_id": event_data["id"]}

# Bookings endpoints
@app.post("/api/bookings")
async def create_booking(booking: Booking, current_user = Depends(verify_jwt_token)):
    # Check if event exists
    event = db.events.find_one({"id": booking.event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    # Find available promoter
    promoter_id = assign_promoter_to_event(booking.event_id)
    if not promoter_id:
        raise HTTPException(status_code=503, detail="Nessun promoter disponibile al momento")
    
    # Create booking
    booking_data = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "event_id": booking.event_id,
        "booking_type": booking.booking_type,
        "party_size": booking.party_size,
        "status": "pending",
        "promoter_id": promoter_id,
        "created_at": datetime.utcnow()
    }
    
    db.bookings.insert_one(booking_data)
    
    # Create chat for this booking
    chat_data = {
        "id": str(uuid.uuid4()),
        "booking_id": booking_data["id"],
        "client_id": current_user["id"],
        "promoter_id": promoter_id,
        "event_id": booking.event_id,
        "status": "active",
        "created_at": datetime.utcnow()
    }
    
    db.chats.insert_one(chat_data)
    
    # Create automatic initial message
    user = db.users.find_one({"id": current_user["id"]})
    booking_type_text = "Lista/Prevendita" if booking.booking_type == "lista" else "Tavolo"
    
    initial_message = f"""🎉 Nuova prenotazione per {event['name']}

👤 Cliente: {user['nome']} {user['cognome']} (@{user['username']})
📅 Evento: {event['name']}
📍 Luogo: {event['location']}
⏰ Data: {event['date']} alle {event['start_time']}
🎫 Tipo: {booking_type_text}
👥 Persone: {booking.party_size}

Ciao! Sono interessato/a a questa prenotazione. Puoi aiutarmi con i dettagli?"""
    
    initial_message_data = {
        "id": str(uuid.uuid4()),
        "chat_id": chat_data["id"],
        "sender_id": current_user["id"],
        "sender_role": "cliente",
        "message": initial_message,
        "timestamp": datetime.utcnow(),
        "is_automatic": True
    }
    
    db.chat_messages.insert_one(initial_message_data)
    
    # Update table availability if booking is for table
    if booking.booking_type == "tavolo" and event["tables_available"] > 0:
        db.events.update_one(
            {"id": booking.event_id},
            {"$inc": {"tables_available": -1}}
        )
    
    return {
        "message": "Prenotazione creata con successo! Chat avviata con il promoter.",
        "booking_id": booking_data["id"],
        "chat_id": chat_data["id"]
    }

@app.get("/api/user/bookings")
async def get_user_bookings(current_user = Depends(verify_jwt_token)):
    bookings = list(db.bookings.find({"user_id": current_user["id"]}, {"_id": 0}).sort("created_at", -1))
    
    # Populate event details for each booking
    for booking in bookings:
        event = db.events.find_one({"id": booking["event_id"]}, {"_id": 0})
        booking["event"] = event
    
    return bookings

# Organizations endpoints (for future development)
@app.get("/api/organizations")
async def get_organizations():
    organizations = list(db.organizations.find({}, {"_id": 0}))
    return organizations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)