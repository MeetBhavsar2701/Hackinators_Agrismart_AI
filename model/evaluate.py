"""
Evaluate the shipped checkpoint on the held-out PlantVillage validation split
and write report/metrics.json + report/confusion_matrix.png.

Run:  python model/evaluate.py --data <dir>

<dir> must contain one subfolder per class, named exactly as in
model/weights/label_mapping.json. The split is the same deterministic
80/20 split (seed 0) used for training, so numbers are reproducible.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import (classification_report, confusion_matrix,
                             f1_score, accuracy_score)
from torchvision import transforms
from torchvision.models import efficientnet_b0

BASE = Path(__file__).resolve().parent.parent
WEIGHTS = BASE / "model" / "weights"

TF = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def load_model(n):
    m = efficientnet_b0()
    m.classifier[1] = nn.Linear(m.classifier[1].in_features, n)
    m.load_state_dict(torch.load(WEIGHTS / "best_model.pt", map_location="cpu",
                                 weights_only=True))
    m.eval()
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True,
                    help="Directory with one subfolder per class")
    ap.add_argument("--per-class", type=int, default=25,
                    help="Images per class to read (must match training)")
    args = ap.parse_args()

    classes = [v for _, v in sorted(
        json.load(open(WEIGHTS / "label_mapping.json")).items(),
        key=lambda kv: int(kv[0]))]
    model = load_model(len(classes))

    paths, labels = [], []
    for i, c in enumerate(classes):
        d = Path(args.data) / c
        if not d.is_dir():
            raise SystemExit(f"missing class folder: {d}")
        for p in sorted(d.iterdir())[:args.per_class]:
            paths.append(p)
            labels.append(i)

    # Same deterministic split as training
    y = torch.tensor(labels)
    perm = torch.randperm(len(y), generator=torch.Generator().manual_seed(0))
    n_train = int(len(y) * 0.8)
    val_idx = perm[n_train:].tolist()

    y_true, y_pred = [], []
    for i in val_idx:
        with torch.no_grad():
            logits = model(TF(Image.open(paths[i]).convert("RGB")).unsqueeze(0))
        y_pred.append(int(logits.argmax(1)))
        y_true.append(labels[i])

    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    rep = classification_report(y_true, y_pred, labels=list(range(len(classes))),
                                target_names=classes, output_dict=True,
                                zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(classes))))

    out = BASE / "report"
    out.mkdir(exist_ok=True)
    json.dump({
        "split": "PlantVillage held-out validation (20%, seed 0)",
        "n_images": len(y_true),
        "n_classes": len(classes),
        "macro_f1": round(macro_f1, 4),
        "accuracy": round(acc, 4),
        "per_class": {k: v for k, v in rep.items() if k in classes},
    }, open(out / "metrics.json", "w"), indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 11))
    ax.imshow(cm, cmap="Greens")
    ax.set_xticks(range(len(classes)))
    ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=90, fontsize=7)
    ax.set_yticklabels(classes, fontsize=7)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(f"Confusion matrix — held-out validation\n"
                 f"macro-F1 {macro_f1:.4f}, accuracy {acc:.4f}, n={len(y_true)}")
    for i in range(len(classes)):
        for j in range(len(classes)):
            if cm[i, j]:
                ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "confusion_matrix.png", dpi=130)

    print(f"macro-F1 {macro_f1:.4f}  accuracy {acc:.4f}  n={len(y_true)}")
    print(f"wrote {out/'metrics.json'} and {out/'confusion_matrix.png'}")


if __name__ == "__main__":
    main()
