import React, { useState } from 'react';
import { ArrowRight, Search, X } from 'lucide-react';

export type ViewType = 'home' | 'analyze' | 'standards' | 'dashboard' | 'decision-package' | 'how-it-works';

interface EditorialHeaderProps {
  currentView: ViewType;
  onSelectView: (view: ViewType) => void;
  runId?: string;
}

export const EditorialHeader: React.FC<EditorialHeaderProps> = ({
  currentView,
  onSelectView,
  runId = 'RUN-2025-0418-NV',
}) => {
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSelectView('standards');
    }
  };

  return (
    <header className="bg-parchment-base border-b border-parchment-border sticky top-0 z-40">
      <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        {/* Left: Brand */}
        <div className="flex items-center gap-6">
          <div
            onClick={() => onSelectView('home')}
            className="cursor-pointer flex items-center gap-2 select-none group"
          >
            <span className="text-2xl font-serif font-black tracking-tight text-ink-text">
              NORM<span className="text-mineral-blue font-sans font-extrabold">VAULT</span>
            </span>
          </div>

          {/* Center Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6 text-xs font-medium uppercase tracking-wider text-ink-muted">
            <button
              onClick={() => onSelectView('home')}
              className={`py-1 transition-all ${
                currentView === 'home'
                  ? 'text-ink-text font-bold border-b border-ink-text'
                  : 'hover:text-ink-text'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => onSelectView('how-it-works')}
              className={`py-1 transition-all ${
                currentView === 'how-it-works'
                  ? 'text-ink-text font-bold border-b border-ink-text'
                  : 'hover:text-ink-text'
              }`}
            >
              How It Works
            </button>
            <button
              onClick={() => onSelectView('standards')}
              className={`py-1 transition-all ${
                currentView === 'standards'
                  ? 'text-ink-text font-bold border-b border-ink-text'
                  : 'hover:text-ink-text'
              }`}
            >
              Standards
            </button>
            <button
              onClick={() => onSelectView('analyze')}
              className={`py-1 transition-all ${
                currentView === 'analyze'
                  ? 'text-ink-text font-bold border-b border-ink-text'
                  : 'hover:text-ink-text'
              }`}
            >
              Workspace
            </button>
            <button
              onClick={() => onSelectView('dashboard')}
              className={`py-1 transition-all ${
                currentView === 'dashboard'
                  ? 'text-ink-text font-bold border-b border-ink-text'
                  : 'hover:text-ink-text'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => onSelectView('decision-package')}
              className={`py-1 transition-all ${
                currentView === 'decision-package'
                  ? 'text-ink-text font-bold border-b border-ink-text'
                  : 'hover:text-ink-text'
              }`}
            >
              Decision Package
            </button>
          </nav>
        </div>

        {/* Right: Telemetry & Actions */}
        <div className="flex items-center gap-4">
          {/* Subtle Telemetry */}
          <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded border border-parchment-border bg-parchment-surface text-[10px] font-mono text-ink-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-subtle-pulse" />
            <span>BIS ENGINE</span>
            <span className="text-slate-300">|</span>
            <span>{runId}</span>
          </div>

          {/* Quick Search */}
          <div className="relative">
            {showSearch ? (
              <form onSubmit={handleSearch} className="flex items-center">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search IS standards..."
                  className="w-44 sm:w-56 px-2.5 py-1 text-xs bg-parchment-surface border border-parchment-border rounded text-ink-text focus:outline-none focus:border-mineral-blue"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => setShowSearch(false)}
                  className="ml-1 text-ink-faint hover:text-ink-text"
                >
                  <X size={14} />
                </button>
              </form>
            ) : (
              <button
                onClick={() => setShowSearch(true)}
                className="p-1.5 text-ink-muted hover:text-ink-text transition-colors rounded hover:bg-parchment-subtle"
                title="Search Standards"
              >
                <Search size={16} />
              </button>
            )}
          </div>

          {/* Standards for a Stronger India Header Text */}
          <div className="hidden xl:block text-right text-[9px] font-bold tracking-[0.2em] text-ink-faint uppercase font-serif leading-tight pl-2 border-l border-parchment-border">
            <div>STANDARDS</div>
            <div>FOR A STRONGER INDIA</div>
          </div>

          {/* Primary Action Button */}
          {currentView !== 'analyze' && (
            <button
              onClick={() => onSelectView('analyze')}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold shadow-xs transition-all"
            >
              <span>Analyze Specification</span>
              <ArrowRight size={13} />
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
