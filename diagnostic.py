import pandas as pd
import json
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0
from pathlib import Path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from augmentations import get_val_transforms
import torch.nn.functional as F

def main():
    base_dir = Path(__file__).resolve().parent
    model_dir = base_dir / "model"
    weights_dir = model_dir / "weights"
    test_manifest = model_dir / "test_manifest.csv"
    mapping_file = weights_dir / "label_mapping.json"
    weights_file = weights_dir / "best_model_v2.pt"

    with open(mapping_file, 'r') as f:
        idx_to_label = json.load(f)
    idx_to_label = {int(k): v for k, v in idx_to_label.items()}
    num_classes = len(idx_to_label)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = efficientnet_b0()
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(torch.load(weights_file, map_location=device))
    model = model.to(device)
    model.eval()

    df = pd.read_csv(test_manifest)
    transform = get_val_transforms()

    print("--- Running Inference on Full Test Set ---")
    preds_counts = {v: 0 for v in idx_to_label.values()}
    
    # 3. PREDICTION DISTRIBUTION
    with torch.no_grad():
        for _, row in df.iterrows():
            img = Image.open(row['image_path']).convert('RGB')
            img_np = np.array(img)
            img_np = transform(image=img_np)['image']
            tensor = torch.from_numpy(img_np).permute(2, 0, 1).float() / 255.0
            tensor = tensor.unsqueeze(0).to(device)
            out = model(tensor)
            pred_idx = torch.argmax(out, dim=1).item()
            preds_counts[idx_to_label[pred_idx]] += 1
            
    print("Prediction Distribution:")
    for k, v in preds_counts.items():
        if v > 0:
            print(f"{k}: {v}")
            
    # 4. VISUAL SPOT CHECK
    sample_df = df.sample(5)
    fig, axes = plt.subplots(1, 5, figsize=(20, 5))
    
    for ax, (_, row) in zip(axes, sample_df.iterrows()):
        img = Image.open(row['image_path']).convert('RGB')
        img_np = np.array(img)
        t_img = transform(image=img_np)['image']
        tensor = torch.from_numpy(t_img).permute(2, 0, 1).float() / 255.0
        tensor = tensor.unsqueeze(0).to(device)
        
        with torch.no_grad():
            out = model(tensor)
            probs = F.softmax(out, dim=1)
            pred_idx = torch.argmax(out, dim=1).item()
            conf = probs[0, pred_idx].item()
            
        ax.imshow(img_np)
        ax.set_title(f"True: {row['label']}\nPred: {idx_to_label[pred_idx]}\nConf: {conf:.2f}", fontsize=8)
        ax.axis('off')
        
    plt.tight_layout()
    plt.savefig('report/spot_check.png')
    print("Saved visual spot check to report/spot_check.png")

if __name__ == "__main__":
    main()
