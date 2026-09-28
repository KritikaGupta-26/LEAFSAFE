# =========================
# STEP 1: Setup
# =========================
import os
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

# Path to dataset
base_dir = r"C:\Users\LENOVO\Desktop\SIH_CNN_TRAIL_MODEL\Split_Dataset"
csv_path = os.path.join(base_dir, "labels.csv")

# Load CSV
df = pd.read_csv(csv_path)
print("✅ Labels loaded:", df.shape)
print(df.head())

# =========================
# STEP 2: Encode Labels
# =========================
plant_encoder = LabelEncoder()
health_encoder = LabelEncoder()
disease_encoder = LabelEncoder()

df["plant_enc"] = plant_encoder.fit_transform(df["plant"])
df["health_enc"] = health_encoder.fit_transform(df["health"])
df["disease_enc"] = disease_encoder.fit_transform(df["disease"])

n_plants = len(plant_encoder.classes_)
n_health = len(health_encoder.classes_)
n_diseases = len(disease_encoder.classes_)

print("Plants:", plant_encoder.classes_)
print("Health:", health_encoder.classes_)
print("Diseases:", disease_encoder.classes_[:10], "... total:", n_diseases)

# =========================
# STEP 3: TF Dataset Loader
# =========================
IMG_SIZE = (256, 256)

def load_image(img_path, plant, health, disease):
    img = tf.io.read_file(img_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE) / 255.0
    labels = {
        "plant": tf.one_hot(plant, n_plants),
        "health": tf.one_hot(health, n_health),
        "disease": tf.one_hot(disease, n_diseases),
    }
    return img, labels

def make_dataset(df, split, batch_size=32):
    subset = df[df["split"] == split]
    ds = tf.data.Dataset.from_tensor_slices(
        (subset["image_path"], subset["plant_enc"], subset["health_enc"], subset["disease_enc"])
    )
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.shuffle(500).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(df, "train")
val_ds = make_dataset(df, "val")
test_ds = make_dataset(df, "test")
print("✅ TF datasets ready")

# =========================
# STEP 4: Build Multi-Output CNN
# =========================
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model

base = MobileNetV2(weights="imagenet", include_top=False, input_shape=(256,256,3))
x = GlobalAveragePooling2D()(base.output)
x = Dropout(0.3)(x)
plant_out = Dense(n_plants, activation='softmax', name="plant")(x)
health_out = Dense(n_health, activation='softmax', name="health")(x)
disease_out = Dense(n_diseases, activation='softmax', name="disease")(x)

model = Model(inputs=base.input, outputs=[plant_out, health_out, disease_out])
model.compile(
    optimizer="adam",
    loss={
        "plant": "categorical_crossentropy",
        "health": "categorical_crossentropy",
        "disease": "categorical_crossentropy"
    },
    metrics={
        "plant": "accuracy",
        "health": "accuracy",
        "disease": "accuracy"
    }
)
model.summary()

# =========================
# STEP 5: Train
# =========================
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=20  # increase to 20+ for better accuracy
)

# =========================
# STEP 6: Evaluate
# =========================
model.evaluate(test_ds)
model.save("plant_health_disease_model.keras")

# =========================
# STEP 7: Plot Training Curves
# =========================
import matplotlib.pyplot as plt

def plot_history(hist, metric):
    plt.figure(figsize=(8,5))
    for output in ["plant", "health", "disease"]:
        plt.plot(hist.history[f"{output}{metric}"], label=f"{output}{metric}")
        plt.plot(hist.history[f"val_{output}{metric}"], label=f"val{output}_{metric}", linestyle="--")
    plt.xlabel("Epochs")
    plt.ylabel(metric.capitalize())
    plt.legend()
    plt.grid(True)
    plt.show()

plot_history(history, "accuracy")
plot_history(history, "loss")