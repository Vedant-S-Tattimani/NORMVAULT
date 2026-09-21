import React, { useState, useEffect } from 'react';
import { ProcurementDecisionPackage } from '../types/intelligence';
import { getDecisionPackage } from '../api/intelligence';
import { PackageHeader } from '../components/decision-package/PackageHeader';
import { ReviewActionsList } from '../components/decision-package/ReviewActionsList';
import { TraceabilityMatrix } from '../components/decision-package/TraceabilityMatrix';
import { JsonExportViewer } from '../components/decision-package/JsonExportViewer';
import { Toast } from '../components/common/Toast';

export const DecisionPackagePage: React.FC = () => {
  const [decisionPackage, setDecisionPackage] = useState<ProcurementDecisionPackage | null>(null);
  const [showJsonViewer, setShowJsonViewer] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      const data = await getDecisionPackage(1);
      setDecisionPackage(data);
    }
    load();
  }, []);

  if (!decisionPackage) {
    return (
      <div className="max-w-[1500px] mx-auto px-4 py-16 text-center text-xs font-mono text-ink-muted">
        Loading Procurement Decision Package...
      </div>
    );
  }

  return (
    <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Official Package Header */}
      <PackageHeader
        pkg={decisionPackage}
        onExportJson={() => setShowJsonViewer(!showJsonViewer)}
      />

      {/* Canonical JSON Viewer (Toggled by Export Canonical JSON) */}
      {showJsonViewer && (
        <JsonExportViewer data={decisionPackage.canonical_json_export} />
      )}

      {/* Pre-Tender Review Actions (Blocking & High Priority) */}
      <ReviewActionsList
        actions={decisionPackage.review_actions}
        onCopyAddendum={() => setToastMessage('Copied recommended tender addendum clause.')}
      />

      {/* End-to-End Traceability Matrix */}
      <TraceabilityMatrix matrix={decisionPackage.traceability_matrix} />

      {/* Toast Notification */}
      {toastMessage && (
        <Toast message={toastMessage} onClose={() => setToastMessage(null)} />
      )}
    </div>
  );
};
