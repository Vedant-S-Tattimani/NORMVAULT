import React, { useState, useEffect } from 'react';
import { ProcurementSpecification } from '../types/requirement';
import { listSpecifications } from '../api/specifications';
import { TenderTable } from '../components/dashboard/TenderTable';
import { GazetteWatchWidget } from '../components/dashboard/GazetteWatchWidget';
import { ShieldCheck, AlertTriangle, Layers, FileCheck } from 'lucide-react';

interface DashboardPageProps {
  onSelectSpecification: (spec: ProcurementSpecification) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onSelectSpecification,
}) => {
  const [specifications, setSpecifications] = useState<ProcurementSpecification[]>([]);

  useEffect(() => {
    async function load() {
      const data = await listSpecifications();
      setSpecifications(data);
    }
    load();
  }, []);

  return (
    <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Executive Header */}
      <div className="parchment-card rounded-xl p-5 mb-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-mineral-light text-mineral-dark font-semibold border border-mineral-blue/30 uppercase">
                NATIONAL PROCUREMENT INTELLIGENCE
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold font-serif text-ink-text">
              Procurement Intelligence Dashboard
            </h1>
            <p className="text-xs text-ink-muted mt-1 font-serif">
              Operational compliance monitor for public procurement specifications and Indian Standards (BIS) governance.
            </p>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono text-ink-muted">
            <span className="p-2 rounded bg-parchment-subtle border border-parchment-border">
              Tenders Monitored: <strong className="text-ink-text">{specifications.length}</strong>
            </span>
            <span className="p-2 rounded bg-status-sageBg text-status-sage border border-status-sageBorder font-bold">
              QCO Enforcement: 100%
            </span>
          </div>
        </div>
      </div>

      {/* KPI Metric Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="parchment-card rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono uppercase text-ink-muted">ACTIVE SPECIFICATIONS</span>
            <Layers size={16} className="text-mineral-blue" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold font-serif text-ink-text">
            {specifications.length}
          </div>
          <p className="text-[11px] text-ink-muted mt-1 font-mono">
            Across 4 Central PSUs
          </p>
        </div>

        <div className="parchment-card rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono uppercase text-ink-muted">READINESS STATE</span>
            <ShieldCheck size={16} className="text-status-sage" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold font-serif text-status-sage">
            1
          </div>
          <p className="text-[11px] text-ink-muted mt-1 font-mono">
            Ready for Immediate Tender
          </p>
        </div>

        <div className="parchment-card rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono uppercase text-ink-muted">ACTION REQUIRED</span>
            <AlertTriangle size={16} className="text-status-amber" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold font-serif text-status-amber">
            2
          </div>
          <p className="text-[11px] text-ink-muted mt-1 font-mono">
            Pre-Tender Corrigendum Needed
          </p>
        </div>

        <div className="parchment-card rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono uppercase text-ink-muted">STATUTORY MANDATES</span>
            <FileCheck size={16} className="text-status-indigo" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold font-serif text-status-indigo">
            3 QCOs
          </div>
          <p className="text-[11px] text-ink-muted mt-1 font-mono">
            In Full Statutory Enforcement
          </p>
        </div>
      </div>

      {/* Main Split: Active Tenders Table + Gazette Watch */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8">
          <TenderTable
            specifications={specifications}
            onSelectSpecification={onSelectSpecification}
          />
        </div>

        <div className="lg:col-span-4">
          <GazetteWatchWidget />
        </div>
      </div>
    </div>
  );
};
