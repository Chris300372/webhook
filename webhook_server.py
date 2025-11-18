from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import os

app = FastAPI()

# 🔐 VARIABLES
VERIFY_TOKEN = "mi_token_secreto"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = "103065052613628"
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return JSONResponse(content=int(challenge), status_code=200)
    else:
        return JSONResponse(content={"error": "Token inválido"}, status_code=403)


@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("📩 Webhook recibido:", data)

    try:
        # 🔍 Extraer texto y número
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]
        text = message["text"]["body"]
        print(f"📨 Mensaje de {sender}: {text}")

        # 🤖 Enviar a ChatGPT
        ai_answer = ask_chatgpt(text)

        # 📤 Enviar respuesta por WhatsApp
        send_whatsapp_message(sender, ai_answer)

    except Exception as e:
        print("⚠️ Error procesando mensaje:", e)

    return {"status": "ok"}


# ====== 📌 Función para enviar el mensaje a ChatGPT ======
def ask_chatgpt(user_msg):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Eres un asistente para una empresa que responde preguntas de clientes."},
            {"role": "user", "content": user_msg}
        ]
    }

    resp = requests.post(url, headers=headers, json=body)

    print("🔍 RESPUESTA CHATGPT:", resp.text)  # 👈 agrega esto

    data = resp.json()

    if "choices" not in data:
        raise Exception(f"Error de ChatGPT: {data}")

    return data["choices"][0]["message"]["content"]


# ====== 📌 Función para responder al cliente en WhatsApp ======
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }

    requests.post(url, headers=headers, json=body)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=8000, reload=True)






