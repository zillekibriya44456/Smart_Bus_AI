import React from 'react';
import { useLocation, Link, Navigate } from 'react-router-dom';
import { ScoreGauge } from '../components/ScoreGauge';
import { CheckCircle, AlertTriangle, ArrowLeft, Wrench } from 'lucide-react';

export const Results: React.FC = () => {
  const { state } = useLocation();
  
  if (!state || !state.result) {
    return <Navigate to="/analyze" />;
  }

  const { result } = state;

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Link to="/analyze" className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-3xl font-bold text-white">Analysis Results</h1>
      </div>

      {result.Analysis_Type === 'Derived' && (
        <div className="p-4 bg-orange-500/10 border border-orange-500/20 rounded-xl flex items-start gap-3">
          <AlertTriangle className="text-orange-400 shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="text-orange-400 font-bold mb-1">Derived Spatial Analysis</h3>
            <p className="text-slate-300 text-sm">
              Because you only provided coordinates, geographic proximity was used to infer the traffic, road width, and demand data from the nearest known surveyed bus stops.
            </p>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <ScoreGauge score={result.Suitability_Score} category={result.Suitability_Category} />
        </div>
        
        <div className="md:col-span-2 space-y-6">
          <div className="bg-card p-6 rounded-2xl border border-slate-800">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <CheckCircle className="text-emerald-400" /> Positive Factors
            </h2>
            {result.Positive_Factors.length > 0 ? (
              <ul className="space-y-2">
                {result.Positive_Factors.map((f: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-slate-300">
                    <span className="text-emerald-400 mt-1">•</span> {f}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-slate-500">None identified.</p>
            )}
          </div>

          <div className="bg-card p-6 rounded-2xl border border-slate-800">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <AlertTriangle className="text-red-400" /> Negative Factors
            </h2>
            {result.Negative_Factors.length > 0 ? (
              <ul className="space-y-2">
                {result.Negative_Factors.map((f: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-slate-300">
                    <span className="text-red-400 mt-1">•</span> {f}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-slate-500">None identified.</p>
            )}
          </div>
        </div>
      </div>

      <div className="bg-card p-6 rounded-2xl border border-slate-800">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Wrench className="text-primary" /> Infrastructure Recommendations
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          {result.Recommendations.map((r: string, i: number) => (
            <div key={i} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 text-slate-300">
              {r}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
