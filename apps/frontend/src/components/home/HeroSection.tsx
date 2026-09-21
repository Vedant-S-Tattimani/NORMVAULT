import React, { useState } from 'react';
import { X, Menu } from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface HeroSectionProps {
  onNavigate: (view: ViewType) => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onNavigate }) => {
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleMobileNav = (view: ViewType) => {
    setIsMobileMenuOpen(false);
    onNavigate(view);
  };

  return (
    <div className="relative w-full min-h-screen bg-[#F6F2EA] flex flex-col justify-between overflow-hidden border-b border-[#8C8275]/25">
      {/* Background Editorial Tint & Fine Grid Overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(#8C8275_0.75px,transparent_0.75px)] [background-size:24px_24px] opacity-15 pointer-events-none" />

      {/* Top Header */}
      <header className="max-w-[1440px] w-full mx-auto px-6 lg:px-12 pt-6 pb-4 flex items-center justify-between z-30 shrink-0">
        {/* Brand Logo */}
        <div
          onClick={() => onNavigate('home')}
          className="cursor-pointer flex items-center gap-0.5 tracking-wide"
        >
          <span className="text-2xl lg:text-[1.7rem] font-serif font-medium text-[#1E2320]">
            NORM<span className="text-[#2C6E80] font-serif font-medium">VAULT</span>
          </span>
        </div>

        {/* Center Nav Links (Desktop) */}
        <nav className="hidden md:flex items-center space-x-9 text-[13px] font-serif text-[#4A4E49] tracking-normal">
          <button
            onClick={() => onNavigate('home')}
            className="text-[#1E2320] font-medium border-b border-[#1E2320] pb-0.5 transition-colors cursor-pointer"
          >
            Home
          </button>
          <button
            onClick={() => onNavigate('standards')}
            className="hover:text-[#1E2320] transition-colors cursor-pointer"
          >
            Standards
          </button>
          <button
            onClick={() => onNavigate('how-it-works')}
            className="hover:text-[#1E2320] transition-colors cursor-pointer"
          >
            How It Works
          </button>
          <button
            onClick={() => scrollToSection('impact-section')}
            className="hover:text-[#1E2320] transition-colors cursor-pointer"
          >
            Impact
          </button>
          <button
            onClick={() => setIsAboutModalOpen(true)}
            className="hover:text-[#1E2320] transition-colors cursor-pointer"
          >
            About
          </button>
        </nav>

        {/* Top Right Header Text & Mobile Menu Button */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:block text-right text-[9px] md:text-[10px] tracking-[0.22em] text-[#787165] uppercase font-serif leading-tight">
            <div>STANDARDS</div>
            <div>FOR A STRONGER</div>
            <div>INDIA</div>
          </div>

          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="md:hidden p-1.5 rounded-lg border border-[#8C8275]/30 text-[#1E2320] hover:bg-[#EAE4D8] transition-colors cursor-pointer"
            aria-label="Open Navigation Menu"
          >
            <Menu size={20} />
          </button>
        </div>
      </header>

      {/* Mobile Slide-Out Drawer */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs">
          <div className="w-[280px] sm:w-[320px] h-full bg-[#FCFAF6] border-l border-[#8C8275]/30 shadow-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-[#8C8275]/20 mb-6">
                <span className="text-xl font-serif font-medium text-[#1E2320]">
                  NORM<span className="text-[#2C6E80]">VAULT</span>
                </span>
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-1 rounded text-[#787165] hover:text-[#1E2320] cursor-pointer"
                >
                  <X size={20} />
                </button>
              </div>

              <nav className="space-y-4 text-sm font-serif">
                <button
                  onClick={() => handleMobileNav('home')}
                  className="block w-full text-left py-1 text-[#1E2320] font-medium border-b border-transparent hover:border-[#1E2320] transition-colors cursor-pointer"
                >
                  Home
                </button>
                <button
                  onClick={() => handleMobileNav('standards')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  Standards Catalog
                </button>
                <button
                  onClick={() => handleMobileNav('analyze')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  Specification Analysis
                </button>
                <button
                  onClick={() => handleMobileNav('dashboard')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  Procurement Dashboard
                </button>
                <button
                  onClick={() => handleMobileNav('decision-package')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  Decision Package
                </button>

                <div className="pt-4 border-t border-[#8C8275]/15 space-y-3 text-xs text-[#686358]">
                  <button
                    onClick={() => handleMobileNav('how-it-works')}
                    className="block w-full text-left py-0.5 hover:text-[#1E2320] transition-colors cursor-pointer"
                  >
                    How It Works
                  </button>
                  <button
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      scrollToSection('impact-section');
                    }}
                    className="block w-full text-left py-0.5 hover:text-[#1E2320] transition-colors cursor-pointer"
                  >
                    Impact & Outcomes
                  </button>
                  <button
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      setIsAboutModalOpen(true);
                    }}
                    className="block w-full text-left py-0.5 hover:text-[#1E2320] transition-colors cursor-pointer"
                  >
                    About NORMVAULT
                  </button>
                </div>
              </nav>
            </div>

            <div className="pt-4 border-t border-[#8C8275]/20 text-[10px] font-mono tracking-widest text-[#787165] uppercase">
              STANDARDS FOR A STRONGER INDIA
            </div>
          </div>
        </div>
      )}

      {/* Main Hero Container with Flanking Columns & Centerpiece */}
      <main className="max-w-[1440px] w-full mx-auto px-6 lg:px-12 flex-1 relative flex flex-col justify-between items-center z-10 min-h-0 pt-2">
        {/* Left & Right Flanking Editorial Metadata (Desktop) */}
        <div className="absolute left-6 lg:left-12 top-[40%] -translate-y-1/2 hidden xl:block z-20">
          <div className="border-l border-[#8C8275]/50 pl-3 text-[9.5px] tracking-[0.22em] text-[#787165] font-serif leading-loose uppercase">
            <div>ACCURATE</div>
            <div>COMPLIANT</div>
            <div>TRANSPARENT</div>
            <div>AUDITABLE</div>
          </div>
        </div>

        <div className="absolute right-6 lg:right-12 top-[40%] -translate-y-1/2 hidden xl:block z-20 text-right">
          <div className="border-r border-[#8C8275]/50 pr-3 text-[9.5px] tracking-[0.22em] text-[#787165] font-serif leading-loose uppercase">
            <div>GFR 144(I)</div>
            <div>BIS ACT 2016</div>
            <div>DPIIT QCOS</div>
            <div>CVC / CAG</div>
          </div>
        </div>

        {/* Center Editorial Hero Content */}
        <div className="text-center max-w-2xl mx-auto flex flex-col items-center shrink-0 z-20">
          {/* Eyebrow */}
          <div className="text-[10.5px] md:text-[11.5px] font-serif tracking-[0.24em] text-[#6E726C] uppercase mb-3">
            INDIAN STANDARDS. SMARTER PROCUREMENT.
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-[3.75rem] font-serif font-normal text-[#1E2320] tracking-normal leading-[1.08] mb-3.5">
            From Specifications <br />
            to the Right Standards.
          </h1>

          {/* Subtitle */}
          <p className="text-xs sm:text-[13.5px] md:text-[14.5px] text-[#525650] leading-[1.65] max-w-[560px] mb-5 font-serif font-normal">
            An AI-powered recommendation engine that helps government departments and PSUs
            identify applicable Indian Standards for accurate, compliant and future-ready
            procurement specifications.
          </p>

          {/* Action Buttons */}
          <div className="flex items-center justify-center gap-4 mb-3">
            <button
              onClick={() => onNavigate('analyze')}
              className="inline-flex items-center gap-2 px-6 py-2 rounded-lg bg-[#1E231D] hover:bg-[#0D100C] text-[#FCFAF6] font-serif font-normal text-xs sm:text-sm shadow-xs transition-all group cursor-pointer"
            >
              <span>Analyze Specification</span>
              <span className="text-sm font-light group-hover:translate-x-0.5 transition-transform">→</span>
            </button>

            <button
              onClick={() => onNavigate('standards')}
              className="inline-flex items-center gap-2 px-6 py-2 rounded-lg border border-[#3A3830]/40 text-[#1E2320] bg-[#EFE9DE]/50 hover:bg-[#EFE9DE] font-serif font-normal text-xs sm:text-sm transition-all cursor-pointer"
            >
              <span>Explore Indian Standards</span>
            </button>
          </div>
        </div>

        {/* Centerpiece Double-Exposure Watercolor Artwork */}
        <div className="w-full flex-1 min-h-0 flex items-end justify-center relative overflow-hidden pointer-events-none select-none z-10">
          <img
            src="/hero_centerpiece.png"
            alt="Indian Standards, Parliament and Specifications"
            className="w-full max-w-[1024px] h-full object-contain object-bottom filter contrast-[1.03] brightness-[1.01]"
          />
        </div>

        {/* Bottom Left Corner Signature */}
        <div className="absolute bottom-4 left-6 lg:left-12 z-20">
          <div className="border-l border-[#8C8275]/50 pl-3 text-[9.5px] md:text-[10px] tracking-[0.22em] text-[#787165] font-serif leading-relaxed uppercase">
            <div>BUILT FOR</div>
            <div>GOVERNMENT AND PSUS</div>
          </div>
        </div>

        {/* Bottom Right Corner Signature */}
        <div className="absolute bottom-4 right-6 lg:right-12 z-20">
          <div className="border-l border-[#8C8275]/50 pl-3 text-[9.5px] md:text-[10px] tracking-[0.22em] text-[#787165] font-serif leading-relaxed uppercase text-left">
            <div>POWERED BY</div>
            <div>INDIAN STANDARDS</div>
          </div>
        </div>
      </main>

      {/* About NORMVAULT Modal */}
      {isAboutModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
          <div className="bg-[#FCFAF6] rounded-2xl border border-[#D9D0C1] shadow-2xl max-w-2xl w-full p-8 relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setIsAboutModalOpen(false)}
              className="absolute top-5 right-5 text-ink-muted hover:text-ink-text cursor-pointer"
            >
              <X size={20} />
            </button>

            <div>
              <h3 className="text-2xl font-serif font-bold text-ink-text mb-2">About NORMVAULT</h3>
              <p className="text-xs font-mono text-ink-muted mb-4">
                Developed for Smart India Hackathon (SIH) Problem Statement 26108:
                "AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications."
              </p>
              <div className="text-xs text-ink-muted space-y-3 leading-relaxed">
                <p>
                  NORMVAULT addresses the critical challenge faced by Indian public procurement entities
                  (NTPC, NHPC, BHEL, Indian Railways, Defense, GeM) where tender specifications frequently
                  cite outdated, superseded, or conflicting Indian Standards (e.g. citing IS 325 instead of
                  mandated IS 12615:2018).
                </p>
                <p>
                  By combining natural language processing, vector retrieval, and deterministic graph
                  verification against the Bureau of Indian Standards catalog, NORMVAULT ensures complete
                  legal compliance with the BIS Act 2016 and DPIIT Quality Control Orders.
                </p>
                <div className="pt-4 border-t border-parchment-border/60 flex items-center justify-between">
                  <span className="font-mono text-[11px] text-[#2C6E80] font-semibold">
                    Ministry of Consumer Affairs, Food and Public Distribution
                  </span>
                  <button
                    onClick={() => setIsAboutModalOpen(false)}
                    className="px-4 py-1.5 rounded bg-ink-text text-white text-xs font-serif cursor-pointer"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
