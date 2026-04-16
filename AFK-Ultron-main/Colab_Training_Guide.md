# Google Colab YOLOv8 Training Setup

To maximize speed and take advantage of Google's powerful A100 or T4 GPUs, use Google Colab for your two-stage training.

## Step 1: Open Google Colab
1. Go to [colab.research.google.com](https://colab.research.google.com/)
2. Click **New Notebook**.
3. At the top menu, go to **Runtime > Change runtime type**.
4. Select **T4 GPU** (or A100 if you have Colab Pro) and click Save.

## Step 2: Install Dependencies
Create a new code cell and paste this, then run it:

```python
# Install YOLOv8 and Roboflow
!pip install ultralytics roboflow
```

## Step 3: Stage 1 - Aerial Pre-Training
Create a new code cell and run this to download the massive VisDrone dataset and begin base training:

```python
from ultralytics import YOLO

# Load a fresh, tiny YOLOv8 model for speed
model = YOLO('yolov8n.pt')

# Train on VisDrone (Ultralytics handles the dataset download automatically)
results = model.train(
    data="VisDrone.yaml", 
    epochs=50, 
    imgsz=640,         # Dropped to 640 for a lighter, guaranteed-to-run resolution
    batch=16,          # Safe batch size for 640 resolution
    device=0, 
    name="aerial_base"
)
```

## Step 4: Download NOMAD Dataset (Roboflow)
Once Stage 1 finishes, you need to bring in your NOMAD data. Create a new cell, add your secret Roboflow API key, and run it:

```python
from roboflow import Roboflow

# Replace 'YOUR_KEY_HERE' with your real API Key from app.py
rf = Roboflow(api_key="YOUR_KEY_HERE")
project = rf.workspace("workspace-id").project("project-id") # Update with your NOMAD project IDs
dataset = project.version(1).download("yolov8")
```

## Step 5: Stage 2 - Fine-Tuning for NOMAD
Create the final code cell to apply heavy drone-movement augmentations on the NOMAD dataset:

```python
# Point the model to the weights from Stage 1
model = YOLO('/content/runs/detect/aerial_base/weights/best.pt')

# Train on the downloaded NOMAD dataset
# 'dataset.location' automatically points to where Roboflow downloaded the NOMAD data
results = model.train(
    data=f"{dataset.location}/data.yaml", 
    epochs=50, 
    imgsz=640, 
    batch=16, 
    device=0, 
    name="nomad_final",
    mosaic=1.0, 
    mixup=0.2, 
    degrees=15.0
)
```

## Step 6: Deploy to AFK-Ultron
When Stage 2 finishes:
1. Open the file browser on the left side of Colab (the folder icon).
2. Navigate to: `runs/detect/nomad_final/weights/`
3. Download the `best.pt` file.
4. Move this file locally into your `AFK-Ultron-main/Ultron/` folder, rename it to `nomad_drone_best.pt`, and your system will seamlessly use it because your Python code is already upgraded!
