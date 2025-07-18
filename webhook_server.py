from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    print("📞 Webhook recibido:", payload)
    # Aquí puedes guardar en BD, enviar a otro servicio, etc.
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=8000, reload=True)
