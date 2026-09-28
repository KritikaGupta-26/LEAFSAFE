# LEAFSAFE
### Leaf Evaluation and AI-based Farming System for Automated Crop Health Assessment and Field Enhancement

An AI-powered smart agriculture system that detects plant diseases from leaf images using Deep Learning and enables intelligent pesticide spraying through an ESP32-based IoT control system.

---

## 🌱 Overview

LEAFSAFE combines Artificial Intelligence, Computer Vision, and IoT technologies to provide an end-to-end smart farming solution. The system analyzes leaf images, identifies plant species, evaluates plant health, detects diseases, and triggers automated spraying recommendations.

The project consists of:

- AI-powered disease detection model
- FastAPI backend for inference
- Next.js frontend dashboard
- ESP32-based IoT control module
- Real-time prediction visualization
- Automated spray decision system

---

## 🚀 Features

### AI-Based Crop Disease Detection
- Plant species classification
- Plant health assessment
- Disease identification
- Confidence score generation
- Top-K prediction support
- Transfer learning with MobileNetV2

### Smart Agriculture Dashboard
- Leaf image upload
- Real-time prediction display
- Disease diagnosis visualization
- Prediction history tracking
- Interactive user interface

### IoT-Based Automated Response
- ESP32 integration
- Automated spray control
- Servo motor actuation
- LCD status display
- LED status indication
- Wi-Fi communication support

### Backend Services
- FastAPI-based REST API
- Image preprocessing pipeline
- Deep learning inference engine
- JSON response generation

---

## 🏗 System Architecture

```text
                ┌─────────────────────┐
                │   Next.js Frontend  │
                │  Upload Leaf Image  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   FastAPI Backend   │
                │  /predict endpoint  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ MobileNetV2 Model   │
                │ Multi-Task Learning │
                └──────────┬──────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Plant Type       Health Type      Disease Type
                           │
                           ▼
                   Spray Decision
                     (0 or 1)
                           │
                           ▼
                ┌─────────────────────┐
                │ Frontend Dashboard  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │      ESP32 Node     │
                └──────────┬──────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
         LCD             LED            Servo
```

---

## 🧠 AI Model

### Model Architecture

- Backbone: MobileNetV2 (Pretrained on ImageNet)
- Framework: TensorFlow / Keras
- Multi-Task Learning Architecture

### Outputs

The model simultaneously predicts:

1. Plant Species
2. Plant Health Status
3. Plant Disease Type

### Training Features

- Transfer Learning
- Data Augmentation
- Label Encoding
- Multi-output Classification
- Confidence-based Prediction

### Inference Features

- Single Image Prediction
- Top-K Predictions
- Confidence Scores
- Healthy Disease Consistency Rule

---

## 📁 Project Structure

```text
LEAFSAFE/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── model/
│
├── model/
│   ├── train.py
│   ├── test.py
│   ├── labels.csv
│   ├── best_model.keras
│   └── training scripts
│
├── ESP32_Code_for_communication/
│   └── esp32 firmware
│
└── README.md
```

---

## ⚙️ Technology Stack

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- Python
- Pillow
- NumPy

### AI/ML
- TensorFlow
- Keras
- MobileNetV2
- Scikit-Learn

### IoT
- ESP32
- Servo Motor
- LCD Display
- LED Indicators

---

## 🔄 Workflow

1. User uploads a leaf image.
2. Frontend sends image to FastAPI backend.
3. Backend preprocesses the image.
4. MobileNetV2 model performs inference.
5. Model predicts:
   - Plant Type
   - Health Status
   - Disease Type
6. Backend generates spray recommendation.
7. Results are displayed on dashboard.
8. ESP32 receives status command.
9. Servo motor performs spraying action if required.
10. LCD and LED display current status.

---

## 📡 API Endpoints

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

### Disease Prediction

```http
POST /predict
```

Request:

```form-data
file: leaf_image.jpg
```

Response:

```json
{
  "plant": "Tomato",
  "health": "Diseased",
  "disease": "Early Blight",
  "spray": 1
}
```

---

## 🔌 ESP32 Communication

### Infected Crop

```http
/infected
```

Actions:

- LED ON
- LCD displays infected status
- Servo rotates for spraying

### Healthy Crop

```http
/notinfected
```

Actions:

- LED OFF
- LCD displays healthy status
- Servo returns to initial position

---

## 💡 Applications

- Smart Farming
- Precision Agriculture
- Automated Crop Monitoring
- Disease Surveillance
- Agricultural IoT Systems
- Sustainable Farming Practices

---

## 🎯 Future Enhancements

- Real-time camera integration
- Drone-based monitoring
- Cloud deployment
- Weather-aware spraying recommendations
- Mobile application support
- Multi-language farmer interface
- Edge AI deployment on embedded devices

---

## 👨‍💻 Team

Developed as a Smart Agriculture and AI-IoT Integration Project focused on improving crop health monitoring and automated disease management.

---

## 📜 License

This project is intended for educational, research, and innovation purposes.

---

## ⭐ Key Highlights

- Multi-Task Deep Learning Model
- MobileNetV2 Transfer Learning
- FastAPI Backend
- Next.js Frontend
- ESP32 IoT Integration
- Automated Spray Decision System
- Real-Time Disease Detection
- Smart Agriculture Solution
