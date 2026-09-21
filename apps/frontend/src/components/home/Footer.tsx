import React from 'react';
import { ShieldCheck, ArrowUp } from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface FooterProps {
  onNavigate: (view: ViewType) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="bg-[#181C17] text-[#D0C9BD] border-t border-[#3A4038] pt-16 pb-12 px-6 lg:px-12 font-sans">
      <div className="max-w-[1440px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-white/10">
          {/* Brand & Purpose Column */}
          <div className="lg:col-span-2">
            <div
              onClick={() => onNavigate('home')}
              className="cursor-pointer flex items-center gap-1 mb-4"
            >
              <span className="text-2xl font-serif font-black tracking-tight text-[#FCFAF6]">
                NORM<span className="text-[#64B5F6] font-sans font-extrabold">VAULT</span>
              </span>
            </div>
            <p className="text-xs text-[#A6AEA4] font-serif leading-relaxed max-w-sm mb-6">
              An AI-powered recommendation and verification engine for identifying applicable Indian Standards 
              for public procurement specifications, ensuring complete compliance with the BIS Act 2016 and DPIIT QCOs.
            </p>

            <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 text-xs font-mono text-[#A6AEA4] max-w-sm">
              <div className="text-[10px] uppercase tracking-wider text-[#64B5F6] font-bold mb-1 flex items-center gap-1.5">
                <ShieldCheck size={13} />
                <span>Smart India Hackathon 2024</span>
              </div>
              <div className="text-[11px] text-[#E0DDD5]">
                Problem Statement 26108: AI-Powered Recommendation Engine for Applicable Indian Standards.
              </div>
            </div>
          </div>

          {/* Col 1: Platform */}
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-[#FCFAF6] mb-4">
              Platform
            </h4>
            <ul className="space-y-2.5 text-xs text-[#A6AEA4]">
              <li>
                <button
                  onClick={() => onNavigate('how-it-works')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  How It Works (7 Stages)
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('analyze')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Specification Analysis
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Indian Standards Catalog
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('dashboard')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Procurement Dashboard
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('decision-package')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Decision Package Engine
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Normative Dependency Graph
                </button>
              </li>
            </ul>
          </div>

          {/* Col 2: Statutory Framework */}
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-[#FCFAF6] mb-4">
              Statutory Framework
            </h4>
            <ul className="space-y-2.5 text-xs text-[#A6AEA4]">
              <li className="flex items-center gap-1">
                <span>Bureau of Indian Standards Act 2016</span>
              </li>
              <li className="flex items-center gap-1">
                <span>DPIIT Quality Control Orders</span>
              </li>
              <li className="flex items-center gap-1">
                <span>General Financial Rules 2017 (Rule 144)</span>
              </li>
              <li className="flex items-center gap-1">
                <span>CVC Guidelines on Procurement</span>
              </li>
              <li className="flex items-center gap-1">
                <span>GeM Technical Bid Mandates</span>
              </li>
            </ul>
          </div>

          {/* Col 3: Standards Divisions */}
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-[#FCFAF6] mb-4">
              Standards Divisions
            </h4>
            <ul className="space-y-2.5 text-xs text-[#A6AEA4]">
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Civil Engineering (CED)
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Electrotechnical (ETD)
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Mechanical Engineering (MED)
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Metallurgical Engineering (MTD)
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  Chemical Engineering (CHD)
                </button>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-[#7E887E]">
          <div className="flex flex-wrap items-center gap-4">
            <div>© 2026 NORMVAULT. All Rights Reserved.</div>
            <span className="hidden sm:inline">•</span>
            <div>Viksit Bharat 2047 Technical Infrastructure</div>
          </div>

          <div className="flex items-center gap-6">
            <span className="text-[11px] text-[#A6AEA4]">
              Deterministic Hash Verification Active
            </span>
            <button
              onClick={scrollToTop}
              className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 text-white flex items-center justify-center transition-colors cursor-pointer"
              title="Scroll to Top"
            >
              <ArrowUp size={15} />
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};
