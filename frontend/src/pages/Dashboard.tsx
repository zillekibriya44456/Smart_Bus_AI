import React from 'react';
import { Activity, Bus, MapPin, Users } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white mb-4">Dashboard</h1>
        <p className="text-slate-400 text-lg">Welcome to the AI-Powered Smart Bus Stop Suitability & Optimization System.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Total Audited Stops', value: '15,000+', icon: <Bus className="text-primary" size={24} /> },
          { label: 'Avg Suitability', value: '68/100', icon: <Activity className="text-secondary" size={24} /> },
          { label: 'High Demand Areas', value: '342', icon: <Users className="text-warning" size={24} /> },
          { label: 'Critical Upgrades', value: '89', icon: <MapPin className="text-danger" size={24} /> },
        ].map((stat, i) => (
          <div key={i} className="bg-card p-6 rounded-2xl border border-slate-800 flex items-start justify-between">
            <div>
              <p className="text-slate-400 text-sm font-medium mb-1">{stat.label}</p>
              <h3 className="text-3xl font-bold text-white">{stat.value}</h3>
            </div>
            <div className="p-3 bg-slate-800/50 rounded-xl">
              {stat.icon}
            </div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-card p-8 rounded-2xl border border-slate-800">
          <h2 className="text-2xl font-bold text-white mb-4">Analyze New Location</h2>
          <p className="text-slate-400 mb-8">Enter geographic, demographic, and traffic parameters to predict the suitability of a new bus stop using our Machine Learning surrogate model.</p>
          <Link to="/analyze" className="inline-flex items-center justify-center px-6 py-3 bg-primary hover:bg-blue-600 text-white font-medium rounded-lg transition-colors">
            Start Analysis
          </Link>
        </div>
        <div className="bg-card p-8 rounded-2xl border border-slate-800">
          <h2 className="text-2xl font-bold text-white mb-4">Audit Existing Stops</h2>
          <p className="text-slate-400 mb-8">Review our database of surveyed bus stops, view their AI-generated suitability scores, and discover recommended infrastructure upgrades.</p>
          <Link to="/audit" className="inline-flex items-center justify-center px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-lg transition-colors border border-slate-700">
            View Audits
          </Link>
        </div>
      </div>
    </div>
  );
};
