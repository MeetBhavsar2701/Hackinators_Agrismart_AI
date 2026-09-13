import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.models import efficientnet_b0
from sklearn.metrics import f1_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

from train import CropDiseaseDataset
from augmentations import get_val_transforms

def evaluate_model(model, dataloader, device):
    model.eval()
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Evaluating", leave=False):
            images = images.to(device)
            outputs = model(images)
            preds = torch.argmax(outputs, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    return np.array(all_labels), np.array(all_preds)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--tiny_subset', action='store_true')
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    model_dir = base_dir / "model"
    report_dir = base_dir / "report"
    weights_dir = model_dir / "weights"
    
    val_manifest = model_dir / "val_manifest.csv"
    test_manifest = model_dir / "test_manifest.csv"
    mapping_file = weights_dir / "label_mapping.json"
    weights_file = weights_dir / "best_model.pt"
    
    if not mapping_file.exists() or not weights_file.exists():
        raise FileNotFoundError("Model weights or label mapping not found. Run train.py first.")
        
    with open(mapping_file, 'r') as f:
        idx_to_label = json.load(f)
    
    # Ensure keys are int for idx_to_label, and reverse for label_to_idx
    idx_to_label = {int(k): v for k, v in idx_to_label.items()}
    label_to_idx = {v: k for k, v in idx_to_label.items()}
    num_classes = len(label_to_idx)
    
    val_transform = get_val_transforms()
    val_dataset = CropDiseaseDataset(val_manifest, label_to_idx, transform=val_transform)
    test_dataset = CropDiseaseDataset(test_manifest, label_to_idx, transform=val_transform)
    
    if args.tiny_subset:
        val_dataset.df = val_dataset.df.head(args.batch_size)
        test_dataset.df = test_dataset.df.head(args.batch_size)
    
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = efficientnet_b0()
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(torch.load(weights_file, map_location=device))
    model = model.to(device)
    
    print("Evaluating on Validation Set (PlantVillage)...")
    val_labels, val_preds = evaluate_model(model, val_loader, device)
    
    print("Evaluating on Test Set (PlantDoc)...")
    test_labels, test_preds = evaluate_model(model, test_loader, device)
    
    def get_metrics(y_true, y_pred):
        mac_p, mac_r, mac_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0, labels=list(range(num_classes)))
        per_class_p, per_class_r, per_class_f1, _ = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0, labels=list(range(num_classes)))
        return {
            "macro_precision": float(mac_p),
            "macro_recall": float(mac_r),
            "macro_f1": float(mac_f1),
            "per_class": {
                idx_to_label[i]: {
                    "precision": float(per_class_p[i]),
                    "recall": float(per_class_r[i]),
                    "f1": float(per_class_f1[i])
                } for i in range(num_classes)
            }
        }
    
    results = {
        "validation_metrics": get_metrics(val_labels, val_preds),
        "test_metrics": get_metrics(test_labels, test_preds)
    }
    
    with open(report_dir / "metrics.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\n--- Metrics summary saved to {report_dir / 'metrics.json'} ---")
    print(f"Validation Macro F1: {results['validation_metrics']['macro_f1']:.4f}")
    print(f"Test Macro F1:       {results['test_metrics']['macro_f1']:.4f}")
    
    # Plot Confusion Matrix for Test Set
    cm = confusion_matrix(test_labels, test_preds, labels=list(range(num_classes)))
    plt.figure(figsize=(15, 12))
    sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=[idx_to_label[i] for i in range(num_classes)], 
                yticklabels=[idx_to_label[i] for i in range(num_classes)])
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Test Set Confusion Matrix (PlantDoc)')
    plt.tight_layout()
    plt.savefig(report_dir / "confusion_matrix.png")
    print(f"Confusion matrix saved to {report_dir / 'confusion_matrix.png'}")

if __name__ == "__main__":
    main()
