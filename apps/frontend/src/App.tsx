import { useState } from 'react';
import { EditorialHeader, ViewType } from './components/common/EditorialHeader';
import { HomePage } from './pages/HomePage';
import { AnalyzePage } from './pages/AnalyzePage';
import { StandardsPage } from './pages/StandardsPage';
import { DashboardPage } from './pages/DashboardPage';
import { DecisionPackagePage } from './pages/DecisionPackagePage';
import { HowItWorksPage } from './pages/HowItWorksPage';
import { BenchmarksPage } from './pages/BenchmarksPage';
import { ComparativeEvaluationPage } from './pages/ComparativeEvaluationPage';
import { AuthProvider } from './context/AuthContext';
import { RoleSwitcherModal } from './components/common/RoleSwitcherModal';
import { ProcurementSpecification } from './types/requirement';

export function App() {
  const [currentView, setCurrentView] = useState<ViewType>('home');
  const [selectedSpec, setSelectedSpec] = useState<ProcurementSpecification | undefined>(undefined);
  const [standardsInitialQuery, setStandardsInitialQuery] = useState<string | undefined>(undefined);

  const handleSelectSpecification = (spec: ProcurementSpecification) => {
    setSelectedSpec(spec);
    setCurrentView('analyze');
  };

  const handleNavigate = (view: ViewType, query?: string) => {
    if (view === 'standards' && query) {
      setStandardsInitialQuery(query);
    }
    setCurrentView(view);
  };

  return (
    <AuthProvider>
      <div className="min-h-screen bg-parchment-base text-ink-text flex flex-col font-sans selection:bg-mineral-light selection:text-mineral-dark">
        <RoleSwitcherModal />

        {/* Top Header shown on non-home pages */}
        {currentView !== 'home' && (
          <EditorialHeader
            currentView={currentView}
            onSelectView={(view) => setCurrentView(view)}
          />
        )}

        {/* Main Content Area */}
        <main className="flex-1">
          {currentView === 'home' && (
            <HomePage onNavigate={handleNavigate} />
          )}
          {currentView === 'how-it-works' && (
            <HowItWorksPage onNavigate={handleNavigate} />
          )}
          {currentView === 'analyze' && (
            <AnalyzePage
              selectedSpecification={selectedSpec}
              onNavigateToDecisionPackage={(spec) => {
                if (spec) setSelectedSpec(spec);
                setCurrentView('decision-package');
              }}
            />
          )}
          {currentView === 'standards' && (
            <StandardsPage
              initialQuery={standardsInitialQuery}
              onNavigate={handleNavigate}
            />
          )}
          {currentView === 'dashboard' && (
            <DashboardPage onSelectSpecification={handleSelectSpecification} />
          )}
          {currentView === 'decision-package' && (
            <DecisionPackagePage selectedSpecification={selectedSpec} />
          )}
          {currentView === 'benchmarks' && (
            <BenchmarksPage />
          )}
          {currentView === 'comparative' && (
            <ComparativeEvaluationPage />
          )}
        </main>

      {/* Editorial Footer */}
      {currentView !== 'home' && (
        <footer className="bg-parchment-surface border-t border-parchment-border py-4 px-4 lg:px-8 text-xs text-ink-muted">
          <div className="max-w-[1500px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-2 font-mono text-[11px]">
              <span>NORMVAULT v2.4.0</span>
              <span className="text-slate-300">•</span>
              <span>Bureau of Indian Standards (BIS) Architecture</span>
            </div>
            <div className="text-[11px] font-mono text-ink-faint">
              Phases 0–8 Authoritative Deterministic Engine
            </div>
          </div>
        </footer>
      )}
      </div>
    </AuthProvider>
  );
}

export default App;
