import os
import tempfile
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn

# Add the parent directory to sys.path to import model.predict
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from model.predict import predict

app = FastAPI(title="AgriSmart AI API", description="Crop Disease Prediction API")

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
    try:
        # Save uploaded file to a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=Path(file.filename).suffix)
        os.close(fd)
        
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
            
        # Run prediction
        result = predict(temp_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
