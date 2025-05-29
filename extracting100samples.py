import pandas as pd
import os
import requests
from PIL import Image
from io import BytesIO

# === CONFIG ===
INPUT_CSV = "/Users/yaseenshaikh/Desktop/IEEE Research/datasets/final_dataset.csv"
OUTPUT_CSV = "/Users/yaseenshaikh/Desktop/IEEE Research/datasets/final_dataset_ready.csv"
EMO_SAVE_DIR = "/Users/yaseenshaikh/Desktop/IEEE Research/datasets/emo135_images"
TARGET_SIZE = (48, 48)

# Create directory if it doesn't exist
os.makedirs(EMO_SAVE_DIR, exist_ok=True)

# Load the original dataset
df = pd.read_csv(INPUT_CSV)

# Track new paths
clean_paths = []
skipped_indices = []
emo_counter = 0

for idx, row in df.iterrows():
    source = row['source']
    path = row['file_path']

    if source == 'ck+':
        # Keep CK+ image path as-is
        clean_paths.append(path)

    elif source == 'emo135':
        try:
            response = requests.get(path, timeout=10)
            img = Image.open(BytesIO(response.content)).convert('L')  # Grayscale
            img = img.resize(TARGET_SIZE)

            # Save with correct naming
            filename = f"image_emo_{emo_counter:04}.png"
            save_path = os.path.join(EMO_SAVE_DIR, filename)
            img.save(save_path)

            # Append absolute path
            clean_paths.append(save_path)
            emo_counter += 1

        except Exception as e:
            print(f"❌ Skipped index {idx} — reason: {e}")
            skipped_indices.append(idx)
            clean_paths.append("ERROR")

    else:
        print(f"⚠️ Unknown source at index {idx}")
        skipped_indices.append(idx)
        clean_paths.append("ERROR")

# Update DataFrame and filter out errors
df['file_path'] = clean_paths
df_clean = df[df['file_path'] != "ERROR"]

# Save to final CSV
df_clean.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Final cleaned dataset saved to: {OUTPUT_CSV}")
print(f"✅ Total records kept: {len(df_clean)}")
print(f"❌ Total records skipped: {len(skipped_indices)}")
