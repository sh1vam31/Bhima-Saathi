from fastapi import FastAPI
from app.webhooks import whatsapp, razorpay

app = FastAPI(title="Bima Saathi WhatsApp Assistant")

app.include_router(whatsapp.router)
app.include_router(razorpay.router)

@app.get("/")
def root():
    return {"message": "Bima Saathi AI is running perfectly! Connect this URL to Twilio."}

@app.get("/health")
def health_check():
    return {"status": "ok"}
