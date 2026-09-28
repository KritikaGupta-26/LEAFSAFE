import io
import os
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import numpy as np
import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# ------------ Settings -------------
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
SPRAY_THRESHOLD = float(os.getenv("SPRAY_THRESHOLD", "0.60"))

# ------------ App ------------------
app = FastAPI(title="SIH • Intelligent Pesticide Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ Schemas -------------

# --- Multi-head prediction schemas ---
class HeadResult(BaseModel):
    label: str
    confidence: float
    top3: list

class PredictResponse(BaseModel):
    plant: HeadResult
    health: HeadResult
    disease: HeadResult
    spray: int
    fileName: str = None
    at: str = None


# ------------ Load Model -------------

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model/plant_health_disease_model_train_2.keras'))
CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model/split_dataset/labels.csv'))
model = tf.keras.models.load_model(MODEL_PATH)

# --- Load label encoders from CSV ---
df = pd.read_csv(CSV_PATH)
plant_encoder = LabelEncoder(); plant_encoder.fit(df['plant'])
health_encoder = LabelEncoder(); health_encoder.fit(df['health'])
disease_encoder = LabelEncoder(); disease_encoder.fit(df['disease'])
plant_classes = plant_encoder.classes_
health_classes = health_encoder.classes_
disease_classes = disease_encoder.classes_

# ------------ Utils -------------
def preprocess_image(image: Image.Image, target_size=(224, 224)) -> np.ndarray:
    """
    Preprocess the image for model prediction.
    - Resize, convert to array, scale, expand dims.
    """
    image = image.resize(target_size)
    arr = np.array(image) / 255.0
    if arr.shape[-1] == 4:
        arr = arr[..., :3]  # Remove alpha if present
    arr = np.expand_dims(arr, axis=0)
    return arr

# ------------ Routes -------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)) -> PredictResponse:
    """
    Contract:
      Request: multipart/form-data with 'file' (image)
      Response: { label, confidence, spray }
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Read bytes & open with Pillow
    try:
        raw = await file.read()
        image = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # --- Use Keras model for multi-head prediction ---
    arr = preprocess_image(image)
    preds = model.predict(arr)
    p_plant, p_health, p_disease = preds  # each is shape (1, num_classes)

    def topk_probs(probs, classes, k=3):
        probs = probs.flatten()
        idxs = probs.argsort()[::-1][:k]
        return [(str(classes[i]), float(probs[i])) for i in idxs]

    def argmax_label(probs, classes):
        i = int(np.argmax(probs, axis=1)[0])
        return str(classes[i]), i, float(np.max(probs))

    plant_label, _, plant_conf = argmax_label(p_plant, plant_classes)
    health_label, _, health_conf = argmax_label(p_health, health_classes)
    disease_label, _, disease_conf = argmax_label(p_disease, disease_classes)

    # Top-3 for each head
    plant_top3 = topk_probs(p_plant, plant_classes, 3)
    health_top3 = topk_probs(p_health, health_classes, 3)
    disease_top3 = topk_probs(p_disease, disease_classes, 3)

    # Decision policy for spray: if health is 'Diseased' and confidence > threshold
    spray = 1 if (health_label == 'Diseased' and health_conf >= SPRAY_THRESHOLD) else 0

    # Compose response
    resp = PredictResponse(
        plant=HeadResult(label=plant_label, confidence=plant_conf, top3=plant_top3),
        health=HeadResult(label=health_label, confidence=health_conf, top3=health_top3),
        disease=HeadResult(label=disease_label, confidence=disease_conf, top3=disease_top3),
        spray=spray,
        fileName=file.filename,
        at=datetime.utcnow().isoformat()
    )

    # --- ESP32 Trigger ---
    import requests
    ESP32_IP = "http://192.168.3.114"  # Use your ESP32's IP
    try:
        if spray == 1:
            requests.get(f"{ESP32_IP}/infected", timeout=2)
        else:
            requests.get(f"{ESP32_IP}/notinfected", timeout=2)
    except Exception as e:
        print("Could not contact ESP32:", e)
    return resp