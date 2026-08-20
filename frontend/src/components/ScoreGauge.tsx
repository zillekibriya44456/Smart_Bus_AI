import React from 'react';

export const ScoreGauge: React.FC<{ score: number, category: string }> = ({ score, category }) => {
  let color = 'text-green-500';
  let ring = 'ring-green-500/20';
  
  if (score < 35) { color = 'text-red-500'; ring = 'ring-red-500/20'; }
  else if (score < 50) { color = 'text-orange-500'; ring = 'ring-orange-500/20'; }
  else if (score < 65) { color = 'text-yellow-500'; ring = 'ring-yellow-500/20'; }
  else if (score < 80) { color = 'text-emerald-400'; ring = 'ring-emerald-400/20'; }

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-slate-900 rounded-2xl border border-slate-800">
      <div className={`relative flex items-center justify-center w-48 h-48 rounded-full ring-8 ${ring} bg-slate-800/50 mb-6`}>
        <div className="text-center">
          <span className={`text-6xl font-black ${color}`}>{Math.round(score)}</span>
          <span className="text-slate-400 text-xl font-bold">/100</span>
        </div>
      </div>
      <h3 className={`text-2xl font-bold tracking-wide uppercase ${color}`}>{category}</h3>
    </div>
  );
};
