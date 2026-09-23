import React, { useState, memo } from 'react';
import { ArrowRight, Search, X } from 'lucide-react';

export type ViewType = 'home' | 'analyze' | 'standards' | 'dashboard' | 'decision-package' | 'how-it-works' | 'benchmarks' | 'comparative';

interface EditorialHeaderProps {
  currentView: ViewType;
  onSelectView: (view: ViewType) => void;
  runId?: string;
}

export const EditorialHeader: React.FC<EditorialHeaderProps> = memo(({
  currentView,
  onSelectView,
}) => {
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSelectView('standards');
    }
  };

  const navItemClass = (view: ViewType) =>
    `py-1 text-xs font-medium uppercase tracking-wider transition-colors duration-150 cursor-pointer ${
      currentView === view
        ? 'text-ink-text font-bold border-b-2 border-ink-text'
        : 'text-ink-muted hover:text-ink-text'
    }`;

  return (
    <header className="bg-parchment-base border-b border-parchment-border sticky top-0 z-40">
      <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        {/* Left: Brand & Navigation */}
        <div className="flex items-center gap-8">
          <div
            onClick={() => onSelectView('home')}
            className="cursor-pointer flex items-center gap-2 select-none group"
          >
            <span className="text-2xl font-serif font-black tracking-tight text-ink-text">
              NORM<span className="text-mineral-blue font-sans font-extrabold">VAULT</span>
            </span>
          </div>

          {/* Center Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6">
            <button
              onClick={() => onSelectView('home')}
              className={navItemClass('home')}
            >
              Home
            </button>
            <button
              onClick={() => onSelectView('how-it-works')}
              className={navItemClass('how-it-works')}
            >
              How It Works
            </button>
            <button
              onClick={() => onSelectView('standards')}
              className={navItemClass('standards')}
            >
              Standards
            </button>
            <button
              onClick={() => onSelectView('analyze')}
              className={navItemClass('analyze')}
            >
              Workspace
            </button>
            <button
              onClick={() => onSelectView('dashboard')}
              className={navItemClass('dashboard')}
            >
              Dashboard
            </button>
            <button
              onClick={() => onSelectView('decision-package')}
              className={navItemClass('decision-package')}
            >
              Decision Package
            </button>
            <button
              onClick={() => onSelectView('benchmarks')}
              className={navItemClass('benchmarks')}
            >
              Benchmarks
            </button>
            <button
              onClick={() => onSelectView('comparative')}
              className={navItemClass('comparative')}
            >
              Bidder Evaluation
            </button>
          </nav>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-4">
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
                  className="ml-1 text-ink-faint hover:text-ink-text cursor-pointer"
                >
                  <X size={14} />
                </button>
              </form>
            ) : (
              <button
                onClick={() => setShowSearch(true)}
                className="p-1.5 text-ink-muted hover:text-ink-text transition-colors rounded hover:bg-parchment-subtle cursor-pointer"
                title="Search Standards"
              >
                <Search size={16} />
              </button>
            )}
          </div>

          {/* Standards for a Stronger India Header Text */}
          <div className="hidden xl:block text-right text-[9px] font-bold tracking-[0.2em] text-ink-faint uppercase font-serif leading-tight pl-3 border-l border-parchment-border">
            <div>STANDARDS</div>
            <div>FOR A STRONGER INDIA</div>
          </div>

          {/* Primary Action Button */}
          {currentView !== 'analyze' && (
            <button
              onClick={() => onSelectView('analyze')}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold shadow-xs transition-colors duration-150 cursor-pointer"
            >
              <span>Analyze Specification</span>
              <ArrowRight size={13} />
            </button>
          )}
        </div>
      </div>
    </header>
  );
});
