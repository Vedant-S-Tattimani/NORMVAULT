import React from 'react';
import { ViewType } from '../components/common/EditorialHeader';
import { HeroSection } from '../components/home/HeroSection';
import { EcosystemBanner } from '../components/home/EcosystemBanner';
import { ProblemSection } from '../components/home/ProblemSection';
import { WorkflowSection } from '../components/home/WorkflowSection';
import { CapabilitiesSection } from '../components/home/CapabilitiesSection';
import { ImpactMetricsSection } from '../components/home/ImpactMetricsSection';
import { StandardsQuickExplorer } from '../components/home/StandardsQuickExplorer';
import { InstitutionalCTA } from '../components/home/InstitutionalCTA';
import { Footer } from '../components/home/Footer';

interface HomePageProps {
  onNavigate: (view: ViewType, query?: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  return (
    <div className="bg-[#F6F2EA] min-h-screen text-[#1E2320]">
      {/* 1. Full-Screen Editorial Hero with Smooth-Scroll Links */}
      <HeroSection onNavigate={(view) => onNavigate(view)} />

      {/* 2. Institutional Ecosystem & Trust Bar with Live Catalog Health Strip */}
      <EcosystemBanner />

      {/* 3. The Core Procurement Challenge & Interactive Clause Reconciliation Teaser */}
      <ProblemSection onNavigate={(view) => onNavigate(view)} />

      {/* 4. 7-Stage Deterministic Workflow & Pipeline */}
      <WorkflowSection onNavigate={(view) => onNavigate(view)} />

      {/* 5. Role-Specific Value for Public Procurement Stakeholders */}
      <CapabilitiesSection onNavigate={(view) => onNavigate(view)} />

      {/* 6. Interactive Standards Catalog Quick Explorer */}
      <StandardsQuickExplorer onNavigate={onNavigate} />

      {/* 7. Measurable Real-World Impact & SIH 26108 Banner */}
      <ImpactMetricsSection />

      {/* 8. Institutional Call To Action */}
      <InstitutionalCTA onNavigate={(view) => onNavigate(view)} />

      {/* 9. Comprehensive Institutional Footer */}
      <Footer onNavigate={(view) => onNavigate(view)} />
    </div>
  );
};
