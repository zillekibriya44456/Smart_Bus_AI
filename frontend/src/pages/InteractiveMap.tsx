import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, Circle } from 'react-leaflet';
import L from 'leaflet';
import { useNavigate } from 'react-router-dom';
import { getBusStops, analyzeCoordinates, optimizeLocation } from '../services/api';
import { Loader2, Crosshair, Map as MapIcon, Star, AlertCircle } from 'lucide-react';
import { OptimizationTable } from '../components/OptimizationTable';

// Fix for default leaflet markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const createIcon = (color: string) => new L.Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const createStarIcon = () => new L.Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png`,
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [35, 51], // Larger for star/best
  iconAnchor: [17, 51],
  popupAnchor: [1, -34],
});

const greenIcon = createIcon('green');
const yellowIcon = createIcon('yellow');
const redIcon = createIcon('red');
const blueIcon = createIcon('blue');
const goldIcon = createStarIcon();

const MapClickDetector = ({ onLocationSelect, mode }: { onLocationSelect: (lat: number, lon: number) => void, mode: string }) => {
  useMapEvents({
    click(e) {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

export const InteractiveMap: React.FC = () => {
  const navigate = useNavigate();
  const [stops, setStops] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Modes
  const [mode, setMode] = useState<'single' | 'optimize'>('single');

  // Single Mode State
  const [selectedLocation, setSelectedLocation] = useState<{lat: number, lon: number} | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  // Optimize Mode State
  const [optCenter, setOptCenter] = useState<{lat: number, lon: number} | null>(null);
  const [radiusKm, setRadiusKm] = useState<number>(1);
  const [optimizing, setOptimizing] = useState(false);
  const [optCandidates, setOptCandidates] = useState<any[]>([]);

  const defaultCenter: [number, number] = [13.0, 77.5];

  useEffect(() => {
    getBusStops()
      .then(data => {
        const validStops = data.filter((s: any) => s.Latitude && s.Longitude);
        setStops(validStops);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleLocationSelect = (lat: number, lon: number) => {
    if (mode === 'single') {
      setSelectedLocation({ lat, lon });
    } else {
      setOptCenter({ lat, lon });
      setOptCandidates([]); // Clear old results
    }
  };

  const handleAnalyzeSingle = async () => {
    if (!selectedLocation) return;
    setAnalyzing(true);
    setErrorMsg(null);
    try {
      const result = await analyzeCoordinates(selectedLocation.lat, selectedLocation.lon);
      navigate('/results', { state: { result, input: { ...selectedLocation } } });
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
      setAnalyzing(false);
    }
  };

  const handleOptimize = async () => {
    if (!optCenter) return;
    setOptimizing(true);
    setErrorMsg(null);
    try {
      const result = await optimizeLocation(optCenter.lat, optCenter.lon, radiusKm);
      setOptCandidates(result.Candidates || []);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Optimization failed. Please try again.');
    } finally {
      setOptimizing(false);
    }
  };

  const getMarkerIcon = (category: string) => {
    if (category.includes('Highly') || category === 'Suitable') return greenIcon;
    if (category.includes('Moderate') || category.includes('Improvement')) return yellowIcon;
    return redIcon;
  };

  if (loading) {
    return <div className="flex flex-col items-center justify-center h-[600px]"><Loader2 className="animate-spin text-primary" size={48} /><p className="text-slate-400 mt-4">Loading Data...</p></div>;
  }

  const ErrorBanner = errorMsg ? (
    <div className="flex items-center gap-2 bg-red-900/40 border border-red-700 text-red-300 rounded-lg px-4 py-3 text-sm">
      <AlertCircle size={16} className="flex-shrink-0" />
      <span>{errorMsg}</span>
      <button onClick={() => setErrorMsg(null)} className="ml-auto text-red-400 hover:text-red-200">✕</button>
    </div>
  ) : null;

  return (
    <div className="space-y-6">
      {ErrorBanner}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Interactive GIS Map</h1>
          <p className="text-slate-400">
            {mode === 'single' 
              ? "Click to drop a pin and perform a spatial suitability analysis."
              : "Click to set a center point, then optimize the area to find the best candidate locations."}
          </p>
        </div>
        
        {/* Mode Toggle */}
        <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700">
          <button 
            onClick={() => { setMode('single'); setOptCandidates([]); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${mode === 'single' ? 'bg-primary text-white' : 'text-slate-400 hover:text-white'}`}
          >
            <MapIcon size={16} /> Analyze Single
          </button>
          <button 
            onClick={() => { setMode('optimize'); setSelectedLocation(null); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${mode === 'optimize' ? 'bg-primary text-white' : 'text-slate-400 hover:text-white'}`}
          >
            <Crosshair size={16} /> Optimize Area
          </button>
        </div>
      </div>

      <div className="bg-card p-4 rounded-2xl border border-slate-800 relative z-0">
        <MapContainer center={defaultCenter} zoom={11} style={{ height: '600px', width: '100%', borderRadius: '0.75rem' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          <MapClickDetector onLocationSelect={handleLocationSelect} mode={mode} />

          {/* Render Existing Stops if not overcrowded by optimization */}
          {optCandidates.length === 0 && stops.map((stop, idx) => (
            <Marker key={idx} position={[stop.Latitude, stop.Longitude]} icon={getMarkerIcon(stop.Suitability_Category)}>
              <Popup>
                <div className="text-slate-800">
                  <h3 className="font-bold text-lg mb-1">{stop.Stop_ID}</h3>
                  <p className="m-0 text-sm"><b>Score:</b> {stop.Suitability_Score.toFixed(1)}</p>
                  <p className="m-0 text-sm"><b>Category:</b> {stop.Suitability_Category}</p>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Single Mode Marker */}
          {mode === 'single' && selectedLocation && (
            <Marker position={[selectedLocation.lat, selectedLocation.lon]} icon={blueIcon}>
              <Popup autoPan={false}>
                <div className="text-center p-2">
                  <h3 className="font-bold text-slate-800 mb-2">Selected Location</h3>
                  <button 
                    onClick={handleAnalyzeSingle}
                    disabled={analyzing}
                    className="w-full bg-primary hover:bg-blue-600 text-white font-bold py-2 px-4 rounded text-sm disabled:opacity-50 transition-colors"
                  >
                    {analyzing ? 'Analyzing...' : 'Analyze Location'}
                  </button>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Optimize Mode UI */}
          {mode === 'optimize' && optCenter && (
            <>
              <Marker position={[optCenter.lat, optCenter.lon]} icon={blueIcon}>
                <Popup autoPan={false}>
                  <div className="text-center p-2 min-w-[200px]">
                    <h3 className="font-bold text-slate-800 mb-2">Search Area Center</h3>
                    
                    <div className="mb-3 text-left">
                      <label className="block text-xs font-bold text-slate-500 mb-1">Search Radius:</label>
                      <select 
                        value={radiusKm} 
                        onChange={(e) => setRadiusKm(Number(e.target.value))}
                        className="w-full border border-slate-300 rounded px-2 py-1 text-sm bg-white text-slate-800"
                      >
                        <option value={1}>1 km</option>
                        <option value={2}>2 km</option>
                        <option value={5}>5 km</option>
                      </select>
                    </div>

                    <button 
                      onClick={handleOptimize}
                      disabled={optimizing}
                      className="w-full bg-primary hover:bg-blue-600 text-white font-bold py-2 px-4 rounded text-sm disabled:opacity-50 transition-colors"
                    >
                      {optimizing ? 'Optimizing Area...' : 'Find Best Locations'}
                    </button>
                  </div>
                </Popup>
              </Marker>
              
              {/* Radius Circle */}
              <Circle 
                center={[optCenter.lat, optCenter.lon]} 
                radius={radiusKm * 1000} 
                pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.1, dashArray: '5, 10' }} 
              />
            </>
          )}

          {/* Optimize Candidates Rendering */}
          {optCandidates.map((cand, idx) => (
            <Marker 
              key={`cand-${idx}`} 
              position={[cand.Latitude, cand.Longitude]} 
              icon={cand.Rank === 1 ? goldIcon : getMarkerIcon(cand.Suitability_Category)}
              zIndexOffset={cand.Rank === 1 ? 1000 : 0}
            >
              <Popup>
                <div className="text-slate-800">
                  <h3 className="font-bold text-lg mb-1 flex items-center gap-1">
                    {cand.Rank === 1 && <Star size={16} className="text-yellow-500 fill-yellow-500" />}
                    Rank #{cand.Rank} Candidate
                  </h3>
                  <p className="m-0 text-sm"><b>Score:</b> {cand.Suitability_Score.toFixed(1)}</p>
                  <p className="m-0 text-sm"><b>Category:</b> {cand.Suitability_Category}</p>
                </div>
              </Popup>
            </Marker>
          ))}

        </MapContainer>
      </div>

      {/* Render Optimization Table */}
      {mode === 'optimize' && optCandidates.length > 0 && (
        <OptimizationTable candidates={optCandidates} />
      )}

    </div>
  );
};
