import os
import shutil
import tempfile
import pandas as pd
from pathlib import Path
from PIL import Image
import pytest
import sys

# Add the project root to sys.path to import model.prepare_data
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from model.prepare_data import main

@pytest.fixture
def dummy_project_dir():
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    base_dir = Path(temp_dir)
    
    # Create required subdirectories
    (base_dir / "data" / "plantvillage").mkdir(parents=True)
    (base_dir / "data" / "plantdoc").mkdir(parents=True)
    (base_dir / "model").mkdir(parents=True)
    (base_dir / "report").mkdir(parents=True)
    
    classes = ["apple_scab", "apple_healthy", "corn_rust"]
    
    def create_dummy_image(path):
        img = Image.new('RGB', (10, 10), color = 'red')
        img.save(path)

    # Populate PlantVillage (needs enough samples for split)
    for cls in classes:
        cls_dir = base_dir / "data" / "plantvillage" / cls
        cls_dir.mkdir()
        for i in range(10): # 10 images per class
            create_dummy_image(cls_dir / f"img_{i}.jpg")
            
    # Populate PlantDoc
    for cls in classes[:2]: # Missing one class to test intersection logic
        cls_dir = base_dir / "data" / "plantdoc" / cls
        cls_dir.mkdir()
        for i in range(3):
            create_dummy_image(cls_dir / f"test_{i}.jpg")
            
    yield base_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

def test_data_pipeline_manifests_and_leakage(dummy_project_dir):
    # Run the pipeline
    main(base_dir=dummy_project_dir)
    
    model_dir = dummy_project_dir / "model"
    train_csv = model_dir / "train_manifest.csv"
    val_csv = model_dir / "val_manifest.csv"
    test_csv = model_dir / "test_manifest.csv"
    
    assert train_csv.exists()
    assert val_csv.exists()
    assert test_csv.exists()
    
    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)
    test_df = pd.read_csv(test_csv)
    
    # Check formatting
    assert list(train_df.columns) == ["image_path", "label"]
    assert list(val_df.columns) == ["image_path", "label"]
    assert list(test_df.columns) == ["image_path", "label"]
    
    # Check class list is non-empty and matches intersection
    shared_classes = {"apple_scab", "apple_healthy"}
    assert set(train_df['label'].unique()) == shared_classes
    assert set(val_df['label'].unique()) == shared_classes
    assert set(test_df['label'].unique()) == shared_classes
    
    # Check no leakage
    train_paths = set(train_df['image_path'])
    val_paths = set(val_df['image_path'])
    test_paths = set(test_df['image_path'])
    
    assert len(train_paths.intersection(val_paths)) == 0, "Leakage detected between train and val!"
    assert len(train_paths.intersection(test_paths)) == 0, "Leakage detected between train and test!"
    assert len(val_paths.intersection(test_paths)) == 0, "Leakage detected between val and test!"

def test_missing_data_directory(tmp_path):
    with pytest.raises(FileNotFoundError, match="PlantVillage dataset not found"):
        main(base_dir=tmp_path)
