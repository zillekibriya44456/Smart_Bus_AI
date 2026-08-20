import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeLocation } from '../services/api';

export const AnalyzeLocation: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    Passenger_Count: 50,
    Boarding: 25,
    Alighting: 25,
    Road_Width: 10,
    Walking_Distance_m: 200,
    Distance_to_Next_Stop_m: 600,
    Traffic_Level: 'Moderate',
    Bus_Frequency: 15,
    Waiting_Time_min: 10,
    Occupancy_pct: 60
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'Traffic_Level' ? value : Number(value)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const result = await analyzeLocation(formData);
      navigate('/results', { state: { result, input: formData } });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during analysis.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Analyze Location</h1>
        <p className="text-slate-400">Input location parameters to predict suitability using our Machine Learning Surrogate Model.</p>
      </div>

      {error && <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-500 rounded-lg">{error}</div>}

      <form onSubmit={handleSubmit} className="bg-card p-8 rounded-2xl border border-slate-800 space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Passenger Demand (Total)</label>
            <input type="number" name="Passenger_Count" value={formData.Passenger_Count} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none" required min="0" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Traffic Level</label>
            <select name="Traffic_Level" value={formData.Traffic_Level} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none">
              <option value="Low">Low</option>
              <option value="Moderate">Moderate</option>
              <option value="High">High</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Road Width (meters)</label>
            <input type="number" step="0.1" name="Road_Width" value={formData.Road_Width} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none" required min="1" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Distance to Next Stop (m)</label>
            <input type="number" name="Distance_to_Next_Stop_m" value={formData.Distance_to_Next_Stop_m} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none" required min="0" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Walking Distance (m)</label>
            <input type="number" name="Walking_Distance_m" value={formData.Walking_Distance_m} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none" required min="0" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Bus Frequency (mins)</label>
            <input type="number" name="Bus_Frequency" value={formData.Bus_Frequency} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none" required min="1" />
          </div>
          
          <input type="hidden" name="Boarding" value={formData.Boarding} />
          <input type="hidden" name="Alighting" value={formData.Alighting} />
          <input type="hidden" name="Waiting_Time_min" value={formData.Waiting_Time_min} />
          <input type="hidden" name="Occupancy_pct" value={formData.Occupancy_pct} />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="w-full py-3 bg-primary hover:bg-blue-600 text-white font-bold rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </form>
    </div>
  );
};
