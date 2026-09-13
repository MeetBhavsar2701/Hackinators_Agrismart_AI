import os
import re
import yaml
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from PIL import Image

def normalize_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', ' ', name)
    words = name.split()
    stop_words = {'leaf', 'leaves', 'plant', 'disease', 'including', 'sour', 'maize', 'the', 'of'}
    words = [w for w in words if w not in stop_words]
    if 'bell' in words and 'pepper' in words:
        words = [w for w in words if w != 'bell']
    if 'spider' in words and 'mites' in words:
        words.append('mite')
    return set(words)

def compute_sim(set1, set2):
    if not set1 or not set2: return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def build_class_mapping(pd_names, pv_names):
    mapping = {}
    for pd_cls in pd_names:
        pd_set = normalize_name(pd_cls)
        # special case for healthy: PlantDoc just says e.g., "Apple leaf"
        if len(pd_set) == 1 and "healthy" not in pd_set: 
            pd_set.add("healthy")
        if "soyabean" in pd_set: pd_set.add("soybean")
        
        best_match = None
        best_score = 0
        for pv_cls in pv_names:
            pv_set = normalize_name(pv_cls)
            score = compute_sim(pd_set, pv_set)
            if score > best_score:
                best_score = score
                best_match = pv_cls
                
        if best_score >= 0.5: # reasonable threshold
            mapping[pd_cls] = best_match
    return mapping

def main(base_dir=None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent
    else:
        base_dir = Path(base_dir)
        
    data_dir = base_dir / "data"
    pv_root = data_dir / "plantvillage"
    pd_root = data_dir / "plantdoc"
    
    if not pv_root.exists() or not any(pv_root.iterdir()):
        raise FileNotFoundError(f"PlantVillage dataset not found or empty at {pv_root}. Please download it from Kaggle and place it here.")
        
    if not pd_root.exists() or not any(pd_root.iterdir()):
        raise FileNotFoundError(f"PlantDoc dataset not found or empty at {pd_root}. Please download it and place it here.")
        
    # Find PlantVillage true root (could be inside color/)
    if (pv_root / "color").exists():
        pv_dir = pv_root / "color"
    else:
        pv_dir = pv_root
        
    pv_classes = [d.name for d in pv_dir.iterdir() if d.is_dir()]
    
    # Process PlantDoc
    yaml_path = pd_root / "data.yaml"
    
    if yaml_path.exists():
        with open(yaml_path, 'r') as f:
            pd_yaml = yaml.safe_load(f)
        pd_names = pd_yaml.get('names', [])
        if isinstance(pd_names, dict):
            pd_names = [pd_names[i] for i in range(len(pd_names))]
    else:
        # Fallback if no data.yaml, assume standard subdirectories
        pd_names = [d.name for d in pd_root.iterdir() if d.is_dir()]
        
    mapping = build_class_mapping(pd_names, pv_classes)
    
    shared_classes = sorted(list(set(mapping.values())))
    if not shared_classes:
        raise ValueError("No common classes found between PlantVillage and PlantDoc datasets.")
        
    print(f"Found {len(shared_classes)} shared classes dynamically matched!")
    
    # Load PlantVillage data
    extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    pv_data = []
    for cls in shared_classes:
        cls_dir = pv_dir / cls
        if cls_dir.exists():
            for file in cls_dir.iterdir():
                if file.is_file() and file.suffix in extensions:
                    pv_data.append({"image_path": str(file.absolute()), "label": cls})
    pv_df = pd.DataFrame(pv_data)
    
    if pv_df.empty:
        raise ValueError("No images found in PlantVillage for the shared classes.")
        
    # Split PlantVillage 80/20
    train_df, val_df = train_test_split(pv_df, test_size=0.2, stratify=pv_df['label'], random_state=42)
    
    # Load PlantDoc data
    pd_data = []
    if yaml_path.exists():
        for split in ['train', 'valid', 'test']:
            split_dir = pd_root / split
            img_dir = split_dir / "images"
            lbl_dir = split_dir / "labels"
            if not img_dir.exists() or not lbl_dir.exists():
                continue
                
            for img_file in img_dir.iterdir():
                if img_file.suffix in extensions:
                    lbl_file = lbl_dir / (img_file.stem + ".txt")
                    if lbl_file.exists():
                        with open(lbl_file, 'r') as lf:
                            lines = lf.readlines()
                            if lines:
                                class_id = int(lines[0].split()[0])
                                if 0 <= class_id < len(pd_names):
                                    pd_cls_name = pd_names[class_id]
                                    if pd_cls_name in mapping:
                                        pv_cls_name = mapping[pd_cls_name]
                                        pd_data.append({"image_path": str(img_file.absolute()), "label": pv_cls_name})
    else:
        # Fallback subdirectory logic
        for pd_cls_name in mapping:
            cls_dir = pd_root / pd_cls_name
            if cls_dir.exists():
                for file in cls_dir.iterdir():
                    if file.is_file() and file.suffix in extensions:
                        pv_cls_name = mapping[pd_cls_name]
                        pd_data.append({"image_path": str(file.absolute()), "label": pv_cls_name})
                                        
    test_df = pd.DataFrame(pd_data)
    if test_df.empty:
        raise ValueError("No images found in PlantDoc for the shared classes.")
        
    # Save manifests
    model_dir = base_dir / "model"
    train_df.to_csv(model_dir / "train_manifest.csv", index=False)
    val_df.to_csv(model_dir / "val_manifest.csv", index=False)
    test_df.to_csv(model_dir / "test_manifest.csv", index=False)
    
    # EDA: Class balance
    print("\n--- Class Distributions ---")
    print("PlantVillage Train:")
    print(train_df['label'].value_counts())
    print("\nPlantVillage Val:")
    print(val_df['label'].value_counts())
    print("\nPlantDoc Test:")
    print(test_df['label'].value_counts())
    
    # EDA: Sample Grid
    report_dir = base_dir / "report"
    report_dir.mkdir(exist_ok=True)
    
    samples = []
    if not train_df.empty: samples.append(("Train (PlantVillage)", train_df.sample(1).iloc[0]))
    if len(train_df) > 1: samples.append(("Train (PlantVillage)", train_df.sample(1).iloc[0]))
    if not val_df.empty: samples.append(("Val (PlantVillage)", val_df.sample(1).iloc[0]))
    if not test_df.empty: samples.append(("Test (PlantDoc)", test_df.sample(1).iloc[0]))
    
    if samples:
        fig, axes = plt.subplots(1, len(samples), figsize=(15, 5))
        if len(samples) == 1:
            axes = [axes]
        for ax, (split_name, row) in zip(axes, samples):
            img = Image.open(row['image_path'])
            ax.imshow(img)
            ax.set_title(f"{split_name}\n{row['label']}", fontsize=8)
            ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(report_dir / "eda_samples.png")
        print(f"\nSaved sample grid to {report_dir / 'eda_samples.png'}")

if __name__ == "__main__":
    main()
