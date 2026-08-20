import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { analyzeCorridor, searchLocations } from '../services/api';
import type { CorridorRequest, CorridorAnalysisResponse, CorridorDecision, NominatimResult } from '../services/api';
import { Map as MapIcon, Route, Play, CheckCircle, AlertTriangle, AlertCircle, Trash2, ArrowRight, Loader2, Database, X, FileText } from 'lucide-react';

// Map Event component for clicking to set points
const MapClickHandler: React.FC<{
  onMapClick: (lat: number, lng: number) => void;
}> = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

// Custom Icons
const createIcon = (color: string) =>
  L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="background-color:${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });

const ICONS = {
  START: createIcon('#3b82f6'),
  END: createIcon('#8b5cf6'),
  RETAIN: createIcon('#22c55e'),
  IMPROVE: createIcon('#eab308'),
  RELOCATE_OLD: createIcon('#f97316'), // orange
  RELOCATE_NEW: createIcon('#10b981'), // emerald
  REMOVE: createIcon('#ef4444'),
};

// Custom hook for debounce
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
}

const SemanticAutocomplete: React.FC<{
  label: string;
  placeholder: string;
  onSelect: (lat: number, lng: number) => void;
  onClear: () => void;
}> = ({ label, placeholder, onSelect, onClear }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<NominatimResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  const debouncedQuery = useDebounce(query, 500);

  useEffect(() => {
    if (debouncedQuery.length > 2) {
      setLoading(true);
      searchLocations(debouncedQuery).then(data => {
        setResults(data);
        setShowDropdown(true);
      }).catch(err => {
        console.error("Search error", err);
      }).finally(() => {
        setLoading(false);
      });
    } else {
      setResults([]);
      setShowDropdown(false);
    }
  }, [debouncedQuery]);

  const handleClear = () => {
    setQuery('');
    setResults([]);
    onClear();
  };

  return (
    <div className="relative flex-1 min-w-[250px]">
      <div className="flex justify-between items-center mb-1">
        <label className="block text-sm font-medium text-slate-700">{label}</label>
        {query && (
          <button onClick={handleClear} className="text-xs text-blue-600 hover:text-blue-800">Clear</button>
        )}
      </div>
      <div className="relative">
        <input 
          type="text" 
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => { if (results.length > 0) setShowDropdown(true); }}
          onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
          className="w-full bg-white border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
        />
        {loading && <div className="absolute right-3 top-2.5"><Loader2 className="w-4 h-4 animate-spin text-slate-400" /></div>}
      </div>
      
      {showDropdown && results.length > 0 && (
        <ul className="absolute z-[1000] w-full bg-white border border-slate-200 mt-1 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {results.map(r => (
            <li 
              key={r.place_id} 
              className="p-3 hover:bg-slate-50 cursor-pointer border-b border-slate-100 text-sm"
              onClick={() => {
                setQuery(r.display_name);
                setShowDropdown(false);
                onSelect(parseFloat(r.lat), parseFloat(r.lon));
              }}
            >
              <div className="font-medium text-slate-800 line-clamp-1">{r.display_name.split(',')[0]}</div>
              <div className="text-xs text-slate-500 line-clamp-1">{r.display_name}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export const CorridorAnalysis: React.FC = () => {
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null);
  const [endPoint, setEndPoint] = useState<[number, number] | null>(null);
  const [buffer, setBuffer] = useState<number>(500);
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<CorridorAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [selectedReport, setSelectedReport] = useState<CorridorDecision | null>(null);

  const clearSelection = () => {
    setStartPoint(null);
    setEndPoint(null);
    setResults(null);
    setError(null);
  };

  const handleMapClick = (lat: number, lng: number) => {
    if (!startPoint) {
      setStartPoint([lat, lng]);
    } else if (!endPoint) {
      setEndPoint([lat, lng]);
    } else {
      // Reset if both are set
      setStartPoint([lat, lng]);
      setEndPoint(null);
      setResults(null);
    }
  };

  const handleAnalyze = async () => {
    if (!startPoint || !endPoint) return;
    
    setLoading(true);
    setError(null);
    try {
      const req: CorridorRequest = {
        Start_Latitude: startPoint[0],
        Start_Longitude: startPoint[1],
        End_Latitude: endPoint[0],
        End_Longitude: endPoint[1],
        Buffer_m: buffer,
      };
      const data = await analyzeCorridor(req);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze corridor');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
            <Route className="w-8 h-8 text-blue-600" />
            Corridor Analysis
          </h1>
          <p className="mt-2 text-slate-600 max-w-2xl">
            Select a start and end point on the map to define a study corridor. 
            The system will analyze all existing bus stops within the buffer zone and automatically 
            recommend whether to Retain, Improve, Relocate, or Remove them.
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col gap-6">
        
        {/* Semantic Search Row */}
        <div className="flex flex-wrap gap-4 items-end bg-slate-50 p-4 rounded-xl border border-slate-200">
          <SemanticAutocomplete 
            label="Start Location / Address" 
            placeholder="Search Bangalore locations (e.g. Peenya)" 
            onSelect={(lat, lon) => setStartPoint([lat, lon])} 
            onClear={() => setStartPoint(null)}
          />
          <SemanticAutocomplete 
            label="Destination Location / Address" 
            placeholder="Search Bangalore locations (e.g. Majestic)" 
            onSelect={(lat, lon) => setEndPoint([lat, lon])} 
            onClear={() => setEndPoint(null)}
          />
        </div>

        {/* Action Row */}
        <div className="flex flex-wrap gap-6 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
            <div className="text-sm text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              {!startPoint ? 'Click map or search to set Start Point' : !endPoint ? 'Click map or search to set End Point' : 'Corridor ready for analysis'}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Buffer Radius (m)</label>
            <select 
              value={buffer}
              onChange={(e) => setBuffer(Number(e.target.value))}
              className="w-32 bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
              disabled={loading}
            >
              <option value={200}>200 m</option>
              <option value={500}>500 m</option>
              <option value={1000}>1000 m</option>
            </select>
          </div>

          <div className="flex gap-3">
            <button
              onClick={clearSelection}
              disabled={!startPoint || loading}
              className="px-4 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 transition-colors"
            >
              Clear
            </button>
            <button
              onClick={handleAnalyze}
              disabled={!startPoint || !endPoint || loading}
              className="flex items-center gap-2 px-6 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 transition-colors shadow-sm"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Analyze Corridor
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Map & Results Summary Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden relative min-h-[600px]">
          <MapContainer center={[12.9716, 77.5946]} zoom={11} style={{ height: '600px', width: '100%' }} className="z-0">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapClickHandler onMapClick={handleMapClick} />
            
            {/* Start and End Points */}
            {startPoint && (
              <Marker position={startPoint} icon={ICONS.START}>
                <Popup>Start Point</Popup>
              </Marker>
            )}
            {endPoint && (
              <Marker position={endPoint} icon={ICONS.END}>
                <Popup>End Point</Popup>
              </Marker>
            )}
            
            {/* Corridor Line */}
            {startPoint && endPoint && (
              <Polyline positions={[startPoint, endPoint]} color="#3b82f6" weight={3} dashArray="5, 10" />
            )}

            {/* Render Result Markers */}
            {results?.Decisions.map((d, idx) => (
              <React.Fragment key={d.Stop_ID}>
                <Marker 
                  position={[d.Current_Latitude, d.Current_Longitude]} 
                  icon={
                    d.Decision === 'RETAIN' ? ICONS.RETAIN :
                    d.Decision === 'IMPROVE' ? ICONS.IMPROVE :
                    d.Decision === 'RELOCATE' ? ICONS.RELOCATE_OLD : ICONS.REMOVE
                  }
                >
                  <Popup>
                    <div className="font-semibold">{d.Stop_ID}</div>
                    <div className="text-sm">Current Score: {d.Current_Score.toFixed(0)}</div>
                    <div className="text-sm font-medium mt-1 mb-2">Decision: {d.Decision}</div>
                    <button 
                      onClick={() => setSelectedReport(d)}
                      className="text-xs bg-blue-50 text-blue-600 px-3 py-1.5 rounded font-medium hover:bg-blue-100 w-full"
                    >
                      View Full Report
                    </button>
                  </Popup>
                </Marker>
                
                {/* Relocated New Position */}
                {d.Decision === 'RELOCATE' && d.Recommended_Location && (
                  <>
                    <Marker position={[d.Recommended_Location.Latitude, d.Recommended_Location.Longitude]} icon={ICONS.RELOCATE_NEW}>
                      <Popup>
                        <div className="font-semibold">New Location for {d.Stop_ID}</div>
                        <div className="text-sm">New Score: {d.Recommended_Location.New_Score.toFixed(0)}</div>
                        <div className="text-sm text-green-600">+{d.Recommended_Location.Improvement.toFixed(0)} points</div>
                      </Popup>
                    </Marker>
                    <Polyline 
                      positions={[
                        [d.Current_Latitude, d.Current_Longitude],
                        [d.Recommended_Location.Latitude, d.Recommended_Location.Longitude]
                      ]} 
                      color="#f97316" 
                      weight={2} 
                      dashArray="4, 4" 
                      opacity={0.7}
                    />
                  </>
                )}
              </React.Fragment>
            ))}
          </MapContainer>

          {/* Map Legend */}
          <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur p-3 rounded-xl shadow-lg border border-slate-100 text-xs font-medium space-y-2 z-[400]">
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500 border border-white"></div> Start Point</div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-purple-500 border border-white"></div> End Point</div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-green-500 border border-white"></div> Retain</div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-yellow-500 border border-white"></div> Improve</div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-orange-500 border border-white"></div> Relocate (Old)</div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-emerald-500 border border-white"></div> Relocate (New)</div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500 border border-white"></div> Remove</div>
          </div>
        </div>

        {/* Summary Dashboard */}
        {results ? (
          <div className="bg-slate-900 rounded-2xl p-6 text-white overflow-y-auto shadow-sm flex flex-col gap-6">
            <h2 className="text-xl font-semibold border-b border-slate-800 pb-4">Corridor Summary</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-800 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-white">{results.Total_Stops_Analyzed}</div>
                <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider">Total Stops</div>
              </div>
              <div className="bg-slate-800 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-green-400">{results.Count_Retain}</div>
                <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider">Retain</div>
              </div>
              <div className="bg-slate-800 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-yellow-400">{results.Count_Improve}</div>
                <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider">Improve</div>
              </div>
              <div className="bg-slate-800 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-orange-400">{results.Count_Relocate}</div>
                <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider">Relocate</div>
              </div>
              <div className="bg-slate-800 p-4 rounded-xl text-center col-span-2">
                <div className="text-3xl font-bold text-red-400">{results.Count_Remove}</div>
                <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider">Remove</div>
              </div>
            </div>

            <div className="mt-4 pt-6 border-t border-slate-800">
              <h3 className="text-sm font-medium text-slate-300 mb-4 uppercase tracking-wider">Before vs After</h3>
              <div className="flex items-center justify-between bg-slate-800 rounded-xl p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-slate-200">{results.Average_Score_Before.toFixed(1)}</div>
                  <div className="text-xs text-slate-400">Avg Before</div>
                </div>
                <ArrowRight className="text-slate-500 w-5 h-5" />
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">{results.Average_Score_After.toFixed(1)}</div>
                  <div className="text-xs text-slate-400">Avg After</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 flex items-center justify-center text-slate-500 text-sm p-6 text-center">
            Run an analysis to view the corridor summary and impact metrics here.
          </div>
        )}
      </div>

      {/* Results Table */}
      {results && results.Total_Stops_Analyzed > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="p-6 border-b border-slate-100">
            <h2 className="text-xl font-semibold text-slate-900">Detailed Stop Decisions</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-slate-600">
              <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4 font-medium">Bus Stop ID</th>
                  <th className="px-6 py-4 font-medium">Current Score</th>
                  <th className="px-6 py-4 font-medium">Decision</th>
                  <th className="px-6 py-4 font-medium">New Score</th>
                  <th className="px-6 py-4 font-medium">Improvement</th>
                  <th className="px-6 py-4 font-medium">Action Needed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {results.Decisions.map((d) => (
                  <tr key={d.Stop_ID} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-900">{d.Stop_ID}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold ${
                        d.Current_Score >= 75 ? 'bg-green-100 text-green-700' :
                        d.Current_Score >= 50 ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {d.Current_Score.toFixed(0)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                        d.Decision === 'RETAIN' ? 'bg-green-100 text-green-700' :
                        d.Decision === 'IMPROVE' ? 'bg-yellow-100 text-yellow-700' :
                        d.Decision === 'RELOCATE' ? 'bg-orange-100 text-orange-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {d.Decision === 'RETAIN' && <CheckCircle className="w-3.5 h-3.5" />}
                        {d.Decision === 'IMPROVE' && <AlertTriangle className="w-3.5 h-3.5" />}
                        {d.Decision === 'RELOCATE' && <MapIcon className="w-3.5 h-3.5" />}
                        {d.Decision === 'REMOVE' && <Trash2 className="w-3.5 h-3.5" />}
                        {d.Decision}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {d.Recommended_Location ? (
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700">
                          {d.Recommended_Location.New_Score.toFixed(0)}
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {d.Recommended_Location ? (
                        <span className="text-emerald-600 font-medium">+{d.Recommended_Location.Improvement.toFixed(0)}</span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {d.Explanation}
                      <button 
                        onClick={() => setSelectedReport(d)}
                        className="mt-2 flex items-center gap-1.5 text-blue-600 font-medium hover:text-blue-800"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        View Report
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Detailed Modal Report */}
      {selectedReport && (
        <div className="fixed inset-0 z-[999] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div>
                <h2 className="text-xl font-bold text-slate-900">Bus Stop Analysis Report</h2>
                <p className="text-sm text-slate-500 mt-1">{selectedReport.Stop_ID}</p>
              </div>
              <button onClick={() => setSelectedReport(null)} className="p-2 hover:bg-slate-200 rounded-full text-slate-500 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto space-y-6">
              
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Current Coordinates</div>
                  <div className="font-mono text-sm text-slate-700">{selectedReport.Current_Latitude.toFixed(6)}, {selectedReport.Current_Longitude.toFixed(6)}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Final Score</div>
                  <div className="text-lg font-bold text-slate-900">{selectedReport.Current_Score.toFixed(0)} / 100</div>
                </div>
              </div>

              {/* Decision */}
              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <div className={`p-4 border-b border-slate-200 flex items-center gap-3 ${
                  selectedReport.Decision === 'RETAIN' ? 'bg-green-50 text-green-800' :
                  selectedReport.Decision === 'IMPROVE' ? 'bg-yellow-50 text-yellow-800' :
                  selectedReport.Decision === 'RELOCATE' ? 'bg-orange-50 text-orange-800' : 'bg-red-50 text-red-800'
                }`}>
                  <div className="font-bold text-lg">DECISION: {selectedReport.Decision}</div>
                </div>
                <div className="p-4 text-sm text-slate-700">
                  <div className="font-semibold mb-2">Analysis Reasoning:</div>
                  <p>{selectedReport.Explanation}</p>
                  
                  {selectedReport.Positive_Factors.length > 0 && (
                    <div className="mt-4">
                      <strong className="text-green-700">Positive Factors:</strong>
                      <ul className="list-disc pl-5 mt-1 space-y-1">
                        {selectedReport.Positive_Factors.map((f, i) => <li key={i}>{f}</li>)}
                      </ul>
                    </div>
                  )}
                  {selectedReport.Negative_Factors.length > 0 && (
                    <div className="mt-4">
                      <strong className="text-red-700">Negative Constraints:</strong>
                      <ul className="list-disc pl-5 mt-1 space-y-1">
                        {selectedReport.Negative_Factors.map((f, i) => <li key={i}>{f}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              {/* Recommendation */}
              {selectedReport.Decision === 'RELOCATE' && selectedReport.Recommended_Location && (
                <div>
                  <h3 className="font-bold text-slate-900 mb-3 border-b border-slate-200 pb-2">Optimization Result</h3>
                  
                  <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 mb-4">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="text-emerald-800 font-bold text-lg mb-1">Rank #1 - Best Recommended Location</div>
                        <div className="font-mono text-sm text-emerald-700">{selectedReport.Recommended_Location.Latitude.toFixed(6)}, {selectedReport.Recommended_Location.Longitude.toFixed(6)}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-emerald-600">{selectedReport.Recommended_Location.New_Score.toFixed(0)} <span className="text-sm font-normal text-emerald-700">/ 100</span></div>
                        <div className="text-sm font-semibold text-emerald-600">+{selectedReport.Recommended_Location.Improvement.toFixed(0)} Points</div>
                      </div>
                    </div>
                    
                    <div className="text-sm text-emerald-800 bg-white/60 p-3 rounded-lg border border-emerald-100">
                      <strong className="block mb-1">Distance to move:</strong> 
                      {selectedReport.Recommended_Location.Distance_Moved_m.toFixed(0)} meters
                      
                      <strong className="block mt-3 mb-1">Why this location is better:</strong>
                      {selectedReport.Recommended_Location.Reason}
                    </div>
                  </div>

                  {selectedReport.Alternatives && selectedReport.Alternatives.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-slate-700 mb-2 text-sm uppercase tracking-wider">Alternative Candidates</h4>
                      <div className="space-y-2">
                        {selectedReport.Alternatives.map((alt, idx) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100 text-sm">
                            <div>
                              <span className="font-bold text-slate-500 mr-2">#{idx + 2}</span>
                              <span className="font-mono text-slate-600">{alt.Latitude.toFixed(4)}, {alt.Longitude.toFixed(4)}</span>
                              <span className="ml-3 text-slate-500">({alt.Distance_Moved_m.toFixed(0)}m away)</span>
                            </div>
                            <div className="font-bold text-emerald-600">{alt.New_Score.toFixed(0)} score</div>
                          </div>
                        ))}
                      </div>
                      <p className="text-xs text-slate-400 mt-3 italic">* Candidate locations are generated using approximate corridor geometry.</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
