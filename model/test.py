import os
import argparse
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# -----------------------------
# GPU safety: don't pre-allocate all VRAM
# -----------------------------
gpus = tf.config.list_physical_devices("GPU")
if gpus:
    for g in gpus:
        try:
            tf.config.experimental.set_memory_growth(g, True)
        except Exception:
            pass

# -----------------------------
# Args
# -----------------------------
parser = argparse.ArgumentParser(description="Test multi-output plant/health/disease model on a single image.")
parser.add_argument("--model", default=r"D:\sih\model\plant_health_disease_model_train_3.keras", help="Path to .keras model file")
parser.add_argument("--image", required=False, default=r"D:\sih\model\split_dataset\test\Apple_Healthy\_0_7131.png", help="Path to input image")
parser.add_argument("--csv",   default=r"D:\sih\model\split_dataset\labels.csv", help="Training CSV (to rebuild encoders)")
parser.add_argument("--img_size", type=int, nargs=2, default=[224, 224], help="H W image size")
parser.add_argument("--tta", action="store_true", help="Enable test-time augmentation (averages a few flips)")
parser.add_argument("--consistency_rule", action="store_true",
                    help="If health=Healthy, set disease=Healthy in post-processing")
parser.add_argument("--topk", type=int, default=3, help="Top-K to display per head")
args = parser.parse_args()

MODEL_PATH = args.model
CSV_PATH   = args.csv
IMG_PATH   = args.image
IMG_SIZE   = tuple(args.img_size)
TOPK       = max(1, args.topk)

# -----------------------------
# Load model
# -----------------------------
# If you used label_smoothing, no custom objects are needed for inference.
model = load_model(MODEL_PATH)
print(f"✅ Loaded model: {MODEL_PATH}")

# -----------------------------
# Build encoders from training CSV (must match training set)
# -----------------------------
df = pd.read_csv(CSV_PATH)

plant_encoder = LabelEncoder()
health_encoder = LabelEncoder()
disease_encoder = LabelEncoder()

df["plant_enc"]   = plant_encoder.fit_transform(df["plant"])
df["health_enc"]  = health_encoder.fit_transform(df["health"])
df["disease_enc"] = disease_encoder.fit_transform(df["disease"])

plant_classes   = plant_encoder.classes_
health_classes  = health_encoder.classes_
disease_classes = disease_encoder.classes_

# Helpful indices
HEALTHY_IDX = None
if "Healthy" in list(health_classes):
    HEALTHY_IDX = int(np.where(health_classes == "Healthy")[0][0])

# -----------------------------
# Image preprocessing (robust to JPG/PNG)
# -----------------------------
def load_and_preprocess(path, img_size=IMG_SIZE):
    raw = tf.io.read_file(path)
    img = tf.io.decode_image(raw, channels=3, expand_animations=False)  # jpg/png
    img = tf.image.resize(img, img_size)
    img = tf.cast(img, tf.float32) / 255.0
    return img[None, ...]  # add batch dim

x = load_and_preprocess(IMG_PATH, IMG_SIZE)

# -----------------------------
# Optional Test-Time Augmentation (TTA)
# -----------------------------
def predict_with_tta(model, x, repeats=4):
    preds_sum = None
    for _ in range(repeats):
        aug = tf.image.random_flip_left_right(x)
        aug = tf.image.random_flip_up_down(aug)
        p = model.predict(aug, verbose=0)
        if preds_sum is None:
            preds_sum = [np.array(pi, dtype=np.float64) for pi in p]
        else:
            preds_sum = [a + b for a, b in zip(preds_sum, p)]
    return [a / repeats for a in preds_sum]

if args.tta:
    preds = predict_with_tta(model, x, repeats=4)
    print("🔁 Using TTA (4 repeats)")
else:
    preds = model.predict(x, verbose=0)

p_plant, p_health, p_disease = preds  # each is shape (1, num_classes)

# -----------------------------
# Utility: pretty print top-k
# -----------------------------
def topk_probs(probs, classes, k=3):
    probs = probs.flatten()
    idxs = probs.argsort()[::-1][:k]
    return [(classes[i], float(probs[i])) for i in idxs]

def argmax_label(probs, classes):
    i = int(np.argmax(probs, axis=1)[0])
    return classes[i], i, float(np.max(probs))

# Raw predictions
plant_label,  plant_idx,  plant_conf  = argmax_label(p_plant, plant_classes)
health_label, health_idx, health_conf = argmax_label(p_health, health_classes)
disease_label, disease_idx, disease_conf = argmax_label(p_disease, disease_classes)

# -----------------------------
# Optional consistency rule
# If health says "Healthy", force disease to "Healthy"
# -----------------------------
post_disease_label = disease_label
post_disease_conf  = disease_conf
if args.consistency_rule and HEALTHY_IDX is not None and health_label == "Healthy":
    if "Healthy" in list(disease_classes):
        post_disease_label = "Healthy"
        # keep confidence conservative: min of health/disease confs
        post_disease_conf  = float(min(health_conf, disease_conf))

# -----------------------------
# Print results
# -----------------------------
print("\n=== Prediction ===")
print(f"Image     : {IMG_PATH}")
print(f"Plant     : {plant_label:>10s}  (conf {plant_conf:.3f})")
print(f"Health    : {health_label:>10s}  (conf {health_conf:.3f})")
print(f"Disease   : {disease_label:>10s}  (conf {disease_conf:.3f})")

if args.consistency_rule and post_disease_label != disease_label:
    print(f"↪ Post-processed Disease → {post_disease_label} (consistency rule applied)")

print("\nTop-{} per head:".format(TOPK))
print("• Plant  :", topk_probs(p_plant,  plant_classes,  TOPK))
print("• Health :", topk_probs(p_health, health_classes, TOPK))
print("• Disease:", topk_probs(p_disease, disease_classes, TOPK))
