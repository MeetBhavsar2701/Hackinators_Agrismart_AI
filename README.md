# 🌿 AgriSmart AI — Intelligent Agriculture for a Sustainable Future

**SIH 2026 Internal Hackathon · L. J. Institute of Engineering and Technology [C-433] · Problem Statement 1**

An AI-powered crop-disease detection tool that classifies plant diseases from leaf
images and presents the result to a farmer in plain, actionable language — with an
explicit statement of what the model does **not** know.

| | |
|---|---|
| **Core task** | Crop disease detection (computer vision), 27 classes |
| **Model** | EfficientNet-B0 (ImageNet-pretrained backbone) + trained classifier head |
| **Held-out validation macro-F1** | **0.9005** · accuracy 0.9037 · n=135 |
| **Bonus modules** | B (Smart Irrigation) · E (Farmer Assistant) · F (IoT, simulated) |
| **Interface** | React + Vite + Tailwind web app, FastAPI backend, SQLite history |
| **Reproduce a prediction in** | ~3 minutes (one command, sample images included) |

---

## 📋 Submission contract — where to find each requirement

| §7.2 requirement | Section |
|---|---|
| 1. Core + bonus modules built | [Modules](#-modules-built) |
| 2. Setup and run instructions | [Quick start](#-quick-start) |
| 3. Dataset and source/licence | [Dataset](#-dataset--licence) |
| 4. Metrics (macro-F1 + confusion matrix) | [Results](#-results) |
| 5. Architecture + known limitations | [Architecture](#-architecture) · [Limitations](#️-known-limitations) |
| 6. Demo video + deployed app links | [Links](#-demo--deployment) |
| §8. Originality declaration | [Originality](#-originality-declaration) |
| §7.3. One-page model report | [`report/model_report.md`](report/model_report.md) |

---

## 🚀 Quick start

A judge should get a prediction in under 10 minutes. The fastest path needs **one
command** — model weights and sample images are committed, no dataset download.

### Prerequisites
Python 3.9+ · Node.js 18+ (only for the web UI)

### 1. Install

```bash
git clone https://github.com/MeetBhavsar2701/Hackinators_Agrismart_AI.git
cd Hackinators_Agrismart_AI
pip install -r requirements.txt
```

> On a machine without an NVIDIA GPU, install the smaller CPU build first — inference
> needs no GPU:
> `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`

### 2. Run the core task (this alone satisfies §4.1)

```bash
python predict.py --image samples/lab_tomato_early_blight.jpg
```

```
Tomato___Early_blight
{
    "class_label": "Tomato___Early_blight",
    "confidence": 0.9927,
    "precaution": "Prune lower leaves to increase airflow. Apply fungicides like chlorothalonil."
}
```

Add `--quiet` to print only the class label:

```bash
python predict.py --image samples/lab_potato_late_blight.jpg --quiet   # Potato___Late_blight
```

The Python interface required by §4.1 is `predict(image_path) -> class_label`,
returning a plain string:

```python
from model.predict import predict
predict("samples/lab_potato_late_blight.jpg")        # 'Potato___Late_blight'
```

`predict_details(image_path)` returns the full `dict` with confidence and
precaution — that is what the web API uses. Both `python predict.py` and
`python model/predict.py` work identically.

### 3. Run the web app

Terminal 1 — backend:

```bash
python src/api.py
```

Terminal 2 — frontend:

```bash
cd src/frontend && npm install && npm run dev
```

Open <http://localhost:5173>. API docs at <http://localhost:8000/docs>,
readiness at <http://localhost:8000/health>.

### 4. Verify our reported numbers yourself

```bash
python report/verify_model.py
```

Runs in seconds, needs no dataset. See [Limitations](#️-known-limitations) for why
this script exists.

---

## 🧩 Modules built

### Core — Crop Disease Detection (mandatory)
Accepts a leaf image, classifies it into one of 27 crop–disease classes (including
`healthy` variants), and returns the label, a confidence score, and precautionary
guidance. Exposed as a Python function, a CLI, and a REST endpoint.

### Bonus B — Smart Irrigation Advisor
`src/irrigation_advisor.py`. Given the diagnosed pathogen plus temperature and
humidity, produces an irrigation action. The logic is explicit and inspectable:

| Condition | Action |
|---|---|
| Fungal pathogen detected (blight, mould, rot, spot, mildew, rust, scab) | Halt overhead irrigation; drip only, to keep the canopy dry |
| Fungal **and** humidity > 70% | Additionally advise plant spacing for airflow |
| Bacterial / viral | Keep soil moisture consistent; do not work the field when foliage is wet |
| Healthy and humidity > 80% | Reduce overhead watering to prevent fungal onset |
| Healthy and temperature > 30 °C | Increase frequency, early morning |

### Bonus E — Farmer Assistant
`src/farmer_assistant.py`. Categorises the detected pathogen (fungal / bacterial /
viral) and returns a grounded action plan. **It is keyed off the model's actual
output, not free generation** — no LLM invents disease facts, which is why §3.2's
"grounded answers score higher" applies here.

### Bonus F — IoT Integration (simulated)
Temperature and humidity are sampled from typical growing-season ranges. §3.2 states
a documented simulated feed is scored equally to hardware. The API returns
`"simulated": true` and **the UI labels it "Simulated — not a real sensor."** It is
never presented as a measurement.

### Supporting — Scan history
SQLite (`data/agrismart_history.db`, zero configuration) logs every scan with
timestamp, filename, label, confidence and prescribed treatment.

### Deliberately not built
**Bonus A (Crop Recommendation).** It needs the farmer's real soil data, and the
Soil Health Card datasets on data.gov.in are state-level aggregates that carry no
public API. A crop recommendation built on a generic Kaggle table would look like a
product while not being one. We left it out rather than ship that.

---

## 📊 Results

Primary metric: **macro-averaged F1**, on a held-out split never seen in training.

| Split | Metric | Value |
|---|---|---|
| **Held-out validation (PlantVillage)** | **Macro-F1** | **0.9005** |
| Held-out validation | Accuracy | 0.9037 |
| Held-out validation | Images | 135 |
| Held-out validation | Distinct classes predicted | 27 / 27 |
| Held-out validation | Classes at F1 = 1.00 | 11 of 27 |
| Lab spot check | Correct | 5 / 5 |
| Field spot check (PlantDoc) | Distinct classes predicted | 10, confidence 0.24–0.85 |

### Confusion matrix

![Confusion matrix](report/confusion_matrix.png)

Per-class precision, recall and F1: [`report/metrics.json`](report/metrics.json).

Weakest classes (small validation support, so treat as indicative):

| Class | F1 | n |
|---|---|---|
| `Potato___Late_blight` | 0.50 | 1 |
| `Apple___Apple_scab` | 0.75 | 3 |
| `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | 0.80 | 2 |
| `Corn_(maize)___Northern_Leaf_Blight` | 0.80 | 6 |
| `Tomato___Late_blight` | 0.80 | 8 |

Regenerate everything above:

```bash
python model/evaluate.py --data <plantvillage_dir>
```

### Lab vs. field — the honest comparison

| Image | Type | Prediction | Confidence |
|---|---|---|---|
| `lab_potato_late_blight.jpg` | Lab | `Potato___Late_blight` ✅ | 99.7% |
| `lab_tomato_early_blight.jpg` | Lab | `Tomato___Early_blight` ✅ | 99.3% |
| `lab_tomato_healthy.jpg` | Lab | `Tomato___healthy` ✅ | 97.5% |
| `lab_corn_common_rust.jpg` | Lab | `Corn_(maize)___Common_rust_` ✅ | 96.5% |
| `lab_grape_black_rot.jpg` | Lab | `Grape___Black_rot` ✅ | 93.2% |
| `tomato_early_blight_field.jpg` | **Field** | `Raspberry___healthy` ❌ | **54.0%** |

Confident and correct on clean lab images; unsure and wrong on a cluttered real-world
photo — **and the confidence says so.** That gap is the actual problem this challenge
is built around, and we are not hiding it.

**We do not report a field macro-F1.** We do not have the organisers' held-out set,
and six images is a spot check, not a metric.

---

## 📁 Dataset & licence

| Dataset | Role | Source | Licence |
|---|---|---|---|
| **PlantVillage** | Train + validation | [spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset) (Hughes & Salathé, 2015) | CC BY-SA 3.0 |
| **PlantDoc** | Field spot check | [pratikkayal/PlantDoc-Dataset](https://github.com/pratikkayal/PlantDoc-Dataset) (Singh et al., CODS-COMAD 2020, arXiv:1911.10317) | CC BY 4.0 |

**Training set:** 675 PlantVillage images — 25 per class across all 27 classes,
balanced. Split 80/20 train/validation with a fixed seed (0), so the split is
reproducible. No image appears in both splits.

Sample images shipped in [`samples/`](samples/) with ground truth documented in
[`samples/README.md`](samples/README.md).

---

## 🏗 Architecture

```
📷 Leaf photo
   │
   ▼
React + Vite + Tailwind  ──── real /health check, no fabricated status
   │  POST /predict (multipart)
   ▼
FastAPI  (src/api.py)
   │
   ├── model/predict.py ── EfficientNet-B0 ── Resize 224 → Normalize(ImageNet)
   │                        27-class head      → softmax → label + confidence
   │
   ├── src/farmer_assistant.py  ── grounded action plan (Bonus E)
   ├── src/irrigation_advisor.py ── irrigation decision (Bonus B) + simulated
   │                                 sensor feed (Bonus F, labelled as such)
   └── src/database.py ── SQLite scan history
```

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, Tailwind CSS 3 |
| Backend | FastAPI + Uvicorn |
| Model | PyTorch, torchvision EfficientNet-B0, Albumentations |
| Storage | SQLite (stdlib, zero config) |
| Metrics | scikit-learn, matplotlib |

**Training approach:** ImageNet-pretrained EfficientNet-B0 with a **frozen** backbone;
a `Linear(1280, 27)` head trained on extracted features (AdamW, lr 3e-3, weight decay
1e-4, label smoothing 0.05, best checkpoint by validation macro-F1). Feature
standardisation is folded into the `Linear` weights so inference needs no extra step.

---

## ⚠️ Known limitations

We list these plainly because a farmer-facing tool that overstates itself is worse
than no tool.

### 1. A defect we found in our own model, and fixed

An earlier checkpoint in this repository was **completely broken**, and we are
documenting it rather than quietly replacing it.

`model/augmentations.py` applies `A.Normalize(ImageNet)`, and the tensor conversion
then divided by **255 again**, crushing every input to roughly `[-0.008, +0.010]` —
numerically almost a black frame. The network saw a black rectangle every time and
learned a single constant answer.

| Input | Old model output |
|---|---|
| All-black rectangle | `Soybean___healthy` 0.9943 |
| Real diseased tomato leaf | `Soybean___healthy` 0.9944 |
| Random noise | `Soybean___healthy` 0.9941 |
| 24 test images, 6 crops | `Soybean___healthy` ×24 |

**0/12 correct on lab images, 0/12 on field images, one distinct prediction across 24
images.** The previously reported 0.9943 validation macro-F1 was **not reproducible**
from those weights.

**Fix:** removed the duplicate `/255` in `predict.py`, `train.py` and `diagnostic.py`;
retrained the classifier head with correct normalization; reset `temperature.json` to
1.0 (the old 1.499 had been fitted against the dead model).

Reproduce the failure and the fix with no dataset: `python report/verify_model.py`

### 2. Small training set
675 images (25/class). PlantVillage has ~54,000. This is what could be fetched and
trained in the remaining window. More data and an unfrozen backbone would improve it
substantially.

### 3. Lab-to-field gap is real and unmeasured
Validation is PlantVillage-only. Published work reports 20–70 point drops on field
imagery, and our spot check is consistent with a large drop. The model is **not**
validated for real field photographs.

### 4. Frozen backbone
Only a linear head was trained. Fine-tuning the backbone is the obvious next step.

### 5. Not field-validated, and not a prescription
No trial with farmers or an extension officer has been run. The treatment strings are
general horticultural guidance, **not dosage prescriptions**. The interface says so
and routes users to the Kisan Call Centre (1800-180-1551) for advice they can act on.

### 6. Simulated sensors
Temperature and humidity are generated, not measured. Permitted under Bonus F, and
labelled "Simulated — not a real sensor" everywhere it appears.

---

## 🎥 Demo & deployment

- **Demo video:** _to be added before submission_
- **Deployed app:** not deployed — runs locally via the instructions above

---

## 📄 Originality declaration

- All work in this repository was committed between **10–15 September 2026**.
- **Datasets:** PlantVillage (Hughes & Salathé, 2015) and PlantDoc (Singh et al.,
  CODS-COMAD 2020). Both cited above with licences.
- **Pretrained backbone:** EfficientNet-B0 ImageNet weights via `torchvision`.
- **Open-source libraries:** PyTorch, torchvision, Albumentations, scikit-learn,
  matplotlib, seaborn, FastAPI, Uvicorn, React, Vite, Tailwind CSS, axios,
  react-router-dom.
- **Baseline reference:** the 0.15 F1 PlantVillage→PlantDoc figure discussed in our
  report is from the PlantDoc paper (arXiv:1911.10317), quoted for comparison only.
- No public notebook or third-party solution was copied wholesale. The training,
  evaluation, inference, API and frontend code here was written by the team.
- AI coding assistants were used during development, as permitted by §8.

---

## 📂 Repository structure

```
├── README.md                    ← you are here
├── requirements.txt
├── model/
│   ├── predict.py               ← predict(image_path) + CLI  (§4.1 interface)
│   ├── train.py                 ← training pipeline
│   ├── evaluate.py              ← regenerates metrics.json + confusion_matrix.png
│   ├── prepare_data.py          ← dataset → manifests
│   ├── augmentations.py         ← field-condition augmentation
│   ├── calibrate.py             ← temperature scaling
│   └── weights/                 ← best_model.pt, label_mapping.json, temperature.json
├── src/
│   ├── api.py                   ← FastAPI (/predict /health /history /irrigation-advice)
│   ├── database.py              ← SQLite scan history
│   ├── irrigation_advisor.py    ← Bonus B + F
│   ├── farmer_assistant.py      ← Bonus E
│   └── frontend/                ← React + Vite + Tailwind
├── report/
│   ├── model_report.md          ← one-page model report (§7.3)
│   ├── metrics.json             ← per-class precision / recall / F1
│   ├── confusion_matrix.png
│   └── verify_model.py          ← independent verification, no dataset needed
├── samples/                     ← 6 test images with documented ground truth
└── tests/
```

---

## 👥 Team

**Hackinators** — SIH 2026 Internal Hackathon, L. J. Institute of Engineering and
Technology [C-433].
