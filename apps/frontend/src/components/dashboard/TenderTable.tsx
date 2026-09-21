import React, { useState } from 'react';
import { ProcurementSpecification } from '../../types/requirement';
import { StatusBadge } from '../common/StatusBadge';
import { ArrowRight, Search } from 'lucide-react';

interface TenderTableProps {
  specifications: ProcurementSpecification[];
  onSelectSpecification: (spec: ProcurementSpecification) => void;
}

export const TenderTable: React.FC<TenderTableProps> = ({
  specifications,
  onSelectSpecification,
}) => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filtered = specifications.filter((spec) => {
    const matchesSearch =
      spec.tender_reference.toLowerCase().includes(search.toLowerCase()) ||
      spec.title.toLowerCase().includes(search.toLowerCase()) ||
      spec.issuing_organization.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === 'ALL' || spec.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="parchment-card rounded-xl p-5 mb-8">
      {/* Header & Search */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-4 pb-4 border-b border-parchment-border">
        <div>
          <h2 className="text-base font-bold font-serif text-ink-text">
            Active Procurement Specifications
          </h2>
          <p className="text-xs text-ink-muted">
            Monitored tenders across Central PSUs and Ministries for BIS Act compliance.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative flex-1 sm:w-64">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search tender reference..."
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-parchment-surface border border-parchment-border rounded-lg text-ink-text focus:outline-none focus:border-mineral-blue"
            />
          </div>

          <div className="relative">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 text-xs bg-parchment-surface border border-parchment-border rounded-lg text-ink-text focus:outline-none focus:border-mineral-blue cursor-pointer"
            >
              <option value="ALL">All Readiness States</option>
              <option value="READY_FOR_TENDER">Ready for Tender</option>
              <option value="ACTION_REQUIRED">Action Required</option>
              <option value="AUDIT_READY">Audit Ready</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-parchment-border text-[10px] text-ink-muted uppercase">
              <th className="py-2.5 px-3">Tender Reference & Title</th>
              <th className="py-2.5 px-3">Issuing Authority</th>
              <th className="py-2.5 px-3">Requirements</th>
              <th className="py-2.5 px-3">Readiness Verdict</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-parchment-border/60">
            {filtered.map((spec) => (
              <tr
                key={spec.id}
                onClick={() => onSelectSpecification(spec)}
                className="hover:bg-parchment-subtle/50 cursor-pointer transition-colors group"
              >
                <td className="py-3 px-3">
                  <div className="font-bold text-ink-text font-serif text-xs group-hover:text-mineral-blue transition-colors">
                    {spec.tender_reference}
                  </div>
                  <div className="text-[11px] text-ink-muted font-sans truncate max-w-sm">
                    {spec.title}
                  </div>
                </td>
                <td className="py-3 px-3 text-ink-text font-sans">
                  {spec.issuing_organization}
                </td>
                <td className="py-3 px-3 text-ink-text">
                  <span className="font-bold">{spec.total_requirements_count || 18}</span> extracted
                </td>
                <td className="py-3 px-3">
                  <StatusBadge status={spec.status} size="sm" />
                </td>
                <td className="py-3 px-3 text-right">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectSpecification(spec);
                    }}
                    className="inline-flex items-center gap-1 text-mineral-blue hover:text-mineral-dark font-semibold text-xs transition-colors"
                  >
                    <span>Analyze</span>
                    <ArrowRight size={12} className="group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
