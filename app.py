from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Thay thế bằng Access Token của bạn
ZALO_ACCESS_TOKEN = "YOUR_ZALO_ACCESS_TOKEN"
FB_ACCESS_TOKEN = "YOUR_FB_PAGE_ACCESS_TOKEN"
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"

# Dữ liệu kiến thức Tin học
data_knowledge = {
    "lớp 10": "Tin học 10 gồm các kiến thức về máy tính, hệ điều hành và lập trình Python.",
    "lớp 11": "Tin học 11 tập trung vào lập trình với Python, thuật toán và cấu trúc dữ liệu.",
    "lớp 12": "Tin học 12 liên quan đến cơ sở dữ liệu, SQL và ứng dụng CNTT."
}

# Hàm phản hồi dựa vào tin nhắn
def get_reply(message):
    for key in data_knowledge:
        if key in message.lower():
            return data_knowledge[key]
    return "Bạn cần học về lớp nào? (10, 11, 12)"

# Xử lý tin nhắn từ Zalo
@app.route("/zalo_webhook", methods=["POST"])
def zalo_webhook():
    data = request.json
    if "message" in data:
        user_id = data["sender"]["id"]
        message_text = data["message"]["text"]
        reply_text = get_reply(message_text)
        send_zalo_message(user_id, reply_text)
    return jsonify({"status": "success"}), 200

def send_zalo_message(user_id, message):
    url = "https://openapi.zalo.me/v2.0/oa/message"
    headers = {"Content-Type": "application/json", "access_token": ZALO_ACCESS_TOKEN}
    payload = {"recipient": {"user_id": user_id}, "message": {"text": message}}
    requests.post(url, json=payload, headers=headers)

# Xử lý tin nhắn từ Messenger
@app.route("/messenger_webhook", methods=["GET", "POST"])
def messenger_webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token không hợp lệ", 403

    data = request.json
    if "entry" in data:
        for entry in data["entry"]:
            for messaging in entry.get("messaging", []):
                sender_id = messaging["sender"]["id"]
                if "message" in messaging:
                    message_text = messaging["message"].get("text", "")
                    reply_text = get_reply(message_text)
                    send_facebook_message(sender_id, reply_text)
    return jsonify({"status": "success"}), 200

def send_facebook_message(user_id, message):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={FB_ACCESS_TOKEN}"
    payload = {"recipient": {"id": user_id}, "message": {"text": message}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")