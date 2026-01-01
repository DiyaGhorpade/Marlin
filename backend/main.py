import pandas as pd
import numpy as np
import joblib
import sys
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import subprocess
import socket
import time
from contextlib import asynccontextmanager

# Use modern lifespan events instead of deprecated on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_streamlit()
    load_ml_models()
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
    allow_origins=["*"],
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
species_model_package = None
ocean_model_package = None
fish_stock_model = None
fish_label_encoders = None


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

def load_ml_models():
    """Load all ML models"""
    global species_model_package, ocean_model_package
    global fish_stock_model, fish_label_encoders

    # Load Fish Stock Model
    try:
        model_paths = [
            'fish_catch_model_min.pkl',
            './fish_catch_model_min.pkl',
            '../fish_catch_model_min.pkl',
            os.path.join(os.path.dirname(__file__), 'fish_catch_model_min.pkl'),
        ]

        encoder_paths = [
            'encoders.pkl',
            './encoders.pkl',
            os.path.join(os.path.dirname(__file__), 'encoders.pkl'),
        ]

        for path in model_paths:
            if os.path.exists(path):
                fish_stock_model = joblib.load(path,mmap_mode="r")
                print(f"Fish Stock Model loaded from: {path}")
                break

        for path in encoder_paths:
            if os.path.exists(path):
                fish_label_encoders = joblib.load(path)
                print(f"Fish Label Encoders loaded from: {path}")
                break

        if fish_stock_model is None:
            print("Fish Stock model not loaded")
        if fish_label_encoders is None:
            print("Fish Label Encoders not loaded")

    except Exception as e:
        print(f"❌ Error loading fish stock model: {e}")

    # Load species richness model
    try:
        possible_paths = [
            'indian_species_richness_model.pkl',
            './indian_species_richness_model.pkl',
            '../indian_species_richness_model.pkl',
            os.path.join(os.path.dirname(__file__), 'indian_species_richness_model.pkl'),
        ]
        
        species_loaded = False
        for model_path in possible_paths:
            try:
                if os.path.exists(model_path):
                    species_model_package = joblib.load(model_path)
                    print(f"✅ Species Richness Model loaded from: {model_path}")
                    species_loaded = True
                    break
            except Exception as e:
                print(f"⚠️  Error loading species model from {model_path}: {e}")
        
        if not species_loaded:
            print("❌ Could not load Species Richness model")
            
    except Exception as e:
        print(f"❌ Error loading species model: {e}")

    # Load ocean parameter model
    try:
        ocean_paths = [
            'ocean_prediction_models2.pkl',
            './ocean_prediction_models2.pkl', 
            '../ocean_prediction_models2.pkl',
            os.path.join(os.path.dirname(__file__), 'ocean_prediction_models2.pkl'),
            'ocean_temperature_model_latest2.pkl',
            'ocean_salinity_model_latest2.pkl',
        ]
        
        ocean_loaded = False
        for model_path in ocean_paths:
            try:
                if os.path.exists(model_path):
                    ocean_model_package = joblib.load(model_path)
                    print(f"✅ Ocean Parameter Model loaded from: {model_path}")
                    
                    # Print model structure for debugging
                    if isinstance(ocean_model_package, dict):
                        print(f"🔧 Model keys: {list(ocean_model_package.keys())}")
                        if 'models' in ocean_model_package:
                            print(f"🔧 Available models: {list(ocean_model_package['models'].keys())}")
                        if 'metadata' in ocean_model_package and 'features' in ocean_model_package['metadata']:
                            print(f"🔧 Features: {ocean_model_package['metadata']['features']}")
                    
                    ocean_loaded = True
                    break
            except Exception as e:
                print(f"⚠️  Error loading ocean model from {model_path}: {e}")
        
        if not ocean_loaded:
            print("❌ Could not load Ocean Parameter model")
            
    except Exception as e:
        print(f"❌ Error loading ocean model: {e}")

def encode_input(encoders, field: str, value: str):
    """
    Safely encode categorical inputs using trained encoders
    """
    try:
        encoder = encoders[field]
        if value not in encoder.classes_:
            # Get available values for better error message
            available = list(encoder.classes_[:5])  # Show first 5 examples
            raise ValueError(
                f"Unknown {field}: '{value}'. "
                f"Available values include: {available}... "
                f"(total {len(encoder.classes_)} options)"
            )
        return int(encoder.transform([value])[0])
    except KeyError:
        raise HTTPException(
            status_code=500, 
            detail=f"Encoder for field '{field}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Pydantic models for prediction inputs
class SpeciesPredictionInput(BaseModel):
    latitude: float
    longitude: float
    total_occurrences: Optional[int] = 1
    total_abundance: Optional[int] = 1
    genus_richness: Optional[int] = 1
    family_richness: Optional[int] = 1

class OceanPredictionInput(BaseModel):
    latitude: float
    longitude: float
    depth: float
    uo: Optional[float] = 0.0  # Eastward current
    vo: Optional[float] = 0.0  # Northward current

class FishStockPredictionInput(BaseModel):
    PERIOD: int
    Area: str
    Country: str
    Scientific_Name: str

class SpeciesPredictionResponse(BaseModel):
    predicted_species_richness: int
    biodiversity_level: str
    coordinates: str
    confidence: float
    inputs_used: dict

class OceanPredictionResponse(BaseModel):
    temperature: Optional[float] = None
    salinity: Optional[float] = None
    temperature_level: Optional[str] = None
    salinity_level: Optional[str] = None
    coordinates: str
    model_version: str
    inputs_used: dict
    predictions: dict

class FishStockPredictionResponse(BaseModel):
    predicted_value: float
    inputs_used: dict
    unit: str = "Metric Tonnes"
    model_info: Optional[dict] = None


# --- Dashboard Routes ---
@app.get("/")
def root():
    dashboard_info = f"http://localhost:{DASHBOARD_PORT}" if DASHBOARD_PORT else "Not running"
    return {
        "status": "Marlin ML API is running 🐋", 
        "species_model_loaded": species_model_package is not None,
        "ocean_model_loaded": ocean_model_package is not None,
        "fish_stock_model_loaded": fish_stock_model is not None,
        "dashboard": dashboard_info,
        "endpoints": {
            "species_prediction": "/predict/species-richness",
            "ocean_prediction": "/predict/ocean-parameters",
            "fish_stock_prediction": "/predict/fish-stock-predictor",
            "model_info": "/model/info",
            "health": "/health"
        }
    }

@app.get("/dashboards/biodiversity")
def open_biodiversity_dashboard():
    """Redirects user to the running Streamlit dashboard"""
    if DASHBOARD_PORT is None:
        raise HTTPException(status_code=503, detail="Dashboard is not running")
    return RedirectResponse(url=f"http://localhost:{DASHBOARD_PORT}")

# --- Health & Status ---
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "species_model_loaded": species_model_package is not None,
        "ocean_model_loaded": ocean_model_package is not None,
        "fish_stock_model_loaded": fish_stock_model is not None,
        "encoders_loaded": fish_label_encoders is not None,
        "api_version": "1.0.0",
        "dashboard_port": DASHBOARD_PORT,
        "dashboard_url": f"http://localhost:{DASHBOARD_PORT}" if DASHBOARD_PORT else "Not running"
    }

# --- Species Richness Prediction ---
@app.post("/predict/species-richness", response_model=SpeciesPredictionResponse)
def predict_species_richness(input_data: SpeciesPredictionInput):
    """
    Predict species richness for Indian coastal locations
    """
    if species_model_package is None:
        raise HTTPException(status_code=503, detail="Species Richness ML model not loaded")
    
    # Validate Indian coordinates
    if not (8.0 <= input_data.latitude <= 37.0 and 68.0 <= input_data.longitude <= 97.0):
        raise HTTPException(
            status_code=400, 
            detail="Coordinates must be within Indian boundaries: 8-37°N, 68-97°E"
        )
    
    try:
        # Extract components from model package
        model = species_model_package['model']
        scaler = species_model_package['scaler'] 
        imputer = species_model_package['imputer']
        feature_columns = species_model_package['feature_columns']
        
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
        
        return SpeciesPredictionResponse(
            predicted_species_richness=final_prediction,
            biodiversity_level=biodiversity_level,
            coordinates=f"({input_data.latitude}, {input_data.longitude})",
            confidence=0.914,  # Your model's R² score
            inputs_used=input_data.dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# --- Ocean Parameter Prediction ---
@app.post("/predict/ocean-parameters", response_model=OceanPredictionResponse)
def predict_ocean_parameters(input_data: OceanPredictionInput):
    """
    Predict ocean temperature and salinity using spatial features only (no time parameters)
    """
    if ocean_model_package is None:
        raise HTTPException(status_code=503, detail="Ocean Parameter ML model not loaded")
    
    try:
        print(f"🔧 Ocean model package type: {type(ocean_model_package)}")
        
        # Handle different model structures
        if isinstance(ocean_model_package, dict):
            # New structure with 'models' and 'metadata' keys
            if 'models' in ocean_model_package and 'metadata' in ocean_model_package:
                models = ocean_model_package['models']
                metadata = ocean_model_package['metadata']
                features = metadata.get('features', ['latitude', 'longitude', 'depth', 'uo', 'vo'])
                
                print(f"🔧 Available models: {list(models.keys())}")
                print(f"🔧 Expected features: {features}")
                
                # Create input data with expected features
                input_dict = {
                    'latitude': input_data.latitude,
                    'longitude': input_data.longitude,
                    'depth': input_data.depth,
                    'uo': input_data.uo,
                    'vo': input_data.vo
                }
                
                # Only include features that the model expects
                model_features = {k: v for k, v in input_dict.items() if k in features}
                new_data = pd.DataFrame([model_features])
                
                print(f"🔧 Sending features: {list(new_data.columns)}")
                
                # Make predictions for available models
                predictions = {}
                if 'temperature' in models:
                    temp_pred = models['temperature'].predict(new_data)[0]
                    predictions['temperature'] = round(temp_pred, 2)
                if 'salinity' in models:
                    salinity_pred = models['salinity'].predict(new_data)[0]
                    predictions['salinity'] = round(salinity_pred, 2)
                    
            else:
                # Old structure - direct model access
                raise HTTPException(status_code=500, detail="Unsupported model structure")
        else:
            # Single model case
            raise HTTPException(status_code=500, detail="Single model structure not supported")
        
        # Determine levels for available predictions
        def get_temperature_level(temp):
            if temp < 5: return "Very Cold"
            if temp < 15: return "Cold" 
            if temp < 25: return "Moderate"
            return "Warm"
            
        def get_salinity_level(salinity):
            if salinity < 32: return "Low"
            if salinity < 35: return "Moderate"
            return "High"
        
        response_data = {
            'coordinates': f"({input_data.latitude}, {input_data.longitude})",
            'model_version': metadata.get('version', '1.0'),
            'inputs_used': input_data.dict(),
            'predictions': predictions
        }
        
        # Add temperature data if available
        if 'temperature' in predictions:
            response_data['temperature'] = predictions['temperature']
            response_data['temperature_level'] = get_temperature_level(predictions['temperature'])
        
        # Add salinity data if available  
        if 'salinity' in predictions:
            response_data['salinity'] = predictions['salinity']
            response_data['salinity_level'] = get_salinity_level(predictions['salinity'])
        
        return OceanPredictionResponse(**response_data)
        
    except Exception as e:
        print(f"❌ Detailed error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ocean prediction failed: {str(e)}")

# --- Fish Stock Prediction ---
@app.post("/predict/fish-stock-predictor", response_model=FishStockPredictionResponse)
def predict_fish_stock(input_data: FishStockPredictionInput):
    """
    Predict fish stock quantity (metric tonnes) based on:
    - PERIOD (year)
    - Area (FAO fishing area)
    - Country
    - Scientific_Name (species)
    
    Model expects: [PERIOD, Area_enc, Country_enc, Scientific_Name_enc]
    """
    if fish_stock_model is None or fish_label_encoders is None:
        raise HTTPException(
            status_code=503, 
            detail="Fish stock model or encoders not loaded. Check server logs."
        )

    try:
        # Encode categorical inputs
        area_enc = encode_input(fish_label_encoders, "Area", input_data.Area)
        country_enc = encode_input(fish_label_encoders, "Country", input_data.Country)
        species_enc = encode_input(
            fish_label_encoders, "Scientific_Name", input_data.Scientific_Name
        )

        # Build model input (ORDER MATTERS: PERIOD, Area, Country, Scientific_Name)
        X = np.array([[
            input_data.PERIOD,
            area_enc,
            country_enc,
            species_enc
        ]])

        print(f"🔧 Input features: PERIOD={input_data.PERIOD}, Area_enc={area_enc}, Country_enc={country_enc}, Species_enc={species_enc}")

        # Predict
        prediction = fish_stock_model.predict(X)[0]
        
        # Ensure non-negative prediction
        prediction = max(0, prediction)

        print(f"✅ Prediction: {prediction} MT")

        return FishStockPredictionResponse(
            predicted_value=round(float(prediction), 2),
            inputs_used=input_data.dict(),
            unit="Metric Tonnes",
            model_info={
                "features": ["PERIOD", "Area", "Country", "Scientific_Name"],
                "encoded_values": {
                    "Area": area_enc,
                    "Country": country_enc,
                    "Scientific_Name": species_enc
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# --- Get Available Values for Fish Stock Model ---
@app.get("/fish-stock/available-values")
def get_available_values():
    """
    Get all available values for categorical fields in fish stock model
    """
    if fish_label_encoders is None:
        raise HTTPException(status_code=503, detail="Encoders not loaded")
    
    try:
        return {
            "areas": sorted(fish_label_encoders["Area"].classes_.tolist()),
            "countries": sorted(fish_label_encoders["Country"].classes_.tolist()),
            "species": sorted(fish_label_encoders["Scientific_Name"].classes_.tolist()),
            "total_areas": len(fish_label_encoders["Area"].classes_),
            "total_countries": len(fish_label_encoders["Country"].classes_),
            "total_species": len(fish_label_encoders["Scientific_Name"].classes_)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get values: {str(e)}")


# --- Model Info Endpoints ---
@app.get("/model/info")
def get_model_info():
    """Get information about all loaded ML models"""
    species_info = {}
    ocean_info = {}
    fish_stock_info = {}
    
    if species_model_package is not None:
        species_info = {
            "model_type": "Random Forest Regressor",
            "accuracy": "91.4%",
            "r2_score": 0.914,
            "features_used": len(species_model_package.get('feature_columns', [])),
            "coverage": "Indian coastline (8°-37°N, 68°-97°E)",
            "training_data": "Indian biodiversity records"
        }
    
    if ocean_model_package is not None:
        if isinstance(ocean_model_package, dict) and 'metadata' in ocean_model_package:
            metadata = ocean_model_package['metadata']
            ocean_info = {
                "model_type": "Multiple Regression Models",
                "available_models": list(ocean_model_package.get('models', {}).keys()),
                "features_used": metadata.get('features', ['latitude', 'longitude', 'depth', 'uo', 'vo']),
                "coverage": "Global Ocean",
                "data_source": "CMEMS",
                "version": metadata.get('version', '1.0'),
                "note": "Spatial features only (no time parameters)"
            }
        else:
            ocean_info = {
                "model_type": "Unknown",
                "structure": str(type(ocean_model_package)),
                "note": "Model loaded but structure not recognized"
            }
    
    if fish_stock_model is not None and fish_label_encoders is not None:
        fish_stock_info = {
            "model_type": "Regression Model (Fish Stock Predictor)",
            "features": ["PERIOD", "Area", "Country", "Scientific_Name"],
            "output": "Fish stock quantity in Metric Tonnes",
            "data_source": "FAO Indian Ocean Data",
            "encoders": {
                "areas": len(fish_label_encoders["Area"].classes_),
                "countries": len(fish_label_encoders["Country"].classes_),
                "species": len(fish_label_encoders["Scientific_Name"].classes_)
            }
        }
    
    return {
        "species_richness_model": species_info,
        "ocean_parameter_model": ocean_info,
        "fish_stock_model": fish_stock_info
    }

# --- Test Endpoints ---
@app.get("/test/species-prediction")
def test_species_prediction():
    """Test endpoint for species prediction with Mumbai coordinates"""
    if species_model_package is None:
        raise HTTPException(status_code=503, detail="Species model not loaded")
        
    test_input = SpeciesPredictionInput(
        latitude=19.0760,
        longitude=72.8777,
        total_occurrences=5,
        total_abundance=50,
        genus_richness=3,
        family_richness=2
    )
    return predict_species_richness(test_input)

@app.get("/test/ocean-prediction")
def test_ocean_prediction():
    """Test endpoint for ocean prediction with sample data"""
    if ocean_model_package is None:
        raise HTTPException(status_code=503, detail="Ocean model not loaded")
        
    test_input = OceanPredictionInput(
        latitude=45.5,
        longitude=-125.3,
        depth=10,
        uo=0.1,
        vo=0.05
    )
    return predict_ocean_parameters(test_input)

@app.get("/test/fish-stock-prediction")
def test_fish_stock_prediction():
    """Test endpoint for fish stock prediction with sample data"""
    if fish_stock_model is None or fish_label_encoders is None:
        raise HTTPException(status_code=503, detail="Fish stock model not loaded")
    
    test_input = FishStockPredictionInput(
        PERIOD=2018,
        Area="Indian Ocean, Eastern",
        Country="India",
        Scientific_Name="Katsuwonus pelamis"  # Skipjack tuna
    )
    return predict_fish_stock(test_input)

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
@app.post("/reload-models")
def reload_models():
    """Manually reload all ML models"""
    load_ml_models()
    return {
        "message": "Models reload attempted", 
        "species_model_loaded": species_model_package is not None,
        "ocean_model_loaded": ocean_model_package is not None,
        "fish_stock_model_loaded": fish_stock_model is not None,
        "encoders_loaded": fish_label_encoders is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)