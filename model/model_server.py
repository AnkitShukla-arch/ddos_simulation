from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from detector import detect_ip

app = FastAPI()

class IP(BaseModel):
    ip: str

@app.post("/predict")
def predict(ip: IP):
    malicious = detect_ip(ip.ip)
    return {
        "ip": ip.ip,
        "malicious": malicious,
        "action": "block" if malicious else "allow"
    }

if __name__ == "__main__":
    uvicorn.run("model_server:app", host="0.0.0.0", port=8000, reload=True)

