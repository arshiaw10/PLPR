from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from ultralytics import YOLO
import json

# ─── تنظیمات ────────────────────────────────────────────────────────────────────
PLATE_MODEL_PATH = "models/plate-model.pt"
CHAR_MODEL_PATH = "models/ocr-model.pt"

CLASS_MAP = {
    '.': '?',
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
    '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
    'A': 'الف', 'AIN': 'ع', 'B': 'ب', 'D': 'د',
    'Disabled': 'معلول', 'F': 'ف', 'G': 'گ', 'GH': 'ق',
    'H': 'ه', 'J': 'ج', 'K': 'ک', 'L': 'ل', 'M': 'م', 'N': 'ن',
    'P': 'پ', 'S': 'س', 'SAD': 'ص', 'SH': 'ش', 'T': 'ت',
    'TA': 'ظ', 'V': 'و', 'Y': 'ی', 'Z': 'ز',
}

# ─── بارگذاری مدل‌ها ────────────────────────────────────────────────────────────
print("🔄 بارگذاری مدل‌ها...")
plate_model = YOLO(PLATE_MODEL_PATH)
char_model = YOLO(CHAR_MODEL_PATH)
print("✅ مدل‌ها آماده‌اند")

# ─── اپلیکیشن ────────────────────────────────────────────────────────────────────
app = FastAPI(title="پلاک‌خوان هوش مصنوعی", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_image(img_bgr: np.ndarray) -> dict:
    # تشخیص پلاک
    plate_results = plate_model(img_bgr, verbose=False)[0]
    plates = [b for b in plate_results.boxes if float(b.conf) >= 0.55]

    if not plates:
        return {"status": "plate_not_found"}

    plate_box = max(plates, key=lambda b: float(b.conf))
    x1, y1, x2, y2 = map(int, plate_box.xyxy[0])
    plate_conf = float(plate_box.conf)

    # پدینگ
    pad_x = int((x2 - x1) * 0.08)
    pad_y = int((y2 - y1) * 0.08)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(img_bgr.shape[1], x2 + pad_x)
    y2 = min(img_bgr.shape[0], y2 + pad_y)

    # کراپ + CLAHE
    crop = img_bgr[y1:y2, x1:x2].copy()
    if crop.size == 0:
        return {"status": "invalid_crop"}

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    crop_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    # تشخیص کاراکترها - فقط کاراکترهای با اعتماد ≥ 0.7 پذیرفته می‌شوند
    char_results = char_model(crop_bgr, verbose=False)[0]
    chars = []
    for box in char_results.boxes:
        conf = float(box.conf)
        if conf < 0.7:  # ✅ آستانه جدید
            continue
        cls_name = char_results.names[int(box.cls)]
        x1c, y1c, x2c, y2c = map(int, box.xyxy[0])
        cx = (x1c + x2c) / 2
        chars.append({
            'raw_class': cls_name,
            'mapped_char': CLASS_MAP.get(cls_name, '?'),
            'confidence': conf,
            'center_x': cx,
            'bbox': [x1c, y1c, x2c, y2c]
        })

    if not chars:
        return {"status": "no_characters"}

    # مرتب‌سازی از چپ به راست (ترتیب فیزیکی در تصویر)
    chars.sort(key=lambda c: c['center_x'])

    # فیلتر تکراری
    filtered = []
    last_x = -1e9
    min_dist = crop.shape[1] * 0.07
    for c in chars:
        if c['center_x'] - last_x > min_dist:
            filtered.append(c)
            last_x = c['center_x']

    # ساخت آرایه کاراکترها برای فرانت‌اند
    characters_array = []
    for c in filtered:
        characters_array.append({
            "char": c['mapped_char'],
            "raw_class": c['raw_class'],
            "confidence": round(c['confidence'], 3),
            "bbox": c['bbox'],
            "position": "left_to_right"
        })

    # ساخت متن نهایی
    physical_order = ''.join([c['mapped_char'] for c in filtered])
    persian_order = physical_order[::-1]

    return {
        "status": "success",
        "plate_text": persian_order,
        "physical_order": physical_order,
        "confidence": round(plate_conf, 3),
        "bbox": [x1, y1, x2, y2],
        "characters": characters_array,
        "character_count": len(filtered)
    }

# ─── اندپوینت اصلی ──────────────────────────────────────────────────────────────
@app.post("/recognize")
async def recognize_plate(file: UploadFile = File(...)):
    # بررسی نوع فایل
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        return Response(
            content=json.dumps(
                {"status": "error", "message": "فقط فرمت‌های JPG/PNG پشتیبانی می‌شوند"},
                ensure_ascii=False
            ),
            media_type="application/json",
            status_code=400
        )

    try:
        # خواندن تصویر
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return Response(
                content=json.dumps(
                    {"status": "error", "message": "تصویر نامعتبر است"},
                    ensure_ascii=False
                ),
                media_type="application/json",
                status_code=400
            )

        # پردازش
        result = process_image(img)
        result["filename"] = file.filename

        # خروجی با فارسی صحیح
        return Response(
            content=json.dumps(result, ensure_ascii=False, indent=2),
            media_type="application/json"
        )

    except Exception as e:
        return Response(
            content=json.dumps(
                {"status": "error", "message": str(e)},
                ensure_ascii=False
            ),
            media_type="application/json",
            status_code=500
        )


@app.get("/")
async def root():
    return {
        "message": "پلاک‌خوان هوش مصنوعی",
        "version": "1.0",
        "endpoint": "/recognize (POST with image file)"
    }


# ─── اجرا ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    print("\n🚀 سرور در حال اجراست: http://localhost:8000")
    print("📸 تست در مرورگر: http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    