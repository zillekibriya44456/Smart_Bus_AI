import React from 'react';
import { Star, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

interface Candidate {
  Rank: number;
  Latitude: number;
  Longitude: number;
  Suitability_Score: number;
  Suitability_Category: string;
  Positive_Factors: string[];
  Negative_Factors: string[];
}

export const OptimizationTable: React.FC<{ candidates: Candidate[] }> = ({ candidates }) => {
  if (!candidates || candidates.length === 0) return null;

  return (
    <div className="mt-8 bg-card border border-slate-800 rounded-2xl overflow-hidden">
      <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Star className="text-yellow-400" />
          Top 5 Recommended Locations
        </h2>
        <span className="text-xs text-slate-500 max-w-sm text-right leading-tight">
          AI-generated candidate locations based on available project data and configured constraints. These are derived estimations, not officially approved engineering locations.
        </span>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 text-sm">
              <th className="p-4 font-medium">Rank</th>
              <th className="p-4 font-medium">Coordinates</th>
              <th className="p-4 font-medium">Score</th>
              <th className="p-4 font-medium">Category</th>
              <th className="p-4 font-medium">Key Positive Factor</th>
              <th className="p-4 font-medium">Key Limitation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {candidates.map((cand) => (
              <tr key={cand.Rank} className={cand.Rank === 1 ? "bg-blue-900/10" : "hover:bg-slate-800/50 transition-colors"}>
                <td className="p-4">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold ${cand.Rank === 1 ? 'bg-yellow-400 text-yellow-900' : 'bg-slate-800 text-slate-300'}`}>
                    {cand.Rank}
                  </div>
                </td>
                <td className="p-4 font-mono text-sm text-slate-300">
                  {cand.Latitude.toFixed(5)}, {cand.Longitude.toFixed(5)}
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${cand.Suitability_Score >= 70 ? 'bg-emerald-400' : cand.Suitability_Score >= 40 ? 'bg-yellow-400' : 'bg-red-400'}`} 
                        style={{ width: `${cand.Suitability_Score}%` }}
                      />
                    </div>
                    <span className="font-bold text-white">{cand.Suitability_Score.toFixed(0)}</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border
                    ${cand.Suitability_Category.includes('Highly') || cand.Suitability_Category === 'Suitable' 
                      ? 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20'
                      : cand.Suitability_Category.includes('Moderate') 
                        ? 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20'
                        : 'bg-red-400/10 text-red-400 border-red-400/20'
                    }`}
                  >
                    {cand.Suitability_Category.includes('Highly') || cand.Suitability_Category === 'Suitable' 
                      ? <CheckCircle size={14} /> 
                      : cand.Suitability_Category.includes('Moderate') 
                        ? <AlertTriangle size={14} /> 
                        : <XCircle size={14} />}
                    {cand.Suitability_Category}
                  </span>
                </td>
                <td className="p-4 text-sm text-slate-300">
                  {cand.Positive_Factors[0] || '-'}
                </td>
                <td className="p-4 text-sm text-slate-300">
                  {cand.Negative_Factors[0] || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
