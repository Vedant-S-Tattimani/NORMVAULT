import React from 'react';
import { Requirement } from '../../types/requirement';
import { X, Shield, Copy, Check } from 'lucide-react';
import { copyToClipboard } from '../../utils/clipboard';

interface EvidenceDrawerProps {
  requirement: Requirement | null;
  isOpen: boolean;
  onClose: () => void;
  onCopyHash?: (hash: string) => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  requirement,
  isOpen,
  onClose,
  onCopyHash,
}) => {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen || !requirement) return null;

  const handleCopy = async () => {
    if (requirement.cryptographic_offset) {
      await copyToClipboard(requirement.cryptographic_offset);
      if (onCopyHash) {
        onCopyHash(requirement.cryptographic_offset);
      }
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30 backdrop-blur-xs">
      <div className="w-full max-w-md bg-parchment-surface h-full border-l border-parchment-border shadow-parchment-lg p-6 flex flex-col justify-between overflow-y-auto">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-parchment-border mb-4">
            <div className="flex items-center gap-2">
              <Shield size={16} className="text-mineral-blue" />
              <h3 className="text-base font-bold font-serif text-ink-text">
                Evidence Provenance Inspector
              </h3>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded text-ink-muted hover:text-ink-text hover:bg-parchment-subtle"
            >
              <X size={16} />
            </button>
          </div>

          {/* Details */}
          <div className="space-y-4 text-xs font-mono">
            <div>
              <span className="text-[10px] text-ink-muted uppercase block">REQUIREMENT CODE</span>
              <span className="text-sm font-bold text-ink-text">{requirement.requirement_code}</span>
            </div>

            <div>
              <span className="text-[10px] text-ink-muted uppercase block">SECTION CITATION</span>
              <span className="text-xs text-ink-text">{requirement.section_citation}</span>
            </div>

            <div>
              <span className="text-[10px] text-ink-muted uppercase block">CRYPTOGRAPHIC SHA-256 OFFSET</span>
              <div className="flex items-center justify-between p-2 rounded bg-parchment-subtle border border-parchment-border mt-1">
                <span className="text-[11px] text-ink-text truncate mr-2">
                  {requirement.cryptographic_offset}
                </span>
                <button
                  onClick={handleCopy}
                  className="p-1 text-ink-muted hover:text-ink-text"
                  title="Copy SHA-256 Hash"
                >
                  {copied ? <Check size={12} className="text-status-sage" /> : <Copy size={12} />}
                </button>
              </div>
            </div>

            <div>
              <span className="text-[10px] text-ink-muted uppercase block mb-1">VERBATIM TENDER TEXT</span>
              <div className="p-3 rounded bg-parchment-subtle/60 border border-parchment-border font-serif italic text-ink-text leading-relaxed">
                "{requirement.verbatim_excerpt}"
              </div>
            </div>

            <div>
              <span className="text-[10px] text-ink-muted uppercase block mb-1">EXTRACTED TECHNICAL PARAMETERS</span>
              <div className="space-y-1.5">
                {requirement.parameters.map((p, idx) => (
                  <div key={idx} className="flex justify-between p-2 rounded bg-parchment-surface border border-parchment-border">
                    <span className="text-ink-muted">{p.name}:</span>
                    <span className="font-bold text-ink-text">{p.value} {p.unit || ''}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold shadow-xs transition-colors mt-6"
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
};
