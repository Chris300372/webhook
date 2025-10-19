from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# ✅ GET para verificación de Meta (WhatsApp)
@app.get("/webhook")
async def verify_webhook(request: Request):
    # Meta envía estos parámetros en la URL
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    VERIFY_TOKEN = "mi_token_secreto"  # 🔒 usa el mismo token configurado en Meta

    # Meta requiere que devuelvas el 'challenge' si el token coincide
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook de Meta verificado correctamente.")
        return JSONResponse(content=int(challenge), status_code=200)
    else:
        print("❌ Verificación fallida. Parámetros recibidos:", params)
        return JSONResponse(content={"error": "Token inválido"}, status_code=403)

# ✅ POST para recibir los mensajes o eventos (Retell / WhatsApp / otros)
@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        payload = await request.json()
        print("📞 Webhook recibido:", payload)
        # Aquí puedes guardar en BD, procesar eventos, responder, etc.
        return {"status": "ok"}
    except Exception as e:
        print("❌ Error procesando webhook:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=8000, reload=True)
