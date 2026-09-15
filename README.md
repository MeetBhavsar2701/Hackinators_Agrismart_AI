# AgriSmart AI - Intelligent Agriculture for a Sustainable Future

AgriSmart AI is a comprehensive, AI-powered agricultural advisory platform designed to solve modern farming challenges. Built for the Smart India Hackathon (SIH), this project combines state-of-the-art Computer Vision with dynamic expert heuristics to provide actionable, real-time insights to farmers.

## 🌟 Key Features & Modules

1. **Core Task: Crop Disease Detection (Computer Vision)**
   - Classifies plant diseases from leaf/crop images across 27 different disease classes.
   - Powered by a fine-tuned **EfficientNet-B0** model pretrained on ImageNet.
   - Robust offline inference deployed via FastAPI.

2. **Bonus Module: Smart Irrigation Advisor**
   - Automatically generates dynamic irrigation tips tailored to the specific crop and diagnosed disease.
   - Integrates synthetic weather heuristics (temperature, humidity) to alter advice (e.g., advising drip irrigation to halt fungal spread in high humidity).

3. **Bonus Module: AI Farmer Assistant**
   - Provides a detailed, actionable treatment plan based on the exact pathogen detected.
   - Categorizes pathogens (Fungal, Viral, Bacterial) and gives immediate offline remediation strategies (chemical and organic).

4. **Robust Scan History Database**
   - Uses a local **SQLite** database (`data/agrismart_history.db`) to seamlessly log every scan.
   - Tracks timestamps, AI confidence scores, disease labels, and prescribed treatments for easy historical lookup.

5. **Modern React UI (Stitch UI)**
   - Beautiful, fully-responsive frontend built with **React, Vite, and Tailwind CSS**.
   - Features a seamless image upload interface, a highly-detailed diagnosis "Result" dashboard with dynamic AI insights, and a dedicated "Scan History" ledger.

---

## 🚀 Setup & Run Instructions

### Prerequisites
- Python 3.9+
- Node.js (v18+)
- npm

### 1. Backend Setup (FastAPI & AI Models)
```bash
# Clone the repository
git clone https://github.com/MeetBhavsar2701/Hackinators_Agrismart_AI.git
cd Hackinators_Agrismart_AI

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI Server
python src/api.py
```
The backend API will run at `http://localhost:8000`. You can view the interactive Swagger documentation at `http://localhost:8000/docs`.

### 2. Frontend Setup (React/Vite)
Open a **new terminal window** and run:
```bash
cd Hackinators_Agrismart_AI/src/frontend

# Install Node dependencies
npm install

# Start the React Development Server
npm run dev
```
The frontend will run at `http://localhost:5173`. Open this link in your browser to interact with the AgriSmart AI web app!

---

## 📊 Dataset & Model Performance

**Core Dataset**: 
- **Training/Validation**: PlantVillage dataset (lab-condition leaf images, uniform background).
- **Test Set**: Provided PlantDoc-style real-world field-condition images.

**Reported Metrics** (current model, measured — see [`report/model_report.md`](report/model_report.md)):

| Split | Metric | Value |
|---|---|---|
| Held-out validation (PlantVillage, lab) | Macro-F1 | **0.9005** |
| Held-out validation (PlantVillage, lab) | Accuracy | **0.9037** (135 images) |
| Lab spot check | Correct | **12/12** |
| Field spot check (PlantDoc) | Distinct classes predicted | **10** of 27, confidence 0.24–0.85 |

Field-set macro-F1 is **not** formally reported: we do not have the organisers'
held-out set, and a 12-image spot check is too small to quote as a metric. We
would rather report nothing than a number we cannot stand behind.

### A defect we found and fixed

The earlier checkpoint in this repository was **completely broken** and we are
documenting it rather than quietly replacing it.

`model/augmentations.py` applies `A.Normalize(ImageNet)`, and the tensor
conversion then divided by 255 **again**, crushing every input to roughly
`[-0.008, +0.010]`. The network received a near-black frame for every image and
learned to emit a constant answer. Verified: an all-black rectangle and a real
diseased tomato leaf both returned `Soybean___healthy` at `0.9943`. It scored
**0/12 on lab images and 0/12 on field images**, with **one** distinct
prediction across 24 test images. The previously reported 0.9943 validation
macro-F1 was not reproducible from the committed weights.

Reproduce the failure mode yourself, no dataset needed:

```bash
python report/verify_model.py
```

**The fix:** removed the duplicate `/255` in `predict.py`, `train.py` and
`diagnostic.py`, then retrained the classifier head on 675 PlantVillage images
(25 × 27 classes) over a frozen ImageNet EfficientNet-B0 backbone with correct
normalization. `temperature.json` was reset to 1.0 — the old 1.499 was fitted
against the dead model.

> **Confusion matrix and per-class metrics are not included.** `model/evaluate.py`
> generates them but needs the dataset manifests and raw images, which are not
> vendored here. To regenerate:
> `python model/prepare_data.py && python model/evaluate.py`

---

## 🏗️ Architecture Overview

- **Frontend**: React + Vite + Tailwind CSS. Hosted locally via Vite dev server.
- **Backend API**: FastAPI framework serving the PyTorch Computer Vision model and the SQLite database layer.
- **Database**: SQLite3 built-in to Python (Zero configuration required!).
- **AI/ML**: PyTorch, Torchvision (EfficientNet-B0), Albumentations for robust field-condition augmentations.

## 📄 Originality Declaration

- All work in this repository was committed between **10–15 September 2026**.
- **Datasets:** PlantVillage (Hughes & Salathé, 2015 — https://github.com/spMohanty/PlantVillage-Dataset)
  and PlantDoc (Singh et al., CODS-COMAD 2020 — https://github.com/pratikkayal/PlantDoc-Dataset).
- **Pretrained backbone:** EfficientNet-B0 ImageNet weights via `torchvision`.
- **Open-source libraries:** PyTorch, torchvision, Albumentations, scikit-learn,
  FastAPI, Uvicorn, React, Vite, Tailwind CSS, axios, react-router-dom.
- **Baseline reference:** the 0.15 F1 PlantVillage→PlantDoc figure cited above is
  from the PlantDoc paper (arXiv:1911.10317); it is quoted for comparison only.
- No public notebook or third-party solution was copied wholesale. Training,
  evaluation, inference, API, and frontend code in this repository were written
  by the team. AI coding assistants were used during development.

## 🔗 Submission Links
- **Demo Video**: _(not yet recorded — to be added before submission)_
- **Deployed App**: _(not deployed — runs locally via the instructions above)_