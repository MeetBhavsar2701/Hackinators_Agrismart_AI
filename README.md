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

**Reported Metrics**:
- **Validation Set (PlantVillage, lab conditions)**: Macro-F1: `0.9943`
- **Field Test Set**: Macro-F1: `0.0690`

The field score is **below** the 0.15 F1 PlantVillage→PlantDoc baseline reported
in the PlantDoc paper. We report it as-is rather than leading with the lab number.

We traced the primary cause to a **verified preprocessing defect**: ImageNet
normalization is applied in `model/augmentations.py`, and the tensor conversion
then divides by 255 a second time (`model/train.py:39`, `model/predict.py:90`,
`diagnostic.py:45`). This is consistent across training and inference — which is
why lab validation still converged — but it neutralises the ImageNet pretrained
features and drives the field-set collapse. The fix is identified but requires
retraining, which we could not complete within the submission window. The
existing weights and preprocessing are left intact and mutually consistent.

Full analysis: **[`report/model_report.md`](report/model_report.md)**.

> **Confusion matrix and per-class metrics are not included.** `model/evaluate.py`
> generates them, but it requires the dataset manifests and raw images, which are
> not vendored in this repository. We chose not to publish reconstructed numbers.
> To regenerate: `python model/prepare_data.py && python model/evaluate.py`
> (writes `report/metrics.json` and `report/confusion_matrix.png`).

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