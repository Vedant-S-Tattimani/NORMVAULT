import React from 'react';
import { IndianStandard } from '../../types/standard';
import { X, Scale } from 'lucide-react';

interface QcoMandateDrawerProps {
  standard: IndianStandard | null;
  isOpen: boolean;
  onClose: () => void;
}

export const QcoMandateDrawer: React.FC<QcoMandateDrawerProps> = ({
  standard,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !standard) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30 backdrop-blur-xs">
      <div className="w-full max-w-md bg-parchment-surface h-full border-l border-parchment-border shadow-parchment-lg p-6 flex flex-col justify-between overflow-y-auto">
        <div>
          <div className="flex items-center justify-between pb-4 border-b border-parchment-border mb-4">
            <div className="flex items-center gap-2">
              <Scale size={18} className="text-status-indigo" />
              <h3 className="text-base font-bold font-serif text-ink-text">
                Statutory QCO Mandate
              </h3>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded text-ink-muted hover:text-ink-text"
            >
              <X size={16} />
            </button>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <span className="text-[10px] text-ink-muted uppercase block">STANDARD</span>
              <span className="text-sm font-bold text-ink-text font-serif">{standard.standard_number}</span>
              <span className="text-xs text-ink-muted font-sans block mt-0.5">{standard.title}</span>
            </div>

            <div>
              <span className="text-[10px] text-ink-muted uppercase block">STATUTORY ORDER</span>
              <span className="text-xs font-semibold text-status-indigo">{standard.qco_order_reference}</span>
            </div>

            <div>
              <span className="text-[10px] text-ink-muted uppercase block">ENFORCEMENT DATE</span>
              <span className="text-xs text-ink-text">{standard.enforcement_date || 'In Full Effect'}</span>
            </div>

            <div>
              <span className="text-[10px] text-ink-muted uppercase block">ISSUING MINISTRY</span>
              <span className="text-xs text-ink-text">{standard.ministry || 'Ministry of Commerce & Industry, DPIIT'}</span>
            </div>

            <div className="p-3.5 rounded-lg bg-status-indigoBg/40 border border-status-indigoBorder text-ink-text font-serif leading-relaxed text-xs">
              <strong className="block text-status-indigo font-sans text-xs mb-1">BIS Act 2016 Section 16 Mandate:</strong>
              No person shall manufacture, import, distribute, sell, hire, lease, store or exhibit for sale any goods that do not conform to the Indian Standard specified in the Quality Control Order and do not bear the Standard Mark (ISI Mark).
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold shadow-xs transition-colors mt-6"
        >
          Close Mandate Details
        </button>
      </div>
    </div>
  );
};
