# TrustNest

**AI-powered real estate fraud detection and land verification assistant for Nigeria**

TrustNest helps Nigerians avoid property scams by providing instant document verification, legal guidance, and fraud education — in five languages.

---

## The Problem

Property fraud is one of the most common financial crimes in Nigeria. Buyers lose life savings to fake land documents, double-sold properties, and impersonated owners. Most victims do not know what documents to ask for, what red flags to watch out for, or what their legal rights are — especially outside major cities and among non-English speakers.

---

## What TrustNest Does

TrustNest is a Flask-based web application with an integrated AI chatbot powered by Google Gemini. It provides:

**Document Verification**
- Upload land documents (PDF, DOCX) for instant AI-assisted analysis
- Verifies Survey Plans against 8 key authenticity markers including surveyor credentials, government approval stamps, boundary coordinates, and plan numbers
- Verifies Land Title documents (Certificate of Occupancy, Governor's Consent, Deed of Assignment) against 7 authenticity markers including government authority, registration details, and official seals
- Returns a verification score, status (Verified / Caution / Flagged), identified red flags, and specific recommendations
- Stores document hash and verification history per user

**AI Chat Assistant (TrustNest Assistant)**
- Answers questions about Nigerian land law, property rights, buyer and tenant rights, and fraud prevention
- Built on a structured knowledge base of Q&A pairs covering 15 core topics
- Falls back to Gemini 2.0 Flash for questions outside the knowledge base
- Uses fuzzy matching to identify relevant answers even when questions are phrased differently

**Multilingual Support**
- English
- Yoruba
- Igbo
- Hausa
- Nigerian Pidgin

**WhatsApp Integration**
- Webhook endpoint for WhatsApp Cloud API
- Users can interact with TrustNest directly via WhatsApp
- Responds in all five languages based on keyword detection

**User Authentication**
- Secure signup and login with bcrypt password hashing
- JWT-based authentication with 1-hour token expiry
- Password reset via email with 15-minute token validity
- Rate limiting on sensitive endpoints

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, Flask |
| AI Model | Google Gemini 2.0 Flash |
| Database | SQLAlchemy with Flask-Migrate |
| Authentication | Flask-JWT-Extended, Flask-Bcrypt |
| Document Processing | PyPDF2, python-docx |
| Translation | googletrans |
| WhatsApp | Meta WhatsApp Cloud API |
| Rate Limiting | Flask-Limiter |
| Email | Flask-Mail |

---

## Project Structure

```
TrustNest/
├── secureNest_backend.py    # Main Flask application, API routes, document verification logic
├── gemini_setup.py          # Gemini AI configuration, knowledge base, chat logic
├── models.py                # User and Document database models
├── database.py              # Database initialisation
├── requirements.txt         # Dependencies
├── migrations/              # Database migration files
└── .gitignore
```

---

## Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | User registration |
| POST | `/login` | User authentication |
| POST | `/forgot-password` | Password reset request |
| POST | `/upload-and-verify-survey` | Upload and verify a survey plan |
| POST | `/upload-land-title` | Upload and verify a land title document |
| POST | `/chat` | AI chatbot query |
| GET | `/api/user-documents/<id>` | Retrieve user document history |
| POST | `/webhook` | WhatsApp Cloud API webhook |

---

## Document Verification Logic

**Survey Plan Verification** checks for:
- Document type indicators
- Licensed surveyor details
- Property identification (lot, block, plan number)
- Boundary coordinates
- Scale information
- Government approval stamps
- Date of survey
- Boundary markers

**Land Title Verification** checks for:
- Document type (C of O, Governor's Consent, Deed of Assignment)
- Issuing government authority
- Property description
- Survey details
- Owner/grantee details
- Registration and file numbers
- Official signatures and seals

Scores above 85% (survey) or 75% (land title) return **Verified** status. Scores below threshold return **Caution** or **Flagged** with specific recommendations.

---

## Knowledge Base

The chatbot knowledge base covers 15 topics in four languages (English, Yoruba, Igbo, Hausa) including:

- What land verification is and why it matters
- Documents to request before purchasing land
- How to identify government-acquired land
- Common fraud tactics (fake documents, double-selling, impersonation)
- Tenant and landlord rights under Nigerian law
- Dispute resolution options
- The role of surveyors
- Women's land ownership rights in Nigeria

---

## Planned Features

- WhatsApp chatbot expansion with full conversational flow
- Fraud agent registry — searchable database of reported fraudulent agents and landlords
- Rental fraud detection module
- Integration with state Lands Registry APIs for real-time verification
- Expanded knowledge base covering all 36 Nigerian states

---

## Background

TrustNest was built as an MVP during a competitive AI hackathon. The project was motivated by the scale of real estate fraud affecting everyday Nigerians — particularly those buying land for the first time with limited legal knowledge and no access to professional verification services. The multilingual design was a deliberate choice to reach buyers across Nigeria's linguistic diversity, not just English speakers in urban centres.

---

## Setup

```bash
# Clone the repository
git clone https://github.com/GhostIntruder/TrustNest.git
cd TrustNest

# Install dependencies
pip install -r requirements.txt

# Create .env file with the following variables
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_id
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
VERIFY_TOKEN=your_verify_token
MAIL_SERVER=your_mail_server
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_email_password

# Run database migrations
flask db upgrade

# Start the application
python secureNest_backend.py
```

---

## Contributors

- Omonivie Cynthia Jatto
- Aisha Bello-Abubakar
- Bella Etuk

---

## License

MIT License
