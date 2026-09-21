import React from 'react';
import { ArrowRight, ShieldCheck, FileCheck, BookOpen } from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface InstitutionalCTAProps {
  onNavigate: (view: ViewType) => void;
}

export const InstitutionalCTA: React.FC<InstitutionalCTAProps> = ({ onNavigate }) => {
  return (
    <section className="py-24 px-6 lg:px-12 bg-[#1E231D] text-[#FCFAF6] relative overflow-hidden">
      {/* Subtle Background Ornamentation */}
      <div className="absolute -right-20 -bottom-20 w-96 h-96 rounded-full bg-[#2C6E80]/10 blur-3xl pointer-events-none" />
      <div className="absolute -left-20 -top-20 w-96 h-96 rounded-full bg-[#8C8275]/10 blur-3xl pointer-events-none" />

      <div className="max-w-[1440px] mx-auto relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-[#64B5F6] text-[10px] font-mono font-semibold uppercase tracking-wider mb-6 border border-white/10">
            <ShieldCheck size={12} />
            <span>STATUTORY RIGOR • VERIFIABLE AUDIT TRAIL</span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-serif font-bold tracking-tight mb-6 leading-tight text-[#FCFAF6]">
            Eliminate Specification Risks from Your Next Tender
          </h2>

          <p className="text-sm sm:text-base text-[#D0C9BD] font-serif leading-relaxed mb-10 max-w-2xl mx-auto">
            Join public procurement officers, chief engineers, and tender committees across India in generating 
            authoritative, DPIIT QCO-compliant, and audit-proof technical specifications.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => onNavigate('analyze')}
              className="inline-flex items-center gap-2 px-7 py-3 rounded-xl bg-[#2C6E80] hover:bg-[#235866] text-white font-medium text-sm shadow-md transition-all group cursor-pointer"
            >
              <span>Analyze Specification Document</span>
              <ArrowRight size={15} className="group-hover:translate-x-0.5 transition-transform" />
            </button>

            <button
              onClick={() => onNavigate('standards')}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-white/20 hover:bg-white/10 text-[#FCFAF6] font-medium text-sm transition-all cursor-pointer"
            >
              <BookOpen size={15} />
              <span>Explore Standards Library</span>
            </button>

            <button
              onClick={() => onNavigate('decision-package')}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-white/20 hover:bg-white/10 text-[#FCFAF6] font-medium text-sm transition-all cursor-pointer"
            >
              <FileCheck size={15} />
              <span>Sample Decision Package</span>
            </button>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10 flex flex-wrap items-center justify-center gap-6 text-xs text-[#A6AEA4] font-mono">
            <div>✓ Zero Vendor Hallucination</div>
            <div>•</div>
            <div>✓ 22,000+ BIS Standards Indexed</div>
            <div>•</div>
            <div>✓ CVC & CAG Audit Compliant</div>
          </div>
        </div>
      </div>
    </section>
  );
};
