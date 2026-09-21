import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, CheckCircle2, Lock } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  className = '',
}) => {
  const sizeClasses = size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  switch (status) {
    case 'APPLICABLE':
    case 'READY_FOR_PROCUREMENT':
    case 'READY_FOR_TENDER':
    case 'AUDIT_READY':
    case 'CURRENT':
    case 'VERIFIED':
      return (
        <span
          className={`inline-flex items-center gap-1 rounded font-mono font-semibold bg-status-sageBg text-status-sage border border-status-sageBorder ${sizeClasses} ${className}`}
        >
          <CheckCircle2 size={size === 'sm' ? 10 : 12} />
          <span>{status.replace(/_/g, ' ')}</span>
        </span>
      );

    case 'ACTION_REQUIRED':
    case 'ACTION_REQUIRED_BEFORE_TENDER':
    case 'CONDITIONAL':
    case 'REVIEW_REQUIRED':
      return (
        <span
          className={`inline-flex items-center gap-1 rounded font-mono font-semibold bg-status-amberBg text-status-amber border border-status-amberBorder ${sizeClasses} ${className}`}
        >
          <AlertTriangle size={size === 'sm' ? 10 : 12} />
          <span>{status.replace(/_/g, ' ')}</span>
        </span>
      );

    case 'CRITICAL_AMBIGUITIES_DETECTED':
    case 'BLOCKING':
    case 'NOT_APPLICABLE':
    case 'SUPERSEDED':
    case 'WITHDRAWN':
    case 'NON_COMPLIANT':
      return (
        <span
          className={`inline-flex items-center gap-1 rounded font-mono font-semibold bg-status-crimsonBg text-status-crimson border border-status-crimsonBorder ${sizeClasses} ${className}`}
        >
          <AlertOctagon size={size === 'sm' ? 10 : 12} />
          <span>{status.replace(/_/g, ' ')}</span>
        </span>
      );

    case 'QCO_MANDATORY':
    case 'MANDATORY_IN_FORCE':
      return (
        <span
          className={`inline-flex items-center gap-1 rounded font-mono font-semibold bg-status-indigoBg text-status-indigo border border-status-indigoBorder ${sizeClasses} ${className}`}
        >
          <Lock size={size === 'sm' ? 10 : 12} />
          <span>MANDATORY QCO</span>
        </span>
      );

    default:
      return (
        <span
          className={`inline-flex items-center gap-1 rounded font-mono font-medium bg-parchment-subtle text-ink-muted border border-parchment-border ${sizeClasses} ${className}`}
        >
          <ShieldCheck size={size === 'sm' ? 10 : 12} />
          <span>{status.replace(/_/g, ' ')}</span>
        </span>
      );
  }
};
