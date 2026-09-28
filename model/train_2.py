import os
import random
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

# Set seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# Path to dataset
base_dir = r"D:\sih\model\split_dataset"
csv_path = os.path.join(base_dir, "labels.csv")

# Load CSV
df = pd.read_csv(csv_path)
print("[DONE] Labels loaded:", df.shape)
print(df.head())

# Encode Labels
plant_encoder = LabelEncoder()
health_encoder = LabelEncoder()
disease_encoder = LabelEncoder()

df["plant_enc"] = plant_encoder.fit_transform(df["plant"])
df["health_enc"] = health_encoder.fit_transform(df["health"])
df["disease_enc"] = disease_encoder.fit_transform(df["disease"])

n_plants = len(plant_encoder.classes_)
n_health = len(health_encoder.classes_)
n_diseases = len(disease_encoder.classes_)

print("Plants:", n_plants)
print("Health:", n_health)
print("Diseases:", n_diseases)

# TF Dataset Loader with Simpler Augmentation
IMG_SIZE = (224, 224)
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.05),
])

def load_image(img_path, plant, health, disease, is_training):
    img = tf.io.read_file(img_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE) / 255.0
    if is_training:
        img = data_augmentation(img, training=True)
    labels = {
        "plant": tf.one_hot(plant, n_plants),
        "health": tf.one_hot(health, n_health),
        "disease": tf.one_hot(disease, n_diseases),
    }
    return img, labels

def make_dataset(df, split, batch_size=16):
    subset = df[df["split"] == split]
    is_training = (split == "train")

    paths = [os.path.join(base_dir, p) for p in subset["image_path"].values]

    ds = tf.data.Dataset.from_tensor_slices(
        (paths,
         subset["plant_enc"].values,
         subset["health_enc"].values,
         subset["disease_enc"].values,
         np.full(len(subset), is_training))
    )
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    if is_training:
        ds = ds.shuffle(500, seed=SEED)
    return ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)


train_ds = make_dataset(df, "train")
val_ds = make_dataset(df, "val")
test_ds = make_dataset(df, "test")
print("[READY] TF datasets ready")

# Build Multi-Output CNN (simpler)
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model

base = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224,224,3))
base.trainable = False  # Freeze all layers for stability

x = base.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation="relu")(x)
x = Dropout(0.3)(x)

# Shared representation
shared = Dense(128, activation="relu")(x)
shared = Dropout(0.2)(shared)

# Plant branch
plant_out = Dense(n_plants, activation="softmax", name="plant")(shared)
# Health branch
health_out = Dense(n_health, activation="softmax", name="health")(shared)
# Disease branch
disease_out = Dense(n_diseases, activation="softmax", name="disease")(shared)

model = Model(inputs=base.input, outputs=[plant_out, health_out, disease_out])

model.compile(
    optimizer=tf.keras.optimizers.Adam(5e-5),  # Lower learning rate
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

# Training
callbacks = [
    tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
    tf.keras.callbacks.ModelCheckpoint("best_model.keras", save_best_only=True),
]

# ---------- PHASE 1: heads-only training ----------
history1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=30,
    callbacks=callbacks
)

# ---------- PHASE 2: unfreeze top of backbone and fine-tune ----------
for layer in base.layers[-40:]:   # tweak 30–50 if needed
    layer.trainable = True

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),  # smaller LR for fine-tuning
    loss={
        "plant": "categorical_crossentropy",
        "health": "categorical_crossentropy",
        "disease": "categorical_crossentropy",
    },
    loss_weights={"plant": 1.2, "health": 1.2, "disease": 0.8},  # focus plant/health
    metrics={"plant": "accuracy", "health": "accuracy", "disease": "accuracy"},
)

callbacks_ft = [
    tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
    tf.keras.callbacks.ModelCheckpoint("best_model_ft.keras", save_best_only=True),
]

history2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,                   # short fine-tune
    callbacks=callbacks_ft
)


# Evaluate
model.evaluate(test_ds)
model.save("plant_health_disease_model_train_2.keras")

# Plot Training Curves
import matplotlib.pyplot as plt

def plot_history(hist, metric):
    plt.figure(figsize=(8,5))
    for output in ["plant", "health", "disease"]:
        plt.plot(hist.history.get(f"{output}_{metric}", []), label=f"{output}_{metric}")
        plt.plot(hist.history.get(f"val_{output}_{metric}", []),
                 label=f"val_{output}_{metric}", linestyle="--")
    plt.xlabel("Epochs"); plt.ylabel(metric.capitalize()); plt.legend(); plt.grid(True); plt.show()

# plot each phase separately
plot_history(history1, "accuracy"); plot_history(history1, "loss")
plot_history(history2, "accuracy"); plot_history(history2, "loss")