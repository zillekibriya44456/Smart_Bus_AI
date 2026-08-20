
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { AnalyzeLocation } from './pages/AnalyzeLocation';
import { Results } from './pages/Results';
import { ExistingAudit } from './pages/ExistingAudit';
import { InteractiveMap } from './pages/InteractiveMap';
import { CompareLocations } from './pages/CompareLocations';
import { CorridorAnalysis } from './pages/CorridorAnalysis';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analyze" element={<AnalyzeLocation />} />
          <Route path="/compare" element={<CompareLocations />} />
          <Route path="/results" element={<Results />} />
          <Route path="/audit" element={<ExistingAudit />} />
          <Route path="/map" element={<InteractiveMap />} />
          <Route path="/corridor-analysis" element={<CorridorAnalysis />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
