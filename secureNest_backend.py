import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS  # Importing flask_cors to handle CORS issues
from googletrans import Translator
import asyncio
from database import db, migrate
from models import User, Document
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
import re
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from flask_jwt_extended import decode_token




load_dotenv()


translator = Translator()

# Initialize the Flassk Application
app = Flask(__name__)

# Enable CORS for all domains (allow React to make requests to this backend)
CORS(app)



# Configure database (SQLite for now)
app.config["SQLALCHEMY_DATABASE_URI"] =  os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Config
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# Configure JWT for authentication
bcrypt = Bcrypt(app) 
jwt = JWTManager(app)
mail = Mail(app)

# Initialize database with app
db.init_app(app)
migrate.init_app(app, db)

# WhatsApp Cloud API credentials
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Configure Flask-Mail for sending emails
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

# Rate limiter (based on client IP)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]  # global fallback
)

# --- Validation Helpers ---
def is_valid_email(email):
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", email)

def is_strong_password(password):
    return (
        len(password) >= 8
        and any(c.isupper() for c in password)
        and any(c.islower() for c in password)
        and any(c.isdigit() for c in password)
        and any(c in "!@#$%^&*()-_+=" for c in password)
    )

def is_valid_name(name):
    # Allow only alphabets (first and last names), no emojis, no digits
    return re.match(r"^[A-Za-z]+$", name)


# Pre-set bot replies in multiple languages
BOT_RESPONSES = {
    "verify documents": {
        "en": "Property Verification! Upload your documents for instant analysis.",
        "pidgin": "Bring di paper make we check am sharp sharp for you.",
        "igbo": "Nyochaa ihe osise ụlọ gị! Gị nwere ike nyochaa akwụkwọ gị ozugbo.",
        "yoruba": "Iṣeduro Iwe-ọwọ! Gbe awọn iwe rẹ silẹ fun itupalẹ lẹsẹkẹsẹ.",
        "hausa": "Binciken Dukiya! Aika da takardunku domin duba nan take."
    },
    "report scam": {
        "en": "To report a scam, please provide details via WhatsApp at +234 906 576 0546 or contact support for business.",
        "pidgin": "If person don scam you, yarn us di tori for WhatsApp +234 906 576 0546 or hala support.",
        "igbo": "Iwepụta egwu, biko nye anyị nkọwa site na WhatsApp +234 906 576 0546 ma ọ bụ kpọtụrụ nkwado maka azụmahịa.",
        "yoruba": "Lati ṣe iroyin itanjẹ, jọwọ pese awọn alaye nipasẹ WhatsApp ni +234 906 576 0546 tabi kan si atilẹyin fun iṣowo.",
        "hausa": "Don bayar da rahoton zamba, don Allah samar da cikakkun bayanai ta WhatsApp a +234 906 576 0546 ko tuntuɓi goyon baya don kasuwanci."
    },
    "know your rights": {
        "en": "I can help with Nigeria property laws. Ask me about buyer/renter rights, and I'll guide you!",
        "pidgin": "I sabi Nigerian property law well well. Ask me about buyer or tenant rights make I show you road.",
        "igbo": "Enyemaka na iwu ụlọ Nigeria. Jụọ m gbasara ikike ndị na-azụ ahịa/ndị na-azụ ụlọ, m ga-eduga gị!",
        "yoruba": "Mo le ran ọ lọwọ pẹlu ofin ohun-ini Nigeria. Beere lọwọ mi nipa awọn ẹtọ olura/tabi onílé, emi yoo tọ ọ!",
        "hausa": "Zan iya taimaka muku da dokokin kadarori na Najeriya. Tambayi ni game da hakkin mai saye/matar haya, zan jagorance ku!"
    },
    "contact support": {
        "en": "Contact our Support team at support@trustnet.com or call +234 906 576 0546 during 8 AM - 6 PM, Monday to Saturday.",
        "pidgin": "Call our Support people for support@trustnet.com or dial +234 906 576 0546 between 8 morning and 6 evening, Monday to Saturday.",
        "igbo": "Kpọtụrụ otu nkwado anyị na support@trustnet.com ma ọ bụ kpọọ +234 906 576 0546 n'oge 8 AM - 6 PM, Mọnde ruo Satọde.",
        "yoruba": "Pe ẹgbẹ Atilẹyin wa ni support@trustnet.com tabi pe +234 906 576 0546 laarin 8 owurọ si 6 osan, Monday si Saturday.",
        "hausa": "Tuntuɓi ƙungiyar tallafinmu a support@trustnet.com ko kiran +234 906 576 0546 daga 8 na safe zuwa 6 na yamma, Litinin zuwa Asabar."
    }
}

# Route for the root endpoint
@app.route("/")
def home():
    return "Backend is running!"

# Function to send WhatsApp message via API
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, data=json.dumps(payload))

# Webhook verification endpoint (for WhatsApp integration)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

# Webhook endpoint to handle incoming WhatsApp messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming message:", json.dumps(data, indent=2))

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    sender = message["from"]
                    text = message.get("text", {}).get("body", "").lower()

                    # Match keywords to responses
                    for keyword, replies in BOT_RESPONSES.items():
                        if keyword in text:
                            # Send replies in multiple languages
                            send_whatsapp_message(sender, replies["en"])
                            send_whatsapp_message(sender, replies["pidgin"])
                            send_whatsapp_message(sender, replies["igbo"])
                            send_whatsapp_message(sender, replies["yoruba"])
                            send_whatsapp_message(sender, replies["hausa"])
                            break
                    else:
                        send_whatsapp_message(sender, "I be Trustie. You fit ask me to Verify Documents, Report Scam, Know Your Rights, or Contact Support.")

    return "EVENT_RECEIVED", 200

# API Route for React to send data (document and language)
@app.route("/api/send", methods=["POST"])
def send_data():
    data = request.get_json()
    document = data.get("documentData")
    language = data.get("language", "en")
    
    # Here you can process the document or trigger WhatsApp messages
    recipient = data.get("phone")  # phone number from React
    if recipient:
        message = f"Your request is received! Language selected: {language}"
        send_whatsapp_message(recipient, message)

    return {"status": "success", "message": "Data received and processed"}, 200


# API Route for translation
@app.route("/api/translate", methods=["POST"])
async def translate_text():
    data = request.get_json()
    texts = data.get("texts")  # This should be a list
    target_lang = data.get("target_lang", "en")

    if not texts or not isinstance(texts, list):
        return {"success": False, "error": "No valid texts provided"}, 400

    try:
        translated_results = []
        for t in texts:
            translated = await translator.translate(t, dest=target_lang)
            translated_results.append({
                "original_text": t,
                "translated_text": translated.text,
                "source_lang": translated.src,
                "target_lang": target_lang
            })

        return {
            "success": True,
            "results": translated_results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


# API Route for user registration
# ---------------- SIGN UP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    # Required fields
    if not data.get("firstName") or not data.get("lastName") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "All fields are required"}), 400

    # Validate names
    if not is_valid_name(data["firstName"]):
        return jsonify({"error": "Invalid first name"}), 400
    if not is_valid_name(data["lastName"]):
        return jsonify({"error": "Invalid last name"}), 400

    # Validate email
    if not is_valid_email(data["email"]):
        return jsonify({"error": "Invalid email format"}), 400

    # Check if email exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    # Validate password strength
    if not is_strong_password(data["password"]):
        return jsonify({"error": "Password must be 8+ chars with upper, lower, digit, and special char"}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    # Save user
    new_user = User(
        first_name=data["firstName"],
        last_name=data["lastName"],
        email=data["email"],
        password=hashed_password,
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
    return jsonify({"token": access_token, "user": {"firstName": user.first_name, "lastName": user.last_name, "email": user.email}})

#---- forget password ----
@app.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per hour")  # Max 5 requests per hour per IP
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    if not email or not is_valid_email(email):
        return jsonify({"error": "Valid email required"}), 400

    user = User.query.filter_by(email=email).first()

    # 🛡 Do not reveal whether email exists
    if not user:
        return jsonify({"message": "If the email exists, a reset link has been sent."}), 200

    # Create reset token valid for 15 minutes
    reset_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(minutes=15),
        additional_claims={"reset": True}
    )

    reset_url = f"http://localhost:3000/reset-password/{reset_token}"

    msg = Message("Password Reset Request",
                  sender=app.config["MAIL_USERNAME"],
                  recipients=[email])
    msg.body = f"Click the link to reset your password: {reset_url}"
    mail.send(msg)

    return jsonify({"message": "If the email exists, a reset link has been sent."}), 200



# ---------------- DOCUMENT UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload_document():
    data = request.get_json()
    if not data.get("filename") or not data.get("file_hash") or not data.get("user_id"):
        return jsonify({"error": "Filename, file hash, and user ID are required"}), 400
    if not User.query.get(data["user_id"]):
        return jsonify({"error": "User not found"}), 404
    if Document.query.filter_by(file_hash=data["file_hash"]).first():
        return jsonify({"error": "Document with this hash already exists"}), 400
    new_document = Document(
        filename=data["filename"],
        file_hash=data["file_hash"],
        user_id=data["user_id"],
        originality_status="Pending"
    )
    db.session.add(new_document)
    db.session.commit()
    return jsonify({"message": "Document uploaded successfully"}), 201


    
if __name__ == "__main__":
    app.run(port=5000, debug=True)