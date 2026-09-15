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
- **Validation Set**: Macro-F1: `0.9943`
- **Field Test Set**: Macro-F1: `0.0690` (Note: Demonstrates expected real-world domain shift from lab conditions, verified via rigorous diagnostic tests).
*A confusion matrix is available in `report/confusion_matrix.png` and detailed per-class metrics in `report/metrics.json`.*

---

## 🏗️ Architecture Overview

- **Frontend**: React + Vite + Tailwind CSS. Hosted locally via Vite dev server.
- **Backend API**: FastAPI framework serving the PyTorch Computer Vision model and the SQLite database layer.
- **Database**: SQLite3 built-in to Python (Zero configuration required!).
- **AI/ML**: PyTorch, Torchvision (EfficientNet-B0), Albumentations for robust field-condition augmentations.

## 🔗 Submission Links
- **Demo Video**: [Link to YouTube Demo]
- **Deployed App**: [Link to Live App]