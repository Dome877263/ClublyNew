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
    profile_image: Optional[str] = None
    biografia: Optional[str] = None

class UserLogin(BaseModel):
    login: str  # Can be email or username
    password: str

class UserSetup(BaseModel):
    cognome: str
    username: str
    data_nascita: str
    citta: str
    profile_image: Optional[str] = None
    biografia: Optional[str] = None

class EventCreate(BaseModel):
    name: str
    date: str
    start_time: str
    location: str
    organization: Optional[str] = None
    end_time: Optional[str] = None
    lineup: Optional[List[str]] = []
    location_address: Optional[str] = None
    total_tables: Optional[int] = 0
    table_types: Optional[List[str]] = []
    max_party_size: Optional[int] = 10

class OrganizationCreate(BaseModel):
    name: str
    location: str
    # Removed capo_promoter_username - will be assigned later

class TemporaryCredentials(BaseModel):
    nome: str
    email: str
    password: str = "Password1"
    ruolo: str  # "promoter" or "capo_promoter"
    organization: Optional[str] = None  # Optional - can be assigned later

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class OrganizationUpdate(BaseModel):
    capo_promoter_id: Optional[str] = None

class EventUpdate(BaseModel):
    name: Optional[str] = None
    lineup: Optional[List[str]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    guests: Optional[List[str]] = None
    event_poster: Optional[str] = None

class UserSearch(BaseModel):
    search_term: Optional[str] = ""
    role_filter: Optional[str] = None
    creation_date_from: Optional[str] = None
    creation_date_to: Optional[str] = None

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
    event_poster: Optional[str] = None

class Booking(BaseModel):
    event_id: str
    booking_type: str  # "lista" or "tavolo"
    party_size: int
    selected_promoter_id: Optional[str] = None  # Allow client to select specific promoter

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
    """Trova il promoter con meno prenotazioni per l'evento"""
    event = db.events.find_one({"id": event_id})
    if not event:
        return None
    
    # Ottieni tutti i promoter della stessa organizzazione dell'evento
    promoters = list(db.users.find({
        "ruolo": {"$in": ["promoter", "capo_promoter"]},
        "organization": event.get("organization"),
        "status": "available"
    }))
    
    if not promoters:
        # Se non ci sono promoter nella stessa organizzazione, prova con qualsiasi promoter
        promoters = list(db.users.find({
            "ruolo": {"$in": ["promoter", "capo_promoter"]},
            "status": "available"
        }))
    
    if not promoters:
        return None
    
    # Conta le prenotazioni per ogni promoter
    promoter_bookings = {}
    for promoter in promoters:
        booking_count = db.bookings.count_documents({
            "promoter_id": promoter["id"],
            "status": {"$in": ["pending", "confirmed"]}
        })
        promoter_bookings[promoter["id"]] = booking_count
    
    # Trova il promoter con meno prenotazioni
    min_bookings_promoter_id = min(promoter_bookings, key=promoter_bookings.get)
    
    return min_bookings_promoter_id

def validate_event_datetime(date_str: str, time_str: str) -> bool:
    """Valida che data e ora dell'evento non siano nel passato"""
    try:
        from datetime import datetime, timedelta
        
        # Combina data e ora
        event_datetime_str = f"{date_str} {time_str}"
        event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
        
        # Aggiungi un margine di 1 ora per permettere eventi molto vicini
        now = datetime.now() - timedelta(hours=1)
        
        return event_datetime > now
    except:
        return False

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
            "biografia": "Fondatore di Clubly, appassionato di vita notturna e tecnologia.",
            "profile_image": None,
            "needs_setup": False,
            "created_at": datetime.utcnow()
        }
        db.users.insert_one(admin_user)
        print("Default admin user created")

    # Create default capo promoter if not exists
    if not db.users.find_one({"ruolo": "capo_promoter"}):
        capo_promoter = {
            "id": str(uuid.uuid4()),
            "nome": "Marco",
            "cognome": "Capo",
            "email": "capo@clubly.it",
            "username": "capo_milano",
            "password": hash_password("Password1"),
            "ruolo": "capo_promoter",
            "data_nascita": "1988-05-10",
            "citta": "Milano",
            "biografia": "Capo promoter con 10 anni di esperienza nel settore della vita notturna milanese.",
            "organization": "Night Events Milano",
            "profile_image": None,
            "needs_setup": False,
            "created_at": datetime.utcnow()
        }
        db.users.insert_one(capo_promoter)
        print("Default capo promoter created")

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
                "biografia": "Promoter esperto di eventi electronic e house music. Amo creare esperienze indimenticabili!",
                "organization": "Night Events Milano",
                "status": "available",
                "profile_image": None,
                "needs_setup": False,
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
                "biografia": "Specializzata in eventi hip-hop e R&B. Sempre alla ricerca delle novità musicali.",
                "organization": "Urban Nights",
                "status": "available",
                "profile_image": None,
                "needs_setup": False,
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
                "biografia": "DJ e promoter di eventi techno underground. La notte è il mio mondo!",
                "organization": "Electronic Sessions",
                "status": "available",
                "profile_image": None,
                "needs_setup": False,
                "created_at": datetime.utcnow()
            }
        ]
        db.users.insert_many(sample_promoters)
        print("Sample promoters created")

    # Create organizations if none exist
    if db.organizations.count_documents({}) == 0:
        sample_organizations = [
            {
                "id": str(uuid.uuid4()),
                "name": "Night Events Milano",
                "location": "Milano",
                "capo_promoter_id": None,  # Will be updated when capo promoter confirms
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Urban Nights",
                "location": "Roma", 
                "capo_promoter_id": None,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Electronic Sessions",
                "location": "Torino",
                "capo_promoter_id": None,
                "created_at": datetime.utcnow()
            }
        ]
        db.organizations.insert_many(sample_organizations)
        print("Sample organizations created")

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
        "biografia": user.biografia or "",
        "profile_image": user.profile_image,
        "needs_setup": False,
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
            "citta": user_data["citta"],
            "biografia": user_data["biografia"],
            "profile_image": user_data["profile_image"],
            "needs_setup": user_data["needs_setup"]
        }
    }

@app.post("/api/auth/login")
async def login(user: UserLogin):
    # Find user in database by email or username
    db_user = db.users.find_one({
        "$or": [
            {"email": user.login},
            {"username": user.login}
        ]
    })
    
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Email o password non corrette")
    
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
            "citta": db_user["citta"],
            "biografia": db_user.get("biografia", ""),
            "profile_image": db_user.get("profile_image"),
            "needs_setup": db_user.get("needs_setup", False),
            "needs_password_change": db_user.get("needs_password_change", False),
            "organization": db_user.get("organization")
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
        "citta": db_user["citta"],
        "biografia": db_user.get("biografia", ""),
        "profile_image": db_user.get("profile_image"),
        "needs_setup": db_user.get("needs_setup", False),
        "organization": db_user.get("organization")
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
    
    # Validate event date and time
    if not validate_event_datetime(event.date, event.start_time):
        raise HTTPException(status_code=400, detail="Non puoi creare eventi con date o orari nel passato")
    
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
    
    # Auto-assign promoter with least bookings (no manual selection)
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
        "auto_assigned": True,
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
    promoter = db.users.find_one({"id": promoter_id})
    booking_type_text = "Lista/Prevendita" if booking.booking_type == "lista" else "Tavolo"
    
    # Enhanced initial message with promoter info
    initial_message = f"""🎉 Nuova prenotazione per {event['name']}

👤 Cliente: {user['nome']} {user['cognome']} (@{user['username']})
🎯 PR Assegnato Automaticamente: {promoter['nome']} {promoter['cognome']} (@{promoter['username']})
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
        "message": "Prenotazione creata con successo! Chat avviata con il promoter assegnato automaticamente.",
        "booking_id": booking_data["id"],
        "chat_id": chat_data["id"],
        "promoter_name": f"{promoter['nome']} {promoter['cognome']}"
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

# Chat endpoints
@app.get("/api/user/chats")
async def get_user_chats(current_user = Depends(verify_jwt_token)):
    """Get all chats for the current user"""
    chats = list(db.chats.find({
        "$or": [
            {"client_id": current_user["id"]},
            {"promoter_id": current_user["id"]}
        ]
    }, {"_id": 0}).sort("created_at", -1))
    
    # Populate chat details
    for chat in chats:
        # Get event details
        event = db.events.find_one({"id": chat["event_id"]}, {"_id": 0})
        chat["event"] = event
        
        # Get other participant details
        if chat["client_id"] == current_user["id"]:
            # Current user is client, get promoter details
            promoter = db.users.find_one({"id": chat["promoter_id"]}, {"_id": 0, "password": 0})
            chat["other_participant"] = promoter
            chat["participant_role"] = "promoter"
        else:
            # Current user is promoter, get client details
            client = db.users.find_one({"id": chat["client_id"]}, {"_id": 0, "password": 0})
            chat["other_participant"] = client
            chat["participant_role"] = "cliente"
        
        # Get last message
        last_message = db.chat_messages.find_one(
            {"chat_id": chat["id"]}, 
            {"_id": 0}, 
            sort=[("timestamp", -1)]
        )
        chat["last_message"] = last_message
    
    return chats

@app.get("/api/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: str, current_user = Depends(verify_jwt_token)):
    """Get all messages for a specific chat"""
    # Verify user has access to this chat
    chat = db.chats.find_one({
        "id": chat_id,
        "$or": [
            {"client_id": current_user["id"]},
            {"promoter_id": current_user["id"]}
        ]
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat non trovata")
    
    messages = list(db.chat_messages.find(
        {"chat_id": chat_id}, 
        {"_id": 0}
    ).sort("timestamp", 1))
    
    return messages

@app.post("/api/chats/{chat_id}/messages")
async def send_message(chat_id: str, message: ChatMessage, current_user = Depends(verify_jwt_token)):
    """Send a message to a specific chat"""
    # Verify user has access to this chat
    chat = db.chats.find_one({
        "id": chat_id,
        "$or": [
            {"client_id": current_user["id"]},
            {"promoter_id": current_user["id"]}
        ]
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat non trovata")
    
    # Create message
    message_data = {
        "id": str(uuid.uuid4()),
        "chat_id": chat_id,
        "sender_id": current_user["id"],
        "sender_role": current_user["ruolo"],
        "message": message.message,
        "timestamp": datetime.utcnow(),
        "is_automatic": False
    }
    
    db.chat_messages.insert_one(message_data)
    
    return {"message": "Messaggio inviato con successo", "message_id": message_data["id"]}

@app.put("/api/bookings/{booking_id}/status")
async def update_booking_status(booking_id: str, status: str, current_user = Depends(verify_jwt_token)):
    """Update booking status (confirm/cancel) - only promoters can do this"""
    if current_user["ruolo"] not in ["promoter", "capo_promoter", "clubly_founder"]:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Update booking status
    result = db.bookings.update_one(
        {"id": booking_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    
    return {"message": f"Prenotazione {status} con successo"}

# User setup endpoint
@app.post("/api/user/setup")
async def complete_user_setup(setup: UserSetup, current_user = Depends(verify_jwt_token)):
    """Complete user profile setup for temporary accounts"""
    # Check if username is already taken
    existing_user = db.users.find_one({
        "username": setup.username,
        "id": {"$ne": current_user["id"]}
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="Username già esistente")
    
    # Update user profile
    update_data = {
        "cognome": setup.cognome,
        "username": setup.username,
        "data_nascita": setup.data_nascita,
        "citta": setup.citta,
        "biografia": setup.biografia or "",
        "profile_image": setup.profile_image,
        "needs_setup": False,
        "updated_at": datetime.utcnow()
    }
    
    result = db.users.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    # Return updated user data
    updated_user = db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    return {"message": "Profilo completato con successo", "user": updated_user}

# Organization management endpoints
@app.get("/api/organizations")
async def get_organizations():
    organizations = list(db.organizations.find({}, {"_id": 0}))
    return organizations

@app.post("/api/organizations")
async def create_organization(org: OrganizationCreate, current_user = Depends(verify_jwt_token)):
    """Create a new organization (only clubly_founder can do this)"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if organization name already exists
    if db.organizations.find_one({"name": org.name}):
        raise HTTPException(status_code=400, detail="Organizzazione già esistente")
    
    org_data = {
        "id": str(uuid.uuid4()),
        "name": org.name,
        "location": org.location,
        "capo_promoter_id": None,  # Will be set later when assigning
        "created_by": current_user["id"],
        "created_at": datetime.utcnow()
    }
    
    db.organizations.insert_one(org_data)
    return {"message": "Organizzazione creata con successo", "organization_id": org_data["id"]}

@app.get("/api/organizations/{org_name}/members")
async def get_organization_members(org_name: str, current_user = Depends(verify_jwt_token)):
    """Get all members of an organization"""
    # Check if user has access to this organization
    if current_user["ruolo"] not in ["capo_promoter", "promoter", "clubly_founder"]:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    members = list(db.users.find(
        {"organization": org_name}, 
        {"_id": 0, "password": 0}
    ).sort("ruolo", 1))
    
    return members

@app.get("/api/organizations/{org_name}/events")
async def get_organization_events(org_name: str, current_user = Depends(verify_jwt_token)):
    """Get all events for an organization"""
    events = list(db.events.find(
        {"organization": org_name}, 
        {"_id": 0}
    ).sort("date", 1))
    
    return events

# Temporary credentials management
@app.post("/api/users/temporary-credentials")
async def create_temporary_credentials(creds: TemporaryCredentials, current_user = Depends(verify_jwt_token)):
    """Create temporary credentials for new promoters/capo_promoters"""
    # Check permissions
    if current_user["ruolo"] == "capo_promoter" and creds.ruolo != "promoter":
        raise HTTPException(status_code=403, detail="Capo promoter può creare solo account promoter")
    elif current_user["ruolo"] == "clubly_founder" and creds.ruolo not in ["promoter", "capo_promoter"]:
        raise HTTPException(status_code=403, detail="Ruolo non valido")
    elif current_user["ruolo"] not in ["capo_promoter", "clubly_founder"]:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if email already exists
    if db.users.find_one({"email": creds.email}):
        raise HTTPException(status_code=400, detail="Email già esistente")
    
    # Handle organization assignment
    organization = None
    if creds.organization:
        # Verify organization exists if provided
        if not db.organizations.find_one({"name": creds.organization}):
            raise HTTPException(status_code=400, detail="Organizzazione non trovata")
        organization = creds.organization
    
    # For promoters created by capo_promoter, use capo_promoter's organization if not specified
    if current_user["ruolo"] == "capo_promoter":
        user = db.users.find_one({"id": current_user["id"]})
        if creds.organization and user.get("organization") != creds.organization:
            raise HTTPException(status_code=403, detail="Puoi creare credenziali solo per la tua organizzazione")
        # If no organization specified for promoter, use capo_promoter's organization
        if creds.ruolo == "promoter" and not organization:
            organization = user.get("organization")
    
    # Create temporary user
    user_data = {
        "id": str(uuid.uuid4()),
        "nome": creds.nome,
        "cognome": "",  # Will be set during setup
        "email": creds.email,
        "username": "",  # Will be set during setup
        "password": hash_password(creds.password),
        "ruolo": creds.ruolo,
        "data_nascita": "",  # Will be set during setup
        "citta": "",  # Will be set during setup
        "organization": organization,  # Can be None for capo_promoter
        "profile_image": None,
        "needs_setup": True,
        "needs_password_change": True,  # Must change password on first login
        "status": "available" if creds.ruolo == "promoter" else None,
        "created_by": current_user["id"],
        "created_at": datetime.utcnow()
    }
    
    db.users.insert_one(user_data)
    
    return {
        "message": "Credenziali temporanee create con successo",
        "user_id": user_data["id"],
        "email": creds.email,
        "temporary_password": creds.password,
        "organization": organization or "Da assegnare"
    }

# Dashboard data endpoints
@app.get("/api/dashboard/promoter")
async def get_promoter_dashboard(current_user = Depends(verify_jwt_token)):
    """Get promoter dashboard data"""
    if current_user["ruolo"] not in ["promoter", "capo_promoter"]:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    user = db.users.find_one({"id": current_user["id"]})
    organization = user.get("organization")
    
    # Get organization events
    events = list(db.events.find(
        {"organization": organization}, 
        {"_id": 0}
    ).sort("date", 1))
    
    # Get organization members
    members = list(db.users.find(
        {"organization": organization}, 
        {"_id": 0, "password": 0}
    ).sort("ruolo", 1))
    
    # Get promoter's active chats
    chats = list(db.chats.find({
        "promoter_id": current_user["id"],
        "status": "active"
    }, {"_id": 0}).sort("created_at", -1))
    
    # Populate chat details
    for chat in chats:
        event = db.events.find_one({"id": chat["event_id"]}, {"_id": 0})
        client = db.users.find_one({"id": chat["client_id"]}, {"_id": 0, "password": 0})
        chat["event"] = event
        chat["client"] = client
        
        # Get last message
        last_message = db.chat_messages.find_one(
            {"chat_id": chat["id"]}, 
            {"_id": 0}, 
            sort=[("timestamp", -1)]
        )
        chat["last_message"] = last_message
    
    return {
        "organization": organization,
        "events": events,
        "members": members,
        "chats": chats
    }

@app.get("/api/dashboard/capo-promoter")
async def get_capo_promoter_dashboard(current_user = Depends(verify_jwt_token)):
    """Get capo promoter dashboard data"""
    if current_user["ruolo"] != "capo_promoter":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Get the same data as promoter dashboard
    dashboard_data = await get_promoter_dashboard(current_user)
    
    # Add additional permissions info
    dashboard_data["can_edit_events"] = True
    dashboard_data["can_create_promoters"] = True
    
    return dashboard_data

@app.get("/api/dashboard/clubly-founder")
async def get_clubly_founder_dashboard(current_user = Depends(verify_jwt_token)):
    """Get clubly founder dashboard data"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Get all organizations
    organizations = list(db.organizations.find({}, {"_id": 0}))
    
    # Get all events
    events = list(db.events.find({}, {"_id": 0}).sort("date", 1))
    
    # Get all users by role
    users_by_role = {
        "capo_promoter": list(db.users.find({"ruolo": "capo_promoter"}, {"_id": 0, "password": 0})),
        "promoter": list(db.users.find({"ruolo": "promoter"}, {"_id": 0, "password": 0})),
        "cliente": db.users.count_documents({"ruolo": "cliente"})
    }
    
    return {
        "organizations": organizations,
        "events": events,
        "users": users_by_role
    }

# Event management for capo promoters
@app.put("/api/events/{event_id}")
async def update_event(event_id: str, event_update: dict, current_user = Depends(verify_jwt_token)):
    """Update event details (only capo_promoter can do this)"""
    if current_user["ruolo"] not in ["capo_promoter", "clubly_founder"]:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if event exists and user has permission
    event = db.events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    # If capo_promoter, check if event belongs to their organization
    if current_user["ruolo"] == "capo_promoter":
        user = db.users.find_one({"id": current_user["id"]})
        if event["organization"] != user.get("organization"):
            raise HTTPException(status_code=403, detail="Non autorizzato per questo evento")
    
    # Update allowed fields for capo_promoter: name, lineup, start_time, end_time, guests, event_poster
    allowed_fields = ["name", "lineup", "start_time", "end_time", "guests", "event_poster"]
    update_data = {k: v for k, v in event_update.items() if k in allowed_fields}
    update_data["updated_at"] = datetime.utcnow()
    update_data["updated_by"] = current_user["id"]
    
    result = db.events.update_one(
        {"id": event_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    return {"message": "Evento aggiornato con successo"}

# Organization management APIs
@app.put("/api/organizations/{org_id}/assign-capo-promoter")
async def assign_capo_promoter_to_organization(org_id: str, update: OrganizationUpdate, current_user = Depends(verify_jwt_token)):
    """Assign a capo promoter to an organization (only clubly_founder can do this)"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if organization exists
    org = db.organizations.find_one({"id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    # If capo_promoter_id provided, validate it exists and is actually a capo_promoter
    if update.capo_promoter_id:
        capo_promoter = db.users.find_one({
            "id": update.capo_promoter_id,
            "ruolo": "capo_promoter"
        })
        if not capo_promoter:
            raise HTTPException(status_code=400, detail="Capo promoter non trovato")
        
        # Update capo promoter's organization
        db.users.update_one(
            {"id": update.capo_promoter_id},
            {"$set": {"organization": org["name"]}}
        )
    
    # Update organization
    result = db.organizations.update_one(
        {"id": org_id},
        {"$set": {"capo_promoter_id": update.capo_promoter_id, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    return {"message": "Capo promoter assegnato con successo"}

@app.get("/api/organizations/available-capo-promoters")
async def get_available_capo_promoters(current_user = Depends(verify_jwt_token)):
    """Get list of capo promoters not yet assigned to organizations"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Get capo promoters without organization or with organization but not yet assigned as capo
    capo_promoters = list(db.users.find(
        {
            "ruolo": "capo_promoter",
            "$or": [
                {"organization": {"$exists": False}},
                {"organization": None},
                {"organization": ""}
            ]
        },
        {"_id": 0, "password": 0}
    ))
    
    return capo_promoters

# Password change API
@app.post("/api/user/change-password")
async def change_password(password_data: PasswordChange, current_user = Depends(verify_jwt_token)):
    """Change user password"""
    user = db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    # Verify current password
    if not verify_password(password_data.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Password attuale non corretta")
    
    # Update password
    result = db.users.update_one(
        {"id": current_user["id"]},
        {
            "$set": {
                "password": hash_password(password_data.new_password),
                "needs_password_change": False,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    return {"message": "Password cambiata con successo"}

# Event management enhancements for clubly founder
@app.delete("/api/events/{event_id}")
async def delete_event(event_id: str, current_user = Depends(verify_jwt_token)):
    """Delete event (only clubly_founder can do this)"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if event exists
    event = db.events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    # Delete related bookings and chats first
    bookings = list(db.bookings.find({"event_id": event_id}))
    for booking in bookings:
        db.chats.delete_many({"booking_id": booking["id"]})
        db.chat_messages.delete_many({"chat_id": {"$in": [chat["id"] for chat in db.chats.find({"booking_id": booking["id"]})]}})
    
    db.bookings.delete_many({"event_id": event_id})
    
    # Delete event
    result = db.events.delete_one({"id": event_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    return {"message": "Evento eliminato con successo"}

@app.put("/api/events/{event_id}/poster")
async def update_event_poster(event_id: str, poster_data: dict, current_user = Depends(verify_jwt_token)):
    """Update event poster - clubly_founder can add, capo_promoter can modify"""
    if current_user["ruolo"] not in ["clubly_founder", "capo_promoter"]:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if event exists
    event = db.events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    # If capo_promoter, check if event belongs to their organization
    if current_user["ruolo"] == "capo_promoter":
        user = db.users.find_one({"id": current_user["id"]})
        if event["organization"] != user.get("organization"):
            raise HTTPException(status_code=403, detail="Non autorizzato per questo evento")
    
    # Update poster
    result = db.events.update_one(
        {"id": event_id},
        {
            "$set": {
                "event_poster": poster_data.get("event_poster"),
                "updated_at": datetime.utcnow(),
                "updated_by": current_user["id"]
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    return {"message": "Locandina evento aggiornata con successo"}

# Enhanced event update for clubly founder
@app.put("/api/events/{event_id}/full-update")
async def full_update_event(event_id: str, event_update: EventUpdate, current_user = Depends(verify_jwt_token)):
    """Full event update for clubly founder (can modify anything)"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if event exists
    event = db.events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    # Prepare update data
    update_data = {}
    for field, value in event_update.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nessun campo da aggiornare")
    
    update_data["updated_at"] = datetime.utcnow()
    update_data["updated_by"] = current_user["id"]
    
    result = db.events.update_one(
        {"id": event_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    return {"message": "Evento aggiornato con successo"}

# Notifications API
@app.get("/api/user/notifications")
async def get_user_notifications(current_user = Depends(verify_jwt_token)):
    """Get user notifications count"""
    user_role = current_user["ruolo"]
    notification_count = 0
    
    if user_role in ["promoter", "capo_promoter"]:
        # Count new messages in active chats
        chats = db.chats.find({
            "promoter_id": current_user["id"],
            "status": "active"
        })
        
        for chat in chats:
            # Count unread messages (simplified - count messages from last 24 hours)
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            unread_count = db.chat_messages.count_documents({
                "chat_id": chat["id"],
                "sender_id": {"$ne": current_user["id"]},
                "timestamp": {"$gte": yesterday}
            })
            notification_count += unread_count
    
    elif user_role == "cliente":
        # Count new messages in user's chats
        chats = db.chats.find({
            "client_id": current_user["id"],
            "status": "active"
        })
        
        for chat in chats:
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            unread_count = db.chat_messages.count_documents({
                "chat_id": chat["id"],
                "sender_id": {"$ne": current_user["id"]},
                "timestamp": {"$gte": yesterday}
            })
            notification_count += unread_count
    
    return {"notification_count": min(notification_count, 99)}  # Cap at 99

# User profile viewing endpoints
@app.get("/api/users/{user_id}/profile")
async def get_user_profile(user_id: str, current_user = Depends(verify_jwt_token)):
    """Get public profile of any user"""
    user = db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    return {
        "id": user["id"],
        "nome": user["nome"],
        "cognome": user["cognome"],
        "username": user["username"],
        "profile_image": user.get("profile_image"),
        "citta": user["citta"],
        "biografia": user.get("biografia"),
        "ruolo": user["ruolo"],
        "organization": user.get("organization"),
        "created_at": user["created_at"]
    }

# User search endpoint
@app.post("/api/users/search")
async def search_users(search_params: UserSearch, current_user = Depends(verify_jwt_token)):
    """Search users with filters"""
    query = {}
    
    # Text search on nome, cognome, username
    if search_params.search_term:
        query["$or"] = [
            {"nome": {"$regex": search_params.search_term, "$options": "i"}},
            {"cognome": {"$regex": search_params.search_term, "$options": "i"}},
            {"username": {"$regex": search_params.search_term, "$options": "i"}}
        ]
    
    # Role filter
    if search_params.role_filter:
        query["ruolo"] = search_params.role_filter
    
    # Date filter
    if search_params.creation_date_from or search_params.creation_date_to:
        date_query = {}
        if search_params.creation_date_from:
            date_query["$gte"] = datetime.fromisoformat(search_params.creation_date_from)
        if search_params.creation_date_to:
            date_query["$lte"] = datetime.fromisoformat(search_params.creation_date_to)
        query["created_at"] = date_query
    
    users = list(db.users.find(query, {
        "_id": 0, 
        "password": 0
    }).sort("created_at", -1).limit(50))
    
    # Return only public info
    return [{
        "id": user["id"],
        "nome": user["nome"],
        "cognome": user["cognome"],
        "username": user["username"],
        "profile_image": user.get("profile_image"),
        "citta": user["citta"],
        "biografia": user.get("biografia"),
        "ruolo": user["ruolo"],
        "organization": user.get("organization"),
        "created_at": user["created_at"]
    } for user in users]

# Profile editing endpoint
class ProfileEdit(BaseModel):
    nome: str
    username: str
    biografia: Optional[str] = ""
    citta: str

@app.put("/api/user/profile/edit")
async def edit_user_profile(profile_data: ProfileEdit, current_user = Depends(verify_jwt_token)):
    """Edit user profile - nome, username, biografia, città"""
    # Check if username is already taken by another user
    existing_user = db.users.find_one({
        "username": profile_data.username,
        "id": {"$ne": current_user["id"]}
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="Username già esistente")
    
    # Update user profile
    update_data = {
        "nome": profile_data.nome,
        "username": profile_data.username,
        "biografia": profile_data.biografia or "",
        "citta": profile_data.citta,
        "updated_at": datetime.utcnow()
    }
    
    result = db.users.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    # Return updated user data
    updated_user = db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    return {"message": "Profilo aggiornato con successo", "user": updated_user}

# Event creation for promoters
@app.post("/api/events/create-by-promoter")
async def create_event_by_promoter(event: EventCreate, current_user = Depends(verify_jwt_token)):
    """Create event by promoter"""
    if current_user["ruolo"] not in ["promoter", "capo_promoter", "clubly_founder"]:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Get user's organization if not specified
    user = db.users.find_one({"id": current_user["id"]})
    organization = event.organization or user.get("organization")
    
    event_data = {
        "id": str(uuid.uuid4()),
        "name": event.name,
        "date": event.date,
        "start_time": event.start_time,
        "location": event.location,
        "organization": organization,
        "end_time": event.end_time,
        "lineup": event.lineup or [],
        "location_address": event.location_address,
        "total_tables": event.total_tables or 0,
        "tables_available": event.total_tables or 0,
        "table_types": event.table_types or [],
        "max_party_size": event.max_party_size or 10,
        "guests": [],
        "image": None,
        "created_at": datetime.utcnow(),
        "created_by": current_user["id"]
    }
    
    db.events.insert_one(event_data)
    return {"message": "Evento creato con successo", "event_id": event_data["id"]}

# Organization details endpoint
@app.get("/api/organizations/{org_id}")
async def get_organization_details(org_id: str, current_user = Depends(verify_jwt_token)):
    """Get organization details with members"""
    org = db.organizations.find_one({"id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    # Get organization members
    members = list(db.users.find(
        {"organization": org["name"]}, 
        {"_id": 0, "password": 0}
    ).sort("ruolo", 1))
    
    # Get organization events
    events = list(db.events.find(
        {"organization": org["name"]}, 
        {"_id": 0}
    ).sort("date", 1))
    
    return {
        **org,
        "members": members,
        "events": events
    }

# Get PR/Promoters for specific organization (for booking)
@app.get("/api/organizations/{organization_name}/promoters")
async def get_organization_promoters(organization_name: str, current_user = Depends(verify_jwt_token)):
    """Get all promoters and capo_promoters for an organization (for client booking selection)"""
    # Get organization promoters
    promoters = list(db.users.find(
        {
            "organization": organization_name,
            "ruolo": {"$in": ["promoter", "capo_promoter"]}
        }
    ).sort("ruolo", 1))
    
    # Filter fields for response
    filtered_promoters = []
    for promoter in promoters:
        filtered_promoters.append({
            "id": promoter["id"],
            "nome": promoter["nome"],
            "cognome": promoter["cognome"],
            "username": promoter["username"],
            "profile_image": promoter.get("profile_image"),
            "ruolo": promoter["ruolo"],
            "biografia": promoter.get("biografia", "")
        })
    
    return filtered_promoters

# NEW APIS - ADDED FOR REQUIREMENTS

@app.put("/api/organizations/{org_id}")
async def update_organization(org_id: str, org_update: OrganizationUpdate, current_user = Depends(verify_jwt_token)):
    """Update organization (assign capo promoter)"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if organization exists
    organization = db.organizations.find_one({"id": org_id})
    if not organization:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    update_data = {}
    
    if org_update.capo_promoter_id:
        # Verify the capo promoter exists
        capo_promoter = db.users.find_one({
            "id": org_update.capo_promoter_id,
            "ruolo": "capo_promoter"
        })
        if not capo_promoter:
            raise HTTPException(status_code=400, detail="Capo promoter non trovato")
        
        # Update capo promoter's organization
        db.users.update_one(
            {"id": org_update.capo_promoter_id},
            {"$set": {"organization": organization["name"]}}
        )
        
        update_data["capo_promoter_id"] = org_update.capo_promoter_id
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        db.organizations.update_one(
            {"id": org_id},
            {"$set": update_data}
        )
    
    return {"message": "Organizzazione aggiornata con successo"}

@app.delete("/api/events/{event_id}")
async def delete_event(event_id: str, current_user = Depends(verify_jwt_token)):
    """Delete event (only clubly_founder can do this)"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Check if event exists
    event = db.events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    # Delete related bookings and chats
    bookings = list(db.bookings.find({"event_id": event_id}))
    for booking in bookings:
        # Delete chat messages
        db.chat_messages.delete_many({"chat_id": {"$in": [chat["id"] for chat in db.chats.find({"booking_id": booking["id"]})]}})
        # Delete chats
        db.chats.delete_many({"booking_id": booking["id"]})
    
    # Delete bookings
    db.bookings.delete_many({"event_id": event_id})
    
    # Delete event
    db.events.delete_one({"id": event_id})
    
    return {"message": "Evento eliminato con successo"}

@app.post("/api/auth/change-password")
async def change_password(password_change: PasswordChange, current_user = Depends(verify_jwt_token)):
    """Change password (for first time login)"""
    user = db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    # Verify current password
    if not verify_password(password_change.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Password attuale non corretta")
    
    # Update password
    new_hashed_password = hash_password(password_change.new_password)
    
    update_data = {
        "password": new_hashed_password,
        "needs_password_change": False,
        "updated_at": datetime.utcnow()
    }
    
    db.users.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    return {"message": "Password cambiata con successo"}

@app.get("/api/organizations/available-capo-promoters")
async def get_available_capo_promoters(current_user = Depends(verify_jwt_token)):
    """Get capo promoters not assigned to any organization"""
    if current_user["ruolo"] != "clubly_founder":
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Get capo promoters without organization or with organization not set
    capo_promoters = list(db.users.find({
        "ruolo": "capo_promoter",
        "$or": [
            {"organization": {"$exists": False}},
            {"organization": ""},
            {"organization": None}
        ]
    }, {"_id": 0, "password": 0}))
    
    return capo_promoters

@app.get("/api/user/notifications/count")
async def get_notifications_count(current_user = Depends(verify_jwt_token)):
    """Get count of unread notifications for user"""
    # Count unread messages in user's chats
    unread_count = 0
    
    if current_user["ruolo"] in ["promoter", "capo_promoter"]:
        # Count messages from clients
        user_chats = list(db.chats.find({"promoter_id": current_user["id"]}))
        for chat in user_chats:
            # Count messages not from this user that are newer than last seen
            unread_messages = db.chat_messages.count_documents({
                "chat_id": chat["id"],
                "sender_id": {"$ne": current_user["id"]},
                "timestamp": {"$gt": chat.get("last_seen_promoter", datetime.utcnow() - timedelta(days=30))}
            })
            unread_count += unread_messages
    else:
        # Count messages from promoters
        user_chats = list(db.chats.find({"client_id": current_user["id"]}))
        for chat in user_chats:
            unread_messages = db.chat_messages.count_documents({
                "chat_id": chat["id"],
                "sender_id": {"$ne": current_user["id"]},
                "timestamp": {"$gt": chat.get("last_seen_client", datetime.utcnow() - timedelta(days=30))}
            })
            unread_count += unread_messages
    
    return {"unread_count": unread_count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)