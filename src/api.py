import os
import tempfile
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add the parent directory and model directory to sys.path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "model"))

from model.predict import predict
from src.database import save_prediction, get_history
from src.irrigation_advisor import get_irrigation_advice
from src.farmer_assistant import get_expert_advice

app = FastAPI(title="AgriSmart AI API", description="Crop Disease Prediction API")

# Add CORS so React frontend can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AdviceRequest(BaseModel):
    class_label: str
    temperature: float = None
    humidity: float = None

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
    temp_path = None
    try:
        # Save uploaded file to a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=Path(file.filename).suffix)
        os.close(fd)
        
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
            
        # Run prediction
        result = predict(temp_path)
        
        # Save to history DB
        save_prediction(
            image_filename=file.filename,
            class_label=result.get("class_label", "Unknown"),
            confidence=result.get("confidence", 0.0),
            precaution=result.get("precaution", "")
        )
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/history")
def history_endpoint():
    try:
        return get_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/irrigation-advice")
def irrigation_endpoint(req: AdviceRequest):
    try:
        return get_irrigation_advice(req.class_label, req.temperature, req.humidity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/expert-advice")
def expert_endpoint(req: AdviceRequest):
    try:
        return get_expert_advice(req.class_label)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # reload=False: the reloader subprocess does not inherit the sys.path
    # entries set above, which breaks the model/ and src/ imports.
    uvicorn.run(app, host="0.0.0.0", port=8000)
