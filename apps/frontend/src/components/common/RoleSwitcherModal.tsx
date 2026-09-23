import React from 'react';
import { X, ShieldCheck, CheckCircle2, UserCheck, Award, Lock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const RoleSwitcherModal: React.FC = () => {
  const { user, role, switchRole, isModalOpen, setIsModalOpen, isLoading } = useAuth();

  if (!isModalOpen) return null;

  const roles = [
    {
      id: 'PROCUREMENT_OFFICER' as const,
      name: 'Shri Rajesh Kumar',
      designation: 'Executive Engineer / Procurement Officer',
      department: 'National Thermal Power Corporation (NTPC)',
      icon: UserCheck,
      badgeColor: 'bg-blue-100 text-blue-800 border-blue-200',
      description: 'Prepares tender specifications, runs automated standards discovery, and generates official GeM BOQ schedules.',
    },
    {
      id: 'STANDARDS_AUDITOR' as const,
      name: 'Dr. Ananya Sharma',
      designation: 'Scientist-D / Standards Reviewer',
      department: 'Bureau of Indian Standards (BIS)',
      icon: Award,
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      description: 'Audits normative references, verifies Gazette amendments, and flags superseded standards or missing test criteria.',
    },
    {
      id: 'ADMIN' as const,
      name: 'Smt. Sunita Verma',
      designation: 'Chief Vigilance Officer & Administrator',
      department: 'Central Vigilance Commission (CVC)',
      icon: Lock,
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-200',
      description: 'Full oversight over compliance audit logs, statutory QCO enforcement, and system configuration.',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 animate-fade-in">
      <div className="bg-parchment-base border border-parchment-border rounded-lg shadow-2xl max-w-xl w-full p-6 relative">
        <button
          onClick={() => setIsModalOpen(false)}
          className="absolute top-4 right-4 text-ink-muted hover:text-ink-text transition-colors p-1"
        >
          <X size={18} />
        </button>

        <div className="flex items-center gap-2.5 mb-1">
          <ShieldCheck size={20} className="text-mineral-blue" />
          <h2 className="text-base font-serif font-bold text-ink-text tracking-tight uppercase">
            Government Audit Persona Switcher
          </h2>
        </div>
        <p className="text-xs text-ink-muted mb-6">
          Switch active officer credentials to test Role-Based Access Control (RBAC) and security enforcement.
        </p>

        <div className="space-y-3">
          {roles.map((r) => {
            const isCurrent = role === r.id;
            const Icon = r.icon;
            return (
              <div
                key={r.id}
                onClick={() => !isCurrent && switchRole(r.id)}
                className={`p-4 rounded-md border transition-all cursor-pointer ${
                  isCurrent
                    ? 'border-mineral-blue bg-parchment-surface ring-1 ring-mineral-blue/30 shadow-xs'
                    : 'border-parchment-border bg-parchment-subtle hover:border-ink-muted'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded border mt-0.5 ${r.badgeColor}`}>
                      <Icon size={16} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-ink-text">{r.name}</span>
                        {isCurrent && (
                          <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                            <CheckCircle2 size={10} /> Active Persona
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-ink-muted font-medium mt-0.5">{r.designation}</div>
                      <div className="text-[11px] text-ink-faint font-mono">{r.department}</div>
                      <p className="text-xs text-ink-text/80 mt-2 leading-relaxed">{r.description}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 pt-4 border-t border-parchment-border flex items-center justify-between text-xs text-ink-muted">
          <span className="font-mono text-[11px]">Active Session: {user?.username}</span>
          <button
            onClick={() => setIsModalOpen(false)}
            disabled={isLoading}
            className="px-4 py-1.5 rounded border border-parchment-border bg-parchment-surface hover:bg-parchment-base text-ink-text font-medium text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
