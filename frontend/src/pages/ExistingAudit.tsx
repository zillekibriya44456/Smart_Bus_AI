import React, { useEffect, useState } from 'react';
import { getBusStops } from '../services/api';
import { Loader2, AlertCircle, AlertTriangle, Info, CheckCircle, ArrowUpDown, Filter } from 'lucide-react';

export const ExistingAudit: React.FC = () => {
  const [stops, setStops] = useState<any[]>([]);
  const [filteredStops, setFilteredStops] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [filterPriority, setFilterPriority] = useState('All');
  const [sortBy, setSortBy] = useState('Priority');

  useEffect(() => {
    getBusStops()
      .then(data => {
        setStops(data);
        setFilteredStops(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to fetch existing bus stops. Make sure the backend is running.');
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    let result = [...stops];

    // Filter
    if (filterPriority !== 'All') {
      result = result.filter(s => s.Priority_Category === filterPriority);
    }

    // Sort
    if (sortBy === 'Priority') {
      result.sort((a, b) => b.Priority_Score - a.Priority_Score);
    } else if (sortBy === 'Suitability') {
      result.sort((a, b) => b.Suitability_Score - a.Suitability_Score);
    }

    setFilteredStops(result);
  }, [filterPriority, sortBy, stops]);

  const getPriorityBadge = (cat: string) => {
    switch (cat) {
      case 'Critical': return <span className="inline-flex items-center gap-1 bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-1 rounded text-xs font-bold"><AlertCircle size={12} /> CRITICAL</span>;
      case 'High': return <span className="inline-flex items-center gap-1 bg-orange-500/20 text-orange-400 border border-orange-500/30 px-2 py-1 rounded text-xs font-bold"><AlertTriangle size={12} /> HIGH</span>;
      case 'Medium': return <span className="inline-flex items-center gap-1 bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 px-2 py-1 rounded text-xs font-bold"><Info size={12} /> MEDIUM</span>;
      case 'Low': return <span className="inline-flex items-center gap-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-1 rounded text-xs font-bold"><CheckCircle size={12} /> LOW</span>;
      default: return null;
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <Loader2 className="animate-spin text-primary mb-4" size={48} />
        <p className="text-slate-400">Auditing all existing bus stops...</p>
      </div>
    );
  }

  if (error) {
    return <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-500 rounded-lg">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Existing Infrastructure Audit</h1>
          <p className="text-slate-400 max-w-2xl">
            This module evaluates all 15,000 surveyed bus stops and calculates an <b>Improvement Priority Score</b> based on demand pressure versus critical infrastructure deficiencies.
          </p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 flex gap-6 items-center">
        <div className="flex items-center gap-3">
          <Filter size={18} className="text-slate-400" />
          <label className="text-sm font-bold text-slate-300">Filter Priority:</label>
          <select 
            value={filterPriority} 
            onChange={e => setFilterPriority(e.target.value)}
            className="bg-slate-800 border border-slate-600 text-white rounded px-3 py-1.5 text-sm outline-none"
          >
            <option value="All">All Categories</option>
            <option value="Critical">Critical Only</option>
            <option value="High">High Only</option>
            <option value="Medium">Medium Only</option>
            <option value="Low">Low Only</option>
          </select>
        </div>

        <div className="flex items-center gap-3">
          <ArrowUpDown size={18} className="text-slate-400" />
          <label className="text-sm font-bold text-slate-300">Sort By:</label>
          <select 
            value={sortBy} 
            onChange={e => setSortBy(e.target.value)}
            className="bg-slate-800 border border-slate-600 text-white rounded px-3 py-1.5 text-sm outline-none"
          >
            <option value="Priority">Highest Priority First</option>
            <option value="Suitability">Highest Suitability First</option>
          </select>
        </div>
        
        <div className="ml-auto text-sm text-slate-400">
          Showing <b>{filteredStops.length}</b> stops
        </div>
      </div>

      <div className="bg-card border border-slate-800 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                <th className="p-4 font-medium w-16 text-center">Rank</th>
                <th className="p-4 font-medium">Stop ID / Location</th>
                <th className="p-4 font-medium w-32">Priority</th>
                <th className="p-4 font-medium w-32">Suitability</th>
                <th className="p-4 font-medium">Main Deficiencies</th>
                <th className="p-4 font-medium">Key Recommendation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filteredStops.map((stop, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 text-center text-slate-500 font-mono text-sm">{idx + 1}</td>
                  <td className="p-4">
                    <div className="font-bold text-slate-200">{stop.Stop_ID}</div>
                    <div className="text-xs font-mono text-slate-500 mt-1">
                      {stop.Latitude.toFixed(5)}, {stop.Longitude.toFixed(5)}
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="mb-1">{getPriorityBadge(stop.Priority_Category)}</div>
                    <div className="text-xs text-slate-400">Score: {stop.Priority_Score}/100</div>
                  </td>
                  <td className="p-4">
                    <div className="text-white font-bold">{stop.Suitability_Score.toFixed(0)}/100</div>
                    <div className="text-xs text-slate-400 truncate w-32">{stop.Suitability_Category}</div>
                  </td>
                  <td className="p-4">
                    <ul className="text-sm text-red-400/80 space-y-1 list-disc list-inside">
                      {stop.Negative_Factors?.slice(0, 2).map((nf: string, i: number) => (
                        <li key={i} className="truncate max-w-xs" title={nf}>{nf}</li>
                      ))}
                      {!stop.Negative_Factors?.length && <span className="text-slate-500">None</span>}
                    </ul>
                  </td>
                  <td className="p-4">
                    <div className="text-sm text-emerald-400/90 truncate max-w-xs" title={stop.Recommendations?.[0]}>
                      {stop.Recommendations?.[0] || 'No action needed'}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredStops.length === 0 && (
            <div className="p-8 text-center text-slate-500">No bus stops match your filters.</div>
          )}
        </div>
      </div>
    </div>
  );
};
