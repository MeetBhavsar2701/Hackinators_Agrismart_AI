import json
import argparse
import pandas as pd
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision.models import efficientnet_b0
from tqdm import tqdm

from train import CropDiseaseDataset
from augmentations import get_val_transforms

class ModelWithTemperature(nn.Module):
    def __init__(self, model):
        super(ModelWithTemperature, self).__init__()
        self.model = model
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)

    def forward(self, input):
        logits = self.model(input)
        return self.temperature_scale(logits)

    def temperature_scale(self, logits):
        temperature = self.temperature.unsqueeze(1).expand(logits.size(0), logits.size(1))
        return logits / temperature

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--tiny_subset', action='store_true')
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    model_dir = base_dir / "model"
    weights_dir = model_dir / "weights"
    
    val_manifest = model_dir / "val_manifest.csv"
    mapping_file = weights_dir / "label_mapping.json"
    weights_file = weights_dir / "best_model.pt"
    
    if not mapping_file.exists() or not weights_file.exists():
        raise FileNotFoundError("Model weights or label mapping not found. Run train.py first.")
        
    with open(mapping_file, 'r') as f:
        idx_to_label = json.load(f)
        
    label_to_idx = {v: int(k) for k, v in idx_to_label.items()}
    num_classes = len(label_to_idx)
    
    val_dataset = CropDiseaseDataset(val_manifest, label_to_idx, transform=get_val_transforms())
    if args.tiny_subset:
        val_dataset.df = val_dataset.df.head(args.batch_size)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = efficientnet_b0()
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(torch.load(weights_file, map_location=device))
    model = model.to(device)
    model.eval()
    
    # Collect logits and labels
    logits_list = []
    labels_list = []
    
    with torch.no_grad():
        for images, labels in tqdm(val_loader, desc="Collecting logits", leave=False):
            images = images.to(device)
            logits = model(images)
            logits_list.append(logits)
            labels_list.append(labels)
            
    logits = torch.cat(logits_list).to(device)
    labels = torch.cat(labels_list).to(device)
    
    # Calculate Expected Calibration Error (ECE) before
    criterion = nn.CrossEntropyLoss()
    before_temperature_nll = criterion(logits, labels).item()
    print(f"Before temperature - NLL: {before_temperature_nll:.4f}")
    
    # Optimize Temperature
    scaled_model = ModelWithTemperature(model).to(device)
    optimizer = optim.LBFGS([scaled_model.temperature], lr=0.01, max_iter=50)
    
    def eval():
        optimizer.zero_grad()
        loss = criterion(scaled_model.temperature_scale(logits), labels)
        loss.backward()
        return loss
        
    optimizer.step(eval)
    
    after_temperature_nll = criterion(scaled_model.temperature_scale(logits), labels).item()
    T = scaled_model.temperature.item()
    
    print(f"Optimal temperature: {T:.4f}")
    print(f"After temperature - NLL: {after_temperature_nll:.4f}")
    
    with open(weights_dir / "temperature.json", "w") as f:
        json.dump({"temperature": T}, f, indent=4)
        
    print(f"Saved temperature to {weights_dir / 'temperature.json'}")

if __name__ == "__main__":
    main()
