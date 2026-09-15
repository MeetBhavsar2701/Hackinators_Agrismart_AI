import os
import json
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0
import torch.nn.functional as F

from augmentations import get_val_transforms

PRECAUTIONS = {
    "Apple___Apple_scab": "Apply copper-based fungicides or captan during early spring. Remove and destroy infected leaves to reduce overwintering.",
    "Apple___Cedar_apple_rust": "Remove nearby Eastern Red Cedar trees if possible. Apply protective fungicides before spring rains.",
    "Apple___healthy": "No disease detected. Continue standard orchard maintenance.",
    "Blueberry___healthy": "No disease detected. Maintain optimal soil pH and watering.",
    "Cherry_(including_sour)___healthy": "No disease detected. Continue standard care.",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Use crop rotation and deep plowing to bury crop residue. Consider resistant hybrids.",
    "Corn_(maize)___Common_rust_": "Apply fungicides if spotted early. Ensure adequate air circulation.",
    "Corn_(maize)___Northern_Leaf_Blight": "Use resistant hybrids. Rotate crops and plow under crop debris.",
    "Grape___Black_rot": "Apply protective fungicides from early bloom until berries are pea-sized. Remove infected mummies.",
    "Grape___healthy": "No disease detected. Keep good canopy management.",
    "Peach___healthy": "No disease detected. Maintain regular pruning.",
    "Pepper,_bell___Bacterial_spot": "Use certified disease-free seeds. Apply copper bactericides. Rotate crops away from solanaceous plants.",
    "Pepper,_bell___healthy": "No disease detected. Continue standard care.",
    "Potato___Early_blight": "Apply fungicides such as chlorothalonil. Practice crop rotation and ensure good soil drainage.",
    "Potato___Late_blight": "Highly destructive! Apply specific fungicides immediately. Destroy infected plants to prevent spread.",
    "Potato___healthy": "No disease detected. Continue standard care.",
    "Raspberry___healthy": "No disease detected. Keep pruning old canes.",
    "Soybean___healthy": "No disease detected. Continue standard care.",
    "Squash___Powdery_mildew": "Apply sulfur or potassium bicarbonate-based fungicides. Ensure adequate spacing for airflow.",
    "Strawberry___healthy": "No disease detected. Continue standard care.",
    "Tomato___Bacterial_spot": "Apply copper-based sprays. Avoid overhead watering and rotate crops.",
    "Tomato___Early_blight": "Prune lower leaves to increase airflow. Apply fungicides like chlorothalonil.",
    "Tomato___Late_blight": "Highly destructive! Apply specific fungicides immediately and destroy infected plants.",
    "Tomato___Leaf_Mold": "Improve air circulation in greenhouses. Reduce humidity and apply appropriate fungicides.",
    "Tomato___Septoria_leaf_spot": "Remove affected lower leaves. Apply fungicides. Do not work among plants when wet.",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Use insecticidal soap or horticultural oil. Introduce predatory mites if possible.",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Control whitefly populations. Remove and destroy infected plants immediately.",
    "Tomato___Tomato_mosaic_virus": "No cure. Remove and destroy infected plants. Wash hands and tools thoroughly.",
    "Tomato___healthy": "No disease detected. Continue standard care."
}

def load_model_and_config():
    base_dir = Path(__file__).resolve().parent.parent
    weights_dir = base_dir / "model" / "weights"
    
    mapping_file = weights_dir / "label_mapping.json"
    weights_file = weights_dir / "best_model.pt"
    temp_file = weights_dir / "temperature.json"
    
    if not mapping_file.exists() or not weights_file.exists():
        raise FileNotFoundError("Model weights or label mapping not found. Run training first.")
        
    with open(mapping_file, 'r') as f:
        idx_to_label = json.load(f)
    idx_to_label = {int(k): v for k, v in idx_to_label.items()}
    num_classes = len(idx_to_label)
    
    # Load temperature if available, else default to 1.0
    temperature = 1.0
    if temp_file.exists():
        with open(temp_file, 'r') as f:
            temperature = json.load(f).get("temperature", 1.0)
            
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = efficientnet_b0()
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(torch.load(weights_file, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()
    
    return model, idx_to_label, temperature, device

def predict(image_path: str) -> str:
    """Submission interface — Problem Statement section 4.1.

        predict(image_path) -> class_label

    Loads the trained weights and runs on a single new image with no manual
    steps, returning the predicted class label as a plain string.

    Use predict_details() when the confidence score and precautionary text are
    also needed (the web API does).
    """
    return predict_details(image_path)["class_label"]


def predict_details(image_path: str) -> dict:
    """Full prediction: class_label, confidence, precaution."""
    model, idx_to_label, temperature, device = load_model_and_config()
    
    # Load and preprocess image
    image = Image.open(image_path).convert('RGB')
    image_np = np.array(image)
    
    transform = get_val_transforms()
    augmented = transform(image=image_np)
    image_np = augmented['image']
    
    # get_val_transforms() already applies A.Normalize(ImageNet mean/std), so the
    # array is correctly scaled here. Do NOT divide by 255 again -- doing so
    # collapsed the previous checkpoint to a constant prediction.
    image_tensor = torch.from_numpy(image_np).permute(2, 0, 1).float()
    image_tensor = image_tensor.unsqueeze(0).to(device) # Add batch dimension
    
    with torch.no_grad():
        logits = model(image_tensor)
        # Apply temperature scaling
        scaled_logits = logits / temperature
        # Get probabilities
        probs = F.softmax(scaled_logits, dim=1)
        
        confidence, class_idx = torch.max(probs, dim=1)
        class_idx = class_idx.item()
        confidence = confidence.item()
        
    class_label = idx_to_label[class_idx]
    precaution = PRECAUTIONS.get(class_label, "No precaution data available.")
    
    return {
        "class_label": class_label,
        "confidence": round(confidence, 4),
        "precaution": precaution
    }

def main():
    parser = argparse.ArgumentParser(description="Predict crop disease from an image.")
    parser.add_argument('--image', type=str, required=True, help='Path to the leaf image')
    parser.add_argument('--quiet', action='store_true',
                        help='Print only the predicted class label')
    args = parser.parse_args()
    
    try:
        result = predict_details(args.image)
        # Section 4.1: the CLI must print the predicted class.
        print(result["class_label"])
        if not args.quiet:
            print(json.dumps(result, indent=4))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))
        raise SystemExit(1)

if __name__ == "__main__":
    main()
