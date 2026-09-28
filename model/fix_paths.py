import os
import pandas as pd

# Base dataset directory (relative to this script)
base_dir = os.path.join(os.path.dirname(__file__), "Split_Dataset")
csv_path = os.path.join(base_dir, "labels.csv")
output_csv_path = os.path.join(base_dir, "labels_clean.csv")

print(f"📂 Base dataset folder: {base_dir}")
print(f"📄 Input CSV: {csv_path}")
print(f"💾 Output CSV: {output_csv_path}")

# Load CSV
df = pd.read_csv(csv_path)
print("✅ Loaded CSV:", df.shape)

# Fix paths → keep relative path inside Split_Dataset
def fix_path(p):
    # Normalize slashes
    p = p.replace("\\", "/")
    # Drop everything up to 'Split_Dataset/'
    if "Split_Dataset/" in p:
        p = p.split("Split_Dataset/")[-1]
    return p

df["image_path"] = df["image_path"].apply(fix_path)

# Drop rows where the file does not exist
df = df[df["image_path"].apply(lambda p: os.path.exists(os.path.join(base_dir, p)))]

# Save cleaned CSV
df.to_csv(output_csv_path, index=False)
print("🎉 Cleaned CSV saved:", output_csv_path)
print("✅ Final rows:", df.shape[0])

# Preview
print(df.head())
