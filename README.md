# Hackinators_Agrismart_AI

An AI-powered crop disease prediction and agricultural assistant platform.

## Quick Start: Predicting Crop Diseases

Once the models are trained (or downloaded into `model/weights/`), you can start using the prediction API.

### 1. Setup the Environment
```bash
# Clone the repository
git clone https://github.com/MeetBhavsar2701/Hackinators_Agrismart_AI.git
cd Hackinators_Agrismart_AI
git checkout feature/predict-interface

# Install all dependencies
pip install -r requirements.txt
```

### 2. Run the Prediction API
Start the FastAPI server:
```bash
python src/api.py
```
The API will be available at `http://localhost:8000`. You can view the interactive documentation at `http://localhost:8000/docs`.

### 3. Test the API
Use `curl` to upload an image and get a prediction:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/plantdoc/valid/images/sample_leaf.jpg;type=image/jpeg"
```

### CLI Prediction
You can also use the CLI directly:
```bash
python model/predict.py --image data/plantdoc/valid/images/sample_leaf.jpg
```