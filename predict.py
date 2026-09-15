"""Repository-root entry point for the submission interface (section 4.1).

Lets the documented command work verbatim from a fresh clone:

    python predict.py --image path/to/leaf.jpg

The implementation lives in model/predict.py; this is a thin forwarder so both
`python predict.py` and `python model/predict.py` behave identically.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "model"))

from model.predict import main, predict, predict_details  # noqa: E402,F401

if __name__ == "__main__":
    main()
