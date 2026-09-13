import sys
from pathlib import Path
import pytest

# Add the project root and model directory to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "model"))

from predict import predict

def test_predict_interface_keys_and_bounds():
    """
    Integration test to ensure the predict() function runs correctly on a real image
    and returns the expected data structure with valid confidence bounds.
    """
    data_dir = project_root / "data" / "plantdoc"
    if not data_dir.exists():
        pytest.skip("PlantDoc dataset not found locally. Skipping integration test.")
        
    images = list(data_dir.rglob("*.jpg"))
    if not images:
        pytest.skip("No .jpg images found in PlantDoc dataset. Skipping integration test.")
        
    test_image_path = str(images[0])
    
    result = predict(test_image_path)
    
    # Assert correct keys are present
    assert isinstance(result, dict)
    assert "class_label" in result
    assert "confidence" in result
    assert "precaution" in result
    
    # Assert values are valid
    assert isinstance(result["class_label"], str)
    assert isinstance(result["precaution"], str)
    
    confidence = result["confidence"]
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0
