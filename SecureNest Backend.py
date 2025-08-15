import requests
import json
from flask import Flask, request

app = Flask(__name__)

# WhatsApp Cloud API credentials
WHATSAPP_PHONE_NUMBER_ID = "739423979255264"  # Replace with your real Phone Number ID
WHATSAPP_ACCESS_TOKEN = "EAAIZCLeIgByQBPHZBhjD875dWo7jvhiRy3fVhj5vGFxzX7DnzuYyiNiebmqfSrawnUyjZC3PH2ql3LmjHMbx42q5YpDUdwUsH8gOzYMJIYmG0TvFm1BwY8b1X90ZBsPBGv6c38HCYCWExTVg6fDz1OL0oGbblUVrbGDbKRMhedwqLZBzQnyZAqjd4GioX22gMC6AygpRoVENVQWy9uRDmLOIG4XVpW2Ppz0PbrfsCxSNoP8gyHpTCyjWjiJokfjgZDZD"
VERIFY_TOKEN = "trustie_webhook_verify"

# Pre-set bot replies
BOT_RESPONSES = {
    "verify documents": {
        "en": "Property Verification! Upload your documents for instant analysis.",
        "pidgin": "Bring di paper make we check am sharp sharp for you."
    },
    "report scam": {
        "en": "To report a scam, please provide details via WhatsApp at +234 906 576 0546 or contact support for business.",
        "pidgin": "If person don scam you, yarn us di tori for WhatsApp +234 906 576 0546 or hala support."
    },
    "know your rights": {
        "en": "I can help with Nigeria property laws. Ask me about buyer/renter rights, and I'll guide you!",
        "pidgin": "I sabi Nigerian property law well well. Ask me about buyer or tenant rights make I show you road."
    },
    "contact support": {
        "en": "Contact our Support team at support@trustnet.com or call +234 906 576 0546 during 8 AM - 6 PM, Monday to Saturday.",
        "pidgin": "Call our Support people for support@trustnet.com or dial +234 906 576 0546 between 8 morning and 6 evening, Monday to Saturday."
    }
}

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

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

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
                            # Send both English and Pidgin reply
                            send_whatsapp_message(sender, replies["en"])
                            send_whatsapp_message(sender, replies["pidgin"])
                            break
                    else:
                        send_whatsapp_message(sender, "I be Trustie. You fit ask me to Verify Documents, Report Scam, Know Your Rights, or Contact Support.")

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
