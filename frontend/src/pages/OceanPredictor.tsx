import React, { useState } from 'react';
import { Link } from 'react-router-dom';

// API function
const predictOceanParameters = async (data: any) => {
  const response = await fetch('http://localhost:8000/predict/ocean-parameters', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Prediction failed');
  }
  
  return response.json();
};

const OceanPredictor: React.FC = () => {
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    depth: '10',
    uo: '0.1',
    vo: '0.05',
  });
  
  const [prediction, setPrediction] = useState<{ 
    temperature: number | null; 
    salinity: number | null;
    temperature_level?: string;
    salinity_level?: string;
    coordinates?: string;
    model_version?: string;
  }>({ 
    temperature: null, 
    salinity: null 
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(null); // Clear error when user starts typing
  };

  const setLocation = (lat: number, lon: number) => {
    setFormData({
      ...formData,
      latitude: lat.toString(),
      longitude: lon.toString()
    });
    setError(null); // Clear error when location is set
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Real API call
      const result = await predictOceanParameters({
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        depth: parseFloat(formData.depth),
        uo: parseFloat(formData.uo),
        vo: parseFloat(formData.vo),
      });
      
      setPrediction({
        temperature: result.temperature,
        salinity: result.salinity,
        temperature_level: result.temperature_level,
        salinity_level: result.salinity_level,
        coordinates: result.coordinates,
        model_version: result.model_version
      });
      setLoading(false);
      
    } catch (error) {
      console.error('Prediction failed:', error);
      setError(error instanceof Error ? error.message : 'Prediction failed');
      setLoading(false);
      
      // Fallback to mock data for demo if API fails
      setTimeout(() => {
        const lat = parseFloat(formData.latitude) || 45.5;
        let baseTemp = 15; // Moderate default
        if (lat > 50) baseTemp = 5;  // Cold regions
        if (lat < 20) baseTemp = 25; // Tropical regions
        
        const mockTemp = (baseTemp + (Math.random() * 10 - 5)).toFixed(1);
        
        let baseSalinity = 34.5; // Ocean average
        if (lat > 50) baseSalinity = 32.5;  // Polar regions (lower salinity)
        if (lat < 20) baseSalinity = 35.5;  // Tropical regions (higher salinity)
        
        const mockSalinity = (baseSalinity + (Math.random() * 2 - 1)).toFixed(1);
        
        setPrediction({
          temperature: parseFloat(mockTemp),
          salinity: parseFloat(mockSalinity),
          temperature_level: getTemperatureLevel(parseFloat(mockTemp)).level,
          salinity_level: getSalinityLevel(parseFloat(mockSalinity)).level,
          coordinates: `(${formData.latitude}, ${formData.longitude})`,
          model_version: '1.0'
        });
      }, 500);
    }
  };

  const getTemperatureLevel = (temp: number) => {
    if (temp < 5) return { level: "Very Cold", color: "text-blue-600", bg: "bg-blue-100" };
    if (temp < 15) return { level: "Cold", color: "text-cyan-600", bg: "bg-cyan-100" };
    if (temp < 25) return { level: "Moderate", color: "text-green-600", bg: "bg-green-100" };
    return { level: "Warm", color: "text-orange-600", bg: "bg-orange-100" };
  };

  const getSalinityLevel = (salinity: number) => {
    if (salinity < 32) return { level: "Low", color: "text-blue-600", bg: "bg-blue-100" };
    if (salinity < 35) return { level: "Moderate", color: "text-green-600", bg: "bg-green-100" };
    return { level: "High", color: "text-purple-600", bg: "bg-purple-100" };
  };

  // Use API levels if available, otherwise calculate from values
  const tempInfo = prediction.temperature ? getTemperatureLevel(prediction.temperature) : null;
  const salinityInfo = prediction.salinity ? getSalinityLevel(prediction.salinity) : null;

  const displayTempLevel = prediction.temperature_level || tempInfo?.level;
  const displaySalinityLevel = prediction.salinity_level || salinityInfo?.level;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-blue-600">MARLIN</span>
              <div className="hidden md:ml-6 md:flex md:space-x-8">
                <Link to="/" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">Home</Link>
                <Link to="/chatbot" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">AI Chatbot</Link>
                <Link to="/dashboards" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">Dashboards</Link>
                <Link to="/models" className="border-b-2 border-blue-500 text-blue-600 px-3 py-2 text-sm font-medium">ML Models</Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Link to="/models" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to ML Models
        </Link>

        {/* Model Header */}
        <div className="bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl p-8 text-white mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Ocean Parameter Predictor</h1>
              <p className="text-cyan-100 text-lg mb-4">Predict sea temperature and salinity with realistic accuracy using Linear Regression</p>
              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">53.3%</div>
                  <div className="text-cyan-100 text-sm">Temperature R²</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">53.1%</div>
                  <div className="text-cyan-100 text-sm">Salinity R²</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">±0.33°C</div>
                  <div className="text-cyan-100 text-sm">Temp MAE</div>
                </div>
              </div>
            </div>
            <div className="text-6xl opacity-80">
              <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Prediction Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Predict Ocean Parameters</h2>
              
              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center">
                    <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span className="text-red-800 text-sm">{error}</span>
                  </div>
                  <p className="text-red-600 text-xs mt-1">Using demo data as fallback</p>
                </div>
              )}
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Coordinates */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Latitude (°N)</label>
                    <input 
                      type="number" 
                      name="latitude"
                      value={formData.latitude}
                      onChange={handleInputChange}
                      step="0.0001" 
                      min="-90" 
                      max="90" 
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., 45.5" 
                      required 
                    />
                    <p className="text-xs text-gray-500 mt-1">Southern hemisphere: negative values</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Longitude (°E)</label>
                    <input 
                      type="number" 
                      name="longitude"
                      value={formData.longitude}
                      onChange={handleInputChange}
                      step="0.0001" 
                      min="-180" 
                      max="180"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., -125.3" 
                      required 
                    />
                    <p className="text-xs text-gray-500 mt-1">Western hemisphere: negative values</p>
                  </div>
                </div>

                {/* Ocean Parameters */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Depth (meters)</label>
                    <input 
                      type="number" 
                      name="depth"
                      value={formData.depth}
                      onChange={handleInputChange}
                      min="0" 
                      max="1000"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Surface: 0-50m</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Eastward Current (m/s)</label>
                    <input 
                      type="number" 
                      name="uo"
                      value={formData.uo}
                      onChange={handleInputChange}
                      step="0.01"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Positive: eastward flow</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Northward Current (m/s)</label>
                    <input 
                      type="number" 
                      name="vo"
                      value={formData.vo}
                      onChange={handleInputChange}
                      step="0.01"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Positive: northward flow</p>
                  </div>
                </div>

                <button 
                  type="submit" 
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition duration-200 disabled:opacity-50"
                >
                  {loading ? (
                    <div className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Predicting...
                    </div>
                  ) : (
                    'Predict Ocean Parameters'
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Results & Info */}
          <div className="space-y-6">
            {/* Results Card */}
            {prediction.temperature && prediction.salinity && (
              <div className="bg-white rounded-xl shadow-sm border p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Prediction Results</h3>
                {prediction.model_version && (
                  <div className="mb-3 text-sm text-gray-500">
                    Model v{prediction.model_version} • {error ? 'Demo Data' : 'Live Prediction'}
                  </div>
                )}
                <div className="space-y-4">
                  {/* Temperature Result */}
                  <div className="text-center p-4 border rounded-lg">
                    <div className={`text-4xl font-bold ${tempInfo?.color} mb-2`}>
                      {prediction.temperature}°C
                    </div>
                    <div className="text-lg font-medium text-gray-700 mb-2">Temperature</div>
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${tempInfo?.bg} ${tempInfo?.color}`}>
                      {displayTempLevel}
                    </div>
                  </div>

                  {/* Salinity Result */}
                  <div className="text-center p-4 border rounded-lg">
                    <div className={`text-4xl font-bold ${salinityInfo?.color} mb-2`}>
                      {prediction.salinity} PSU
                    </div>
                    <div className="text-lg font-medium text-gray-700 mb-2">Salinity</div>
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${salinityInfo?.bg} ${salinityInfo?.color}`}>
                      {displaySalinityLevel}
                    </div>
                  </div>

                  <div className="text-sm text-gray-600 text-center">
                    Coordinates: <span className="font-mono">{prediction.coordinates || `(${formData.latitude}, ${formData.longitude})`}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Model Info */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">About This Model</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Algorithm</span>
                  <span className="font-medium">Linear Regression</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Data Source</span>
                  <span className="font-medium">Copernicus</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Temperature R²</span>
                  <span className="font-medium">0.533</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Salinity R²</span>
                  <span className="font-medium">0.531</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Features Used</span>
                  <span className="font-medium">9 parameters</span>
                </div>
              </div>
            </div>

            {/* Model Performance Info */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Model Performance</h3>
              <p className="text-sm text-gray-600 mb-3">
                This Linear Regression model explains <strong>53% of the variance</strong> in ocean parameters - realistic for complex ocean processes.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• <strong>Temperature MAE:</strong> ±0.33°C</li>
                <li>• <strong>Salinity MAE:</strong> ±1.24 PSU</li>
                <li>• <strong>Cross-validation:</strong> Consistent results</li>
                <li>• <strong>No overfitting:</strong> Honest predictions</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OceanPredictor;