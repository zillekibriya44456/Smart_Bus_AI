import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Bus, Map, List, Activity } from 'lucide-react';

export const Layout: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: <Activity size={20} /> },
    { path: '/map', label: 'Interactive Map', icon: <Map size={20} /> },
    { path: '/analyze', label: 'Manual Input', icon: <List size={20} /> },
    { path: '/compare', label: 'Compare Locations', icon: <Activity size={20} /> },
    { path: '/audit', label: 'Existing Audit', icon: <List size={20} /> },
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-slate-800">
        <div className="p-6 flex items-center gap-3">
          <div className="p-2 bg-primary/20 rounded-lg text-primary">
            <Bus size={24} />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            SmartBus AI
          </h1>
        </div>
        
        <nav className="mt-6 px-4 flex flex-col gap-2">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname === item.path 
                  ? 'bg-primary text-white' 
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
              }`}
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto p-8">
        <div className="max-w-6xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};
