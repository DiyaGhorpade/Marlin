from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from typing import Optional
import subprocess
import os
import socket
import time
from contextlib import asynccontextmanager

# Use modern lifespan events instead of deprecated on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_streamlit()
    load_ml_model()
    yield
    # Shutdown (if needed)
    pass

app = FastAPI(
    title="Marlin ML API", 
    description="Machine Learning Models for Marine Biodiversity",
    lifespan=lifespan
)

# Allow requests from your React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your React URL, e.g. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_available_port(start_port=8501, max_port=8510):
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

# Global variables
DASHBOARD_PORT = None
model_package = None

def start_streamlit():
    """Start Streamlit dashboard"""
    global DASHBOARD_PORT
    
    try:
        # Find available port
        DASHBOARD_PORT = find_available_port()
        if DASHBOARD_PORT is None:
            print("❌ No available ports found for Streamlit dashboard")
            return
            
        # Check if Streamlit is already running
        try:
            import requests
            response = requests.get(f"http://localhost:{DASHBOARD_PORT}", timeout=2)
            print(f"✅ Streamlit dashboard already running on port {DASHBOARD_PORT}")
            return
        except:
            pass
        
        # Run streamlit in background
        subprocess.Popen(
            ["streamlit", "run", "dashboard.py", "--server.port", str(DASHBOARD_PORT), "--server.headless", "true"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        print(f"✅ Streamlit dashboard started on port {DASHBOARD_PORT}")
        
        # Wait a bit for Streamlit to start
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def load_ml_model():
    """Load the ML model with correct path"""
    global model_package
    
    try:
        # Try different possible paths for the model file
        possible_paths = [
            'indian_species_richness_model.pkl',  # Same directory
            './indian_species_richness_model.pkl',  # Same directory
            '../indian_species_richness_model.pkl',  # Parent directory
            os.path.join(os.path.dirname(__file__), 'indian_species_richness_model.pkl'),  # Absolute path
        ]
        
        model_loaded = False
        for model_path in possible_paths:
            try:
                if os.path.exists(model_path):
                    model_package = joblib.load(model_path)
                    print(f"✅ ML Model loaded successfully from: {model_path}")
                    model_loaded = True
                    break
                else:
                    print(f"⚠️  Model not found at: {model_path}")
            except Exception as e:
                print(f"⚠️  Error loading from {model_path}: {e}")
        
        if not model_loaded:
            print("❌ Could not load ML model from any path")
            # List files in current directory to help debug
            print("📁 Files in current directory:")
            for file in os.listdir('.'):
                print(f"   - {file}")
            
    except Exception as e:
        print(f"❌ Error loading model: {e}")

# Pydantic model for prediction input
class PredictionInput(BaseModel):
    latitude: float
    longitude: float
    total_occurrences: Optional[int] = 1
    total_abundance: Optional[int] = 1
    genus_richness: Optional[int] = 1
    family_richness: Optional[int] = 1

class PredictionResponse(BaseModel):
    predicted_species_richness: int
    biodiversity_level: str
    coordinates: str
    confidence: float
    inputs_used: dict

# --- Dashboard Routes ---
@app.get("/")
def root():
    dashboard_info = f"http://localhost:{DASHBOARD_PORT}" if DASHBOARD_PORT else "Not running"
    return {
        "status": "Marlin ML API is running 🐋", 
        "model_loaded": model_package is not None,
        "dashboard": dashboard_info,
        "current_directory": os.getcwd()
    }

@app.get("/dashboards/biodiversity")
def open_biodiversity_dashboard():
    """Redirects user to the running Streamlit dashboard"""
    if DASHBOARD_PORT is None:
        raise HTTPException(status_code=503, detail="Dashboard is not running")
    return RedirectResponse(url=f"http://localhost:{DASHBOARD_PORT}")

# --- ML Model Routes ---
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "model_loaded": model_package is not None,
        "api_version": "1.0.0",
        "dashboard_port": DASHBOARD_PORT,
        "dashboard_url": f"http://localhost:{DASHBOARD_PORT}" if DASHBOARD_PORT else "Not running"
    }

@app.post("/predict/species-richness", response_model=PredictionResponse)
def predict_species_richness(input_data: PredictionInput):
    """
    Predict species richness for Indian coastal locations
    """
    if model_package is None:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    # Validate Indian coordinates
    if not (8.0 <= input_data.latitude <= 37.0 and 68.0 <= input_data.longitude <= 97.0):
        raise HTTPException(
            status_code=400, 
            detail="Coordinates must be within Indian boundaries: 8-37°N, 68-97°E"
        )
    
    try:
        # Extract components from model package
        model = model_package['model']
        scaler = model_package['scaler'] 
        imputer = model_package['imputer']
        feature_columns = model_package['feature_columns']
        
        # Create feature array
        features = np.array([[
            input_data.latitude,
            input_data.longitude,
            np.abs(input_data.latitude),
            input_data.latitude ** 2,
            input_data.longitude ** 2,
            1 if np.abs(input_data.latitude) < 23.5 else 0,
            input_data.total_occurrences,
            input_data.total_abundance,
            input_data.genus_richness,
            input_data.family_richness
        ]])
        
        # Handle feature dimension mismatch
        if features.shape[1] < len(feature_columns):
            base_features = features
            additional_features = np.full((1, len(feature_columns) - base_features.shape[1]), np.median(base_features))
            features = np.hstack([base_features, additional_features])
        
        # Preprocess and predict
        features_imputed = imputer.transform(features)
        features_scaled = scaler.transform(features_imputed)
        prediction = model.predict(features_scaled)[0]
        
        # Ensure positive integer
        final_prediction = max(1, round(prediction))
        
        # Determine biodiversity level
        if final_prediction < 5:
            biodiversity_level = "Low"
        elif final_prediction < 15:
            biodiversity_level = "Moderate"
        elif final_prediction < 25:
            biodiversity_level = "High"
        else:
            biodiversity_level = "Very High"
        
        return PredictionResponse(
            predicted_species_richness=final_prediction,
            biodiversity_level=biodiversity_level,
            coordinates=f"({input_data.latitude}, {input_data.longitude})",
            confidence=0.914,  # Your model's R² score
            inputs_used=input_data.dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/model/info")
def get_model_info():
    """Get information about the loaded ML model"""
    if model_package is None:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    return {
        "model_type": "Random Forest Regressor",
        "accuracy": "91.4%",
        "r2_score": 0.914,
        "features_used": len(model_package['feature_columns']),
        "feature_names": model_package['feature_columns'],
        "coverage": "Indian coastline (8°-37°N, 68°-97°E)",
        "training_data": "Indian biodiversity records"
    }

# Example test endpoint
@app.get("/test/prediction")
def test_prediction():
    """Test endpoint with Mumbai coordinates"""
    if model_package is None:
        raise HTTPException(status_code=503, detail="ML model not loaded")
        
    test_input = PredictionInput(
        latitude=19.0760,
        longitude=72.8777,
        total_occurrences=5,
        total_abundance=50,
        genus_richness=3,
        family_richness=2
    )
    return predict_species_richness(test_input)

# --- Dashboard Status ---
@app.get("/dashboards/status")
def dashboard_status():
    """Check if Streamlit dashboard is running"""
    if DASHBOARD_PORT is None:
        return {
            "dashboard_running": False,
            "status": "Dashboard is not running",
            "port": None
        }
    
    try:
        import requests
        response = requests.get(f"http://localhost:{DASHBOARD_PORT}", timeout=5)
        return {
            "dashboard_running": True,
            "status": f"Dashboard is running on port {DASHBOARD_PORT}",
            "url": f"http://localhost:{DASHBOARD_PORT}",
            "port": DASHBOARD_PORT
        }
    except:
        return {
            "dashboard_running": False,
            "status": f"Dashboard failed to start on port {DASHBOARD_PORT}",
            "port": DASHBOARD_PORT
        }

# Manual model reload endpoint
@app.post("/reload-model")
def reload_model():
    """Manually reload the ML model"""
    load_ml_model()
    return {"message": "Model reload attempted", "model_loaded": model_package is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)