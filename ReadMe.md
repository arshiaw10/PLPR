<div align="center">

# 🚗 AI License Plate Reader
### Automatic Iranian License Plate Recognition System

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=for-the-badge&logo=pytorch&logoColor=white)](https://ultralytics.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-v1.0%20Active-brightgreen?style=for-the-badge)]()

<br/>

> **Computer Engineering Bachelor's Final Project** — A project-based entry into AI with no prior experience, earning a perfect score. 🎓

</div>

---

## 📌 About

This system uses two **YOLOv8** models running in a sequential pipeline:

1. **Plate Detection Model** — Locates the license plate within the image
2. **Character Recognition Model (OCR)** — Reads the letters and digits on the plate

The final output is rendered in a web UI that displays the recognized Iranian license plate in its real visual format.

---

## ✨ Features

- 🔍 **Automatic plate detection** from any input image
- 🔤 **Full Iranian OCR** — supports all Persian letters and digits
- 🖥️ **Clean web interface** with drag & drop upload
- 📊 **Confidence score display** for each recognition
- ⚡ **Real-time processing** powered by FastAPI
- 🎨 **Realistic plate rendering** matching actual Iranian plate design
- 🛡️ **CLAHE preprocessing** for improved accuracy in low-light conditions

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Backend | FastAPI + Uvicorn |
| Detection Models | YOLOv8 (Ultralytics) |
| Image Processing | OpenCV |
| Frontend | HTML + Tailwind CSS + Vanilla JS |
| Font | Vazirmatn |

---

## 📂 Project Structure

```
PLPR/
│
├── models/
│   ├── plate-model.pt       # License plate detection model
│   └── ocr-model.pt         # Character recognition model
│
├── frontend/
│   ├── index.html           # Main web interface
│   ├── app.js               # Frontend logic
│   └── style.css            # Styles
│
├── app.py                   # FastAPI server
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the server

```bash
python app.py
```

The server will be available at `http://localhost:8000`

### 3. Open the UI

Open `frontend/index.html` in your browser, or use a Live Server extension.

---

## 📡 API Reference

### `POST /recognize`

Accepts an image and returns plate recognition data.

**Input:** Image file (`image/jpeg` or `image/png`)

**Sample Response:**

```json
{
  "status": "success",
  "plate_text": "53الف72868",
  "confidence": 0.921,
  "character_count": 8,
  "characters": [
    {
      "char": "الف",
      "raw_class": "A",
      "confidence": 0.95,
      "bbox": [10, 5, 40, 50]
    }
  ],
  "bbox": [120, 80, 520, 200]
}
```

---

## 🧠 Processing Pipeline

```
Input Image
     │
     ▼
[Plate Detection - YOLOv8]
     │  Confidence ≥ 0.55
     ▼
Crop plate region + 8% padding
     │
     ▼
CLAHE preprocessing (contrast enhancement)
     │
     ▼
[Character OCR - YOLOv8]
     │  Confidence ≥ 0.70
     ▼
Sort left-to-right + duplicate filtering
     │
     ▼
Output in Iranian plate format
```

---

## 🗺️ Roadmap

This is **v1.0** — the first working release. As my knowledge and experience in AI continues to grow, this project will be actively updated and expanded.

- [ ] Live video / RTSP stream support
- [ ] Model improvement with larger datasets and fine-tuning
- [ ] Night-time and adverse weather robustness
- [ ] Mobile-friendly PWA interface
- [ ] Recognition history with database storage
- [ ] API authentication and rate limiting
- [ ] Docker support for easy deployment
- [ ] Upgraded model architecture for higher accuracy

---

## 👤 Developer

**[@arshiaw10](https://github.com/arshiaw10)**

Built as a Computer Engineering Bachelor's final project — entering the AI field through hands-on, project-based learning with zero prior experience, and graduating with a perfect grade. 🎓

---

## 📄 License

This project is released under the [MIT License](LICENSE).
