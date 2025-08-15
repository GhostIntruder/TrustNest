import requests
import json
from flask import Flask, request
from flask_cors import CORS  # Importing flask_cors to handle CORS issues
from googletrans import Translator
import asyncio


translator = Translator()

# Initialize the Flask Application
app = Flask(__name__)

# Enable CORS for all domains (allow React to make requests to this backend)
CORS(app)

# WhatsApp Cloud API credentials
WHATSAPP_PHONE_NUMBER_ID = "739423979255264"  # Replace with your real Phone Number ID
WHATSAPP_ACCESS_TOKEN = "EAAIZCLeIgByQBPHZBhjD875dWo7jvhiRy3fVhj5vGFxzX7DnzuYyiNiebmqfSrawnUyjZC3PH2ql3LmjHMbx42q5YpDUdwUsH8gOzYMJIYmG0TvFm1BwY8b1X90ZBsPBGv6c38HCYCWExTVg6fDz1OL0oGbblUVrbGDbKRMhedwqLZBzQnyZAqjd4GioX22gMC6AygpRoVENVQWy9uRDmLOIG4XVpW2Ppz0PbrfsCxSNoP8gyHpTCyjWjiJokfjgZDZD"
VERIFY_TOKEN = "trustie_webhook_verify"

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


    
if __name__ == "__main__":
    app.run(port=5000, debug=True)