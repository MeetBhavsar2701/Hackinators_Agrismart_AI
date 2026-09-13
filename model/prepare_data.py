import os
import yaml
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from PIL import Image

CLASS_MAPPING = {
    "Apple___Apple_scab": "Apple Scab Leaf",
    "Apple___Cedar_apple_rust": "Apple rust leaf",
    "Apple___healthy": "Apple leaf",
    "Blueberry___healthy": "Blueberry leaf",
    "Cherry_(including_sour)___healthy": "Cherry leaf",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn Gray leaf spot",
    "Corn_(maize)___Common_rust_": "Corn rust leaf",
    "Corn_(maize)___Northern_Leaf_Blight": "Corn leaf blight",
    "Grape___Black_rot": "grape leaf black rot",
    "Grape___healthy": "grape leaf",
    "Peach___healthy": "Peach leaf",
    "Pepper,_bell___Bacterial_spot": "Bell_pepper leaf spot",
    "Pepper,_bell___healthy": "Bell_pepper leaf",
    "Potato___Early_blight": "Potato leaf early blight",
    "Potato___Late_blight": "Potato leaf late blight",
    "Raspberry___healthy": "Raspberry leaf",
    "Soybean___healthy": "Soyabean leaf",
    "Squash___Powdery_mildew": "Squash Powdery mildew leaf",
    "Strawberry___healthy": "Strawberry leaf",
    "Tomato___Bacterial_spot": "Tomato leaf bacterial spot",
    "Tomato___Early_blight": "Tomato Early blight leaf",
    "Tomato___healthy": "Tomato leaf",
    "Tomato___Late_blight": "Tomato leaf late blight",
    "Tomato___Leaf_Mold": "Tomato mold leaf",
    "Tomato___Septoria_leaf_spot": "Tomato Septoria leaf spot",
    "Tomato___Tomato_mosaic_virus": "Tomato leaf mosaic virus",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato leaf yellow virus",
}

def main(base_dir=None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent
    else:
        base_dir = Path(base_dir)
        
    data_dir = base_dir / "data"
    
    # In some extractions it's "plantvillage dataset/color", in others just "color"
    pv_root = data_dir / "plantvillage"
    if (pv_root / "plantvillage dataset" / "color").exists():
        pv_dir = pv_root / "plantvillage dataset" / "color"
    elif (pv_root / "color").exists():
        pv_dir = pv_root / "color"
    else:
        raise FileNotFoundError(f"Could not find 'color' directory in {pv_root}")

    pd_root = data_dir / "plantdoc"
    yaml_path = pd_root / "data.yaml"
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"PlantDoc data.yaml not found at {yaml_path}")
        
    with open(yaml_path, 'r') as f:
        pd_yaml = yaml.safe_load(f)
        
    pd_names = pd_yaml.get('names', [])
    if isinstance(pd_names, dict):
        pd_names = [pd_names[i] for i in range(len(pd_names))]

    # 4. Programmatically verify every folder/class exists
    missing_pv = []
    missing_pd = []
    
    for pv_cls, pd_cls in CLASS_MAPPING.items():
        if not (pv_dir / pv_cls).exists():
            missing_pv.append(pv_cls)
        if pd_cls not in pd_names:
            missing_pd.append(pd_cls)
            
    if missing_pv or missing_pd:
        error_msg = "Class mapping validation failed!\n"
        if missing_pv:
            error_msg += f"Missing in PlantVillage ({pv_dir}):\n  " + "\n  ".join(missing_pv) + "\n"
        if missing_pd:
            error_msg += f"Missing in PlantDoc (data.yaml names):\n  " + "\n  ".join(missing_pd) + "\n"
        raise ValueError(error_msg)
        
    print(f"Validation successful! All {len(CLASS_MAPPING)} mapped classes exist in both datasets.")
    
    # Create an inverse mapping for PlantDoc ID -> PlantVillage label
    pd_name_to_pv = {pd_cls: pv_cls for pv_cls, pd_cls in CLASS_MAPPING.items()}
    pd_id_to_pv = {}
    for idx, name in enumerate(pd_names):
        if name in pd_name_to_pv:
            pd_id_to_pv[idx] = pd_name_to_pv[name]

    # Load PlantVillage data (Train/Val)
    extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    pv_data = []
    for pv_cls in CLASS_MAPPING.keys():
        cls_dir = pv_dir / pv_cls
        for file in cls_dir.iterdir():
            if file.is_file() and file.suffix in extensions:
                pv_data.append({"image_path": str(file.absolute()), "label": pv_cls})
                
    pv_df = pd.DataFrame(pv_data)
    if pv_df.empty:
        raise ValueError("No images found in PlantVillage for the mapped classes.")
        
    # Split PlantVillage 80/20
    train_df, val_df = train_test_split(pv_df, test_size=0.2, stratify=pv_df['label'], random_state=42)
    
    # Load PlantDoc data (Test ONLY)
    pd_data = []
    test_dir = pd_root / "test"
    img_dir = test_dir / "images"
    lbl_dir = test_dir / "labels"
    
    if not img_dir.exists() or not lbl_dir.exists():
        raise FileNotFoundError(f"PlantDoc test directories missing at {test_dir}")
        
    for img_file in img_dir.iterdir():
        if img_file.suffix in extensions:
            lbl_file = lbl_dir / (img_file.stem + ".txt")
            if lbl_file.exists():
                with open(lbl_file, 'r') as lf:
                    lines = lf.readlines()
                    if lines:
                        # Taking the first bounding box class as the image class for simplicity
                        class_id = int(lines[0].split()[0])
                        if class_id in pd_id_to_pv:
                            pv_cls_name = pd_id_to_pv[class_id]
                            pd_data.append({"image_path": str(img_file.absolute()), "label": pv_cls_name})
                                        
    test_df = pd.DataFrame(pd_data)
    if test_df.empty:
        raise ValueError("No images found in PlantDoc 'test' split for the mapped classes.")
        
    # Save manifests
    model_dir = base_dir / "model"
    train_df.to_csv(model_dir / "train_manifest.csv", index=False)
    val_df.to_csv(model_dir / "val_manifest.csv", index=False)
    test_df.to_csv(model_dir / "test_manifest.csv", index=False)
    
    # EDA: Class balance
    print("\n--- Summary ---")
    print(f"Total Shared Classes: {len(CLASS_MAPPING)}")
    print(f"Train Manifest: {len(train_df)} images")
    print(f"Val Manifest:   {len(val_df)} images")
    print(f"Test Manifest:  {len(test_df)} images (from PlantDoc test set only)\n")
    
    print("--- Sample Rows (Train) ---")
    print(train_df.head(3))
    print("\n--- Sample Rows (Val) ---")
    print(val_df.head(3))
    print("\n--- Sample Rows (Test) ---")
    print(test_df.head(3))
    
    # Verify non-zero counts for every class in test
    test_counts = test_df['label'].value_counts()
    missing_test_classes = set(CLASS_MAPPING.keys()) - set(test_counts.index)
    if missing_test_classes:
        print(f"\nWARNING: The following classes have ZERO images in the PlantDoc test set:")
        for c in missing_test_classes:
            print(f"  - {c}")
            
    print("\nData pipeline completed successfully.")

if __name__ == "__main__":
    main()
