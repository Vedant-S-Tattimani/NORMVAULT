import React, { useState } from 'react';
import { Search, BookOpen, ShieldCheck, Tag } from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface StandardsQuickExplorerProps {
  onNavigate: (view: ViewType, query?: string) => void;
}

export const StandardsQuickExplorer: React.FC<StandardsQuickExplorerProps> = ({ onNavigate }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const featuredStandards = [
    {
      code: 'IS 456:2000',
      title: 'Plain and Reinforced Concrete — Code of Practice',
      domain: 'Civil Engineering',
      qco: false,
      relevance: 'Primary structural design standard across all Indian civil infrastructure.',
    },
    {
      code: 'IS 1786:2008',
      title: 'High Strength Deformed Steel Bars and Wires for Concrete Reinforcement',
      domain: 'Metallurgy & Steel',
      qco: true,
      relevance: 'Mandatory DPIIT QCO certification for all TMT reinforcement rebar.',
    },
    {
      code: 'IS 12615:2018',
      title: 'Line Operated Three-Phase AC Motors — Efficiency Classes (IE Code)',
      domain: 'Electrical Engineering',
      qco: true,
      relevance: 'Mandated under Electric Motors QCO; completely supersedes legacy IS 325.',
    },
    {
      code: 'IS 2062:2011',
      title: 'Hot Rolled Medium and High Tensile Structural Steel — Specification',
      domain: 'Structural Steel',
      qco: true,
      relevance: 'Core standard for all structural fabrication in power and railway tenders.',
    },
  ];

  const categories = [
    { name: 'Civil & Structural', query: 'IS 456' },
    { name: 'Steel & Metallurgy', query: 'IS 1786' },
    { name: 'Electrical & Power', query: 'IS 12615' },
    { name: 'Pipes & Pressure Vessels', query: 'IS 1239' },
    { name: 'Fire Safety & Alarms', query: 'IS 2189' },
    { name: 'Cement & Aggregates', query: 'IS 269' },
  ];

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNavigate('standards', searchTerm.trim() || undefined);
  };

  return (
    <section className="py-24 px-6 lg:px-12 bg-[#EDE8DC] border-b border-[#8C8275]/25">
      <div className="max-w-[1440px] mx-auto">
        <div className="max-w-3xl mx-auto text-center mb-12">
          <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-2">
            STANDARDS CATALOG EXPLORER
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[#1E2320] leading-tight mb-4">
            Authoritative BIS Knowledge Foundation
          </h2>
          <p className="text-sm sm:text-base text-[#525650] font-serif leading-relaxed">
            Search across 22,000+ Indian Standards with active edition currentness, normative references, 
            and mandatory Quality Control Orders.
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearchSubmit} className="mt-8 relative max-w-xl mx-auto">
            <div className="relative flex items-center">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by IS code (e.g. IS 456, IS 1786) or keyword..."
                className="w-full pl-11 pr-32 py-3.5 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/40 text-sm text-[#1E2320] placeholder-[#787165] focus:outline-hidden focus:border-[#2C6E80] shadow-xs"
              />
              <Search size={17} className="absolute left-4 text-[#787165]" />
              <button
                type="submit"
                className="absolute right-2 px-4 py-2 rounded-lg bg-[#1E231D] hover:bg-[#0D100C] text-white text-xs font-medium transition-colors cursor-pointer"
              >
                Search Catalog
              </button>
            </div>
          </form>

          {/* Quick Category Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
            <span className="text-xs font-mono text-[#787165] mr-1">Frequent:</span>
            {categories.map((cat) => (
              <button
                key={cat.name}
                onClick={() => onNavigate('standards', cat.query)}
                className="px-3 py-1 rounded-full bg-[#FCFAF6] border border-[#8C8275]/25 text-xs text-[#525650] hover:border-[#2C6E80] hover:text-[#2C6E80] transition-colors cursor-pointer"
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        {/* Featured Standards Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredStandards.map((std) => (
            <div
              key={std.code}
              className="bg-[#FCFAF6] rounded-2xl p-6 border border-[#8C8275]/30 shadow-xs flex flex-col justify-between hover:border-[#2C6E80] transition-all group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono font-bold text-sm text-[#1E2320] group-hover:text-[#2C6E80] transition-colors">
                    {std.code}
                  </span>
                  {std.qco && (
                    <span className="inline-flex items-center gap-1 text-[9px] font-mono uppercase bg-emerald-100/70 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-300/50">
                      <ShieldCheck size={10} />
                      <span>QCO Mandated</span>
                    </span>
                  )}
                </div>

                <div className="text-[11px] font-mono text-[#787165] mb-2 flex items-center gap-1">
                  <Tag size={11} />
                  <span>{std.domain}</span>
                </div>

                <h4 className="font-serif font-bold text-xs sm:text-sm text-[#1E2320] mb-2 leading-snug">
                  {std.title}
                </h4>

                <p className="text-xs text-[#525650] font-serif leading-relaxed mb-4">
                  {std.relevance}
                </p>
              </div>

              <div className="pt-3 border-t border-[#8C8275]/15">
                <button
                  onClick={() => onNavigate('standards')}
                  className="inline-flex items-center gap-1.5 text-xs font-serif font-semibold text-[#2C6E80] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  <BookOpen size={12} />
                  <span>View Clauses & Dependencies</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
