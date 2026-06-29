import requests
from fastapi import FastAPI

app = FastAPI()


@app.get("/proxy")
def proxy(url: str):
    # Intentional fixture: attacker-controlled URL reaches server-side request.
    response = requests.get(url, timeout=5, verify=False)
    return {"status": response.status_code, "body": response.text[:200]}
