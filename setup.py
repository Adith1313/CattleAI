import os

# These are the folders YOLO needs to learn
folders = [
    "dataset/train/images",
    "dataset/train/labels",
    "dataset/valid/images",
    "dataset/valid/labels"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

print("✅ All folders created successfully!")