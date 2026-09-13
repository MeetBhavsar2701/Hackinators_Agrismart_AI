import os
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from sklearn.metrics import f1_score, accuracy_score
from tqdm import tqdm

from augmentations import get_train_transforms, get_val_transforms

class CropDiseaseDataset(Dataset):
    def __init__(self, manifest_file, label_to_idx, transform=None):
        self.df = pd.read_csv(manifest_file)
        self.label_to_idx = label_to_idx
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row['image_path']
        label_str = row['label']
        
        # Open image and convert to RGB
        image = Image.open(img_path).convert('RGB')
        image_np = np.array(image)
        
        if self.transform:
            augmented = self.transform(image=image_np)
            image_np = augmented['image']
            
        # Convert HWC numpy to CHW tensor and normalize to [0,1]
        image_tensor = torch.from_numpy(image_np).permute(2, 0, 1).float() / 255.0
        
        label_idx = self.label_to_idx[label_str]
        return image_tensor, torch.tensor(label_idx, dtype=torch.long)

def get_label_mapping(train_manifest_path):
    df = pd.read_csv(train_manifest_path)
    unique_labels = sorted(df['label'].unique())
    label_to_idx = {label: i for i, label in enumerate(unique_labels)}
    idx_to_label = {i: label for label, i in label_to_idx.items()}
    return label_to_idx, idx_to_label

def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    all_preds, all_labels = [], []
    
    pbar = tqdm(dataloader, desc="Training", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * images.size(0)
        preds = torch.argmax(outputs, dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        
        pbar.set_postfix({'loss': loss.item()})
        
    epoch_loss = running_loss / len(dataloader.dataset)
    epoch_acc = accuracy_score(all_labels, all_preds)
    epoch_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    return epoch_loss, epoch_acc, epoch_f1

def validate_epoch(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Validating", leave=False):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    epoch_loss = running_loss / len(dataloader.dataset)
    epoch_acc = accuracy_score(all_labels, all_preds)
    epoch_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    return epoch_loss, epoch_acc, epoch_f1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=1, help='Number of epochs to train (default 1 for local tests)')
    parser.add_argument('--batch_size', type=int, default=16, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--tiny_subset', action='store_true', help='Use a tiny subset of data for smoke testing')
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    model_dir = base_dir / "model"
    report_dir = base_dir / "report"
    weights_dir = model_dir / "weights"
    
    report_dir.mkdir(exist_ok=True)
    weights_dir.mkdir(exist_ok=True)
    
    train_manifest = model_dir / "train_manifest.csv"
    val_manifest = model_dir / "val_manifest.csv"
    
    label_to_idx, idx_to_label = get_label_mapping(train_manifest)
    num_classes = len(label_to_idx)
    
    train_transform = get_train_transforms()
    val_transform = get_val_transforms()
    
    train_dataset = CropDiseaseDataset(train_manifest, label_to_idx, transform=train_transform)
    val_dataset = CropDiseaseDataset(val_manifest, label_to_idx, transform=val_transform)
    
    if args.tiny_subset:
        print("Using tiny subset for smoke testing...")
        train_dataset.df = train_dataset.df.head(args.batch_size)
        val_dataset.df = val_dataset.df.head(args.batch_size)
        
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load Pretrained EfficientNet-B0
    model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
    # Replace classification head
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    
    best_val_f1 = -1.0
    history = []
    
    for epoch in range(args.epochs):
        print(f"Epoch {epoch+1}/{args.epochs}")
        train_loss, train_acc, train_f1 = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_f1 = validate_epoch(model, val_loader, criterion, device)
        
        print(f"Train - Loss: {train_loss:.4f}, Acc: {train_acc:.4f}, F1: {train_f1:.4f}")
        print(f"Val   - Loss: {val_loss:.4f}, Acc: {val_acc:.4f}, F1: {val_f1:.4f}")
        
        history.append({
            'epoch': epoch + 1,
            'train_loss': train_loss, 'train_acc': train_acc, 'train_macro_f1': train_f1,
            'val_loss': val_loss, 'val_acc': val_acc, 'val_macro_f1': val_f1
        })
        
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            torch.save(model.state_dict(), weights_dir / "best_model.pt")
            
            # Save label mapping alongside the model
            import json
            with open(weights_dir / "label_mapping.json", "w") as f:
                json.dump(idx_to_label, f)
            print(f"-> Saved new best model with Val F1: {val_f1:.4f}")
            
    # Save training log
    log_df = pd.DataFrame(history)
    log_df.to_csv(report_dir / "training_log.csv", index=False)
    print(f"Training complete. Log saved to {report_dir / 'training_log.csv'}")

if __name__ == "__main__":
    main()
