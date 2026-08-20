import React, { useState } from 'react';
import { compareLocations } from '../services/api';
import { Loader2, ArrowRightLeft, CheckCircle, AlertTriangle, XCircle, Award } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export const CompareLocations: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<any>(null);

  // Default mock forms for Location A and B
  const [locA, setLocA] = useState({
    Passenger_Count: 80,
    Boarding: 40,
    Alighting: 40,
    Road_Width: 12,
    Walking_Distance_m: 200,
    Distance_to_Next_Stop_m: 600,
    Traffic_Level: 'Low',
    Bus_Frequency: 10,
    Waiting_Time_min: 5,
    Occupancy_pct: 50
  });

  const [locB, setLocB] = useState({
    Passenger_Count: 30,
    Boarding: 15,
    Alighting: 15,
    Road_Width: 6,
    Walking_Distance_m: 600,
    Distance_to_Next_Stop_m: 300,
    Traffic_Level: 'High',
    Bus_Frequency: 20,
    Waiting_Time_min: 15,
    Occupancy_pct: 80
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>, loc: 'A' | 'B') => {
    const { name, value } = e.target;
    const setter = loc === 'A' ? setLocA : setLocB;
    setter(prev => ({
      ...prev,
      [name]: name === 'Traffic_Level' ? value : Number(value)
    }));
  };

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const data = await compareLocations(locA, locB);
      setResults(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Comparison failed.');
    } finally {
      setLoading(false);
    }
  };

  const LocationForm = ({ title, locKey, state }: { title: string, locKey: 'A' | 'B', state: any }) => (
    <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 space-y-4">
      <h2 className="text-xl font-bold text-white mb-4">{title}</h2>
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Passenger Demand</label>
          <input type="number" name="Passenger_Count" value={state.Passenger_Count} onChange={(e) => handleChange(e, locKey)} className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm" />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Road Width (m)</label>
          <input type="number" step="0.1" name="Road_Width" value={state.Road_Width} onChange={(e) => handleChange(e, locKey)} className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm" />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Walking Distance (m)</label>
          <input type="number" name="Walking_Distance_m" value={state.Walking_Distance_m} onChange={(e) => handleChange(e, locKey)} className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm" />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Traffic Level</label>
          <select name="Traffic_Level" value={state.Traffic_Level} onChange={(e) => handleChange(e, locKey)} className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm">
            <option value="Low">Low</option>
            <option value="Moderate">Moderate</option>
            <option value="High">High</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Dist. to Next Stop (m)</label>
          <input type="number" name="Distance_to_Next_Stop_m" value={state.Distance_to_Next_Stop_m} onChange={(e) => handleChange(e, locKey)} className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm" />
        </div>
      </div>
    </div>
  );

  const formatChartData = () => {
    if (!results) return [];
    const keys = ["Demand", "Road", "Accessibility", "Safety", "Spacing"];
    return keys.map(k => ({
      subject: k,
      A: results.Location_A_Response.SubScores[k],
      B: results.Location_B_Response.SubScores[k],
      fullMark: 100,
    }));
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-2">
          <ArrowRightLeft className="text-primary" /> Location Comparison
        </h1>
        <p className="text-slate-400">Input parameters for two theoretical locations to compare their suitability using the AI Engine side-by-side.</p>
      </div>

      {error && <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-500 rounded-lg">{error}</div>}

      <form onSubmit={handleCompare} className="bg-card p-6 rounded-2xl border border-slate-800">
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <LocationForm title="Location A" locKey="A" state={locA} />
          <LocationForm title="Location B" locKey="B" state={locB} />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="w-full py-4 bg-primary hover:bg-blue-600 text-white font-bold rounded-xl transition-colors disabled:opacity-50 flex justify-center items-center gap-2"
        >
          {loading ? <><Loader2 className="animate-spin" /> Running Comparison...</> : 'Compare Locations'}
        </button>
      </form>

      {results && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* Recommendation Banner */}
          <div className={`p-6 rounded-2xl border flex items-start gap-4 ${
            results.Recommended_Location === 'Location A' 
              ? 'bg-blue-900/20 border-blue-500/30' 
              : results.Recommended_Location === 'Location B'
                ? 'bg-purple-900/20 border-purple-500/30'
                : 'bg-slate-800 border-slate-600'
          }`}>
            <Award className={
              results.Recommended_Location === 'Location A' ? 'text-blue-400' 
              : results.Recommended_Location === 'Location B' ? 'text-purple-400' 
              : 'text-slate-400'
            } size={40} />
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Winner: {results.Recommended_Location}
              </h2>
              <p className="text-slate-300 leading-relaxed">
                {results.Recommendation_Reason}
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Visual Radar Chart */}
            <div className="bg-card p-6 rounded-2xl border border-slate-800 flex flex-col items-center justify-center min-h-[400px]">
              <h3 className="text-lg font-bold text-white mb-4 w-full">Sub-Score Analysis</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={formatChartData()}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar name="Location A" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} />
                  <Radar name="Location B" dataKey="B" stroke="#a855f7" fill="#a855f7" fillOpacity={0.4} />
                  <Legend wrapperStyle={{ paddingTop: '20px' }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Score Comparison Table */}
            <div className="bg-card p-6 rounded-2xl border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4">Detailed Metrics</h3>
              <div className="space-y-4">
                
                <div className="grid grid-cols-3 gap-2 pb-2 border-b border-slate-800 text-sm font-medium text-slate-400">
                  <div>Metric</div>
                  <div className="text-blue-400 text-right">Location A</div>
                  <div className="text-purple-400 text-right">Location B</div>
                </div>

                {["Demand", "Road", "Accessibility", "Safety", "Spacing"].map(k => (
                  <div key={k} className="grid grid-cols-3 gap-2 py-2 border-b border-slate-800/50 text-slate-300">
                    <div>{k} Score</div>
                    <div className="text-right font-mono">{results.Location_A_Response.SubScores[k]}</div>
                    <div className="text-right font-mono">{results.Location_B_Response.SubScores[k]}</div>
                  </div>
                ))}

                <div className="grid grid-cols-3 gap-2 pt-2 text-white font-bold text-lg">
                  <div>Final Score</div>
                  <div className="text-right">{results.Location_A_Response.Suitability_Score.toFixed(0)}</div>
                  <div className="text-right">{results.Location_B_Response.Suitability_Score.toFixed(0)}</div>
                </div>
                
                <div className="grid grid-cols-3 gap-2 pt-2 text-sm">
                  <div>Category</div>
                  <div className="text-right text-blue-300">{results.Location_A_Response.Suitability_Category}</div>
                  <div className="text-right text-purple-300">{results.Location_B_Response.Suitability_Category}</div>
                </div>

              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
