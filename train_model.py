from ultralytics import YOLO
import os

if __name__ == '__main__':
    # 1. Point to train10 where you found the last.pt
    last_weights = r'C:/Cattle_Project/runs/detect/train10/weights/last.pt'
    data_yaml = r'C:/Cattle_Project/dataset/data.yaml'

    if not os.path.exists(last_weights):
        print(f"❌ ERROR: Still can't find it. Are you sure it's in train10?")
    else:
        # 2. Load the weights from epoch 90
        model = YOLO(last_weights)
        print("✅ Weights found! Starting the final 10 epochs on GTX 1650...")

        # 3. Resume the final push
        model.train(
            data=data_yaml,
            resume=True,
            workers=0,  # Keeps your 8GB RAM stable
            batch=2,    # Safe for the memory-heavy finish
            device=0    # Uses your GPU
        )