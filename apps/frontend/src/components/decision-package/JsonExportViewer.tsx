import React, { useState } from 'react';
import { Copy, Check, Download } from 'lucide-react';

interface JsonExportViewerProps {
  data: Record<string, unknown>;
}

export const JsonExportViewer: React.FC<JsonExportViewerProps> = ({ data }) => {
  const [copied, setCopied] = useState(false);
  const jsonString = JSON.stringify(data, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `normvault_decision_package_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="parchment-card rounded-xl p-5 mb-8">
      <div className="flex items-center justify-between pb-3 border-b border-parchment-border mb-3">
        <div>
          <h3 className="text-sm font-bold font-serif text-ink-text">
            Canonical Decision Package JSON Export
          </h3>
          <p className="text-xs text-ink-muted">
            Signed and hash-verified structured data artifact for e-procurement portals (GeM / NIC).
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded border border-parchment-border text-ink-text hover:bg-parchment-subtle text-xs font-mono transition-colors"
          >
            {copied ? <Check size={12} className="text-status-sage" /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy JSON'}</span>
          </button>

          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-mono transition-colors shadow-xs"
          >
            <Download size={12} />
            <span>Download .json</span>
          </button>
        </div>
      </div>

      <pre className="p-4 rounded-lg bg-parchment-subtle border border-parchment-border text-ink-text font-mono text-xs overflow-x-auto max-h-80 leading-relaxed">
        {jsonString}
      </pre>
    </div>
  );
};
