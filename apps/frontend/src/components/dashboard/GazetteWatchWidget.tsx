import React, { useState, useEffect } from 'react';
import { ShieldAlert, Calendar, BookOpen, Loader2 } from 'lucide-react';
import { getGazetteFeed, GazetteFeedItem } from '../../api/standards';

export const GazetteWatchWidget: React.FC = () => {
  const [qcos, setQcos] = useState<GazetteFeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const feed = await getGazetteFeed();
        setQcos(feed);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="parchment-card rounded-xl p-5 mb-8">
      <div className="flex items-center justify-between pb-3 border-b border-parchment-border mb-4">
        <div className="flex items-center gap-2">
          <ShieldAlert size={16} className="text-status-indigo" />
          <h3 className="text-sm font-bold font-serif text-ink-text">
            Gazette & QCO Statutory Watch
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-status-indigoBg text-status-indigo border border-status-indigoBorder font-semibold">
          DPIIT STATUTORY FEED
        </span>
      </div>

      <p className="text-xs text-ink-muted mb-4 font-serif">
        Live tracking of Ministry Quality Control Orders (QCO) issued under BIS Act 2016 Section 16. Procurement of non-certified items constitutes a statutory violation.
      </p>

      {loading ? (
        <div className="flex items-center justify-center gap-2 py-8 text-xs font-mono text-ink-muted">
          <Loader2 size={15} className="animate-spin text-mineral-blue" />
          <span>Synchronizing Gazette statutory feed...</span>
        </div>
      ) : (
        <div className="space-y-3">
          {qcos.map((qco) => (
          <div
            key={qco.id}
            className="p-3.5 rounded-lg bg-parchment-surface border border-parchment-border hover:border-mineral-blue/50 transition-colors"
          >
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <h4 className="text-xs font-bold font-serif text-ink-text">
                {qco.title}
              </h4>
              <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-status-indigoBg text-status-indigo border border-status-indigoBorder shrink-0">
                {qco.status}
              </span>
            </div>

            <div className="text-[11px] text-ink-muted mb-2 font-mono">
              Standard: <strong className="text-ink-text">{qco.standard_number}</strong>
            </div>

            <div className="flex items-center justify-between text-[10px] font-mono text-ink-muted pt-2 border-t border-parchment-border/60">
              <span className="flex items-center gap-1">
                <BookOpen size={10} />
                {qco.so_number}
              </span>
              <span className="flex items-center gap-1">
                <Calendar size={10} />
                Enforced: {qco.enforced_date}
              </span>
            </div>
          </div>
        ))}
        </div>
      )}
    </div>
  );
};
