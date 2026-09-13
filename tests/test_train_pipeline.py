import sys
from pathlib import Path
from unittest.mock import patch
import pytest

# Add the project root and model dir to sys.path to import model.train and augmentations
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "model"))
from train import main

def test_train_tiny_subset():
    """
    Smoke test to verify that the training loop runs end-to-end on a tiny subset
    without crashing.
    """
    test_args = ['train.py', '--tiny_subset', '--epochs', '1', '--batch_size', '4']
    with patch.object(sys, 'argv', test_args):
        # This will run train.py using only the first 4 images of the real dataset
        main()
