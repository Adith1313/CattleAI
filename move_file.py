import shutil
import os

# This is where the AI saved your brain (based on your screenshot)
source = "runs/detect/train2/weights/best.pt"
destination = "best.pt"

if os.path.exists(source):
    shutil.copy(source, destination)
    print("✅ Success! Moved best.pt to the main folder.")
else:
    print("❌ Error: Could not find the file. Please look for 'best.pt' manually inside the 'runs' folder.")