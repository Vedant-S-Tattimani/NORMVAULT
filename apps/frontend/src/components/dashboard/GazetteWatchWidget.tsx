import { ShieldAlert, Calendar, BookOpen } from 'lucide-react';

export const GazetteWatchWidget: React.FC = () => {
  const qcos = [
    {
      id: 1,
      title: 'Electric Motors (Quality Control) Order, 2024',
      standard: 'IS 12615:2018 (Motors 0.75 kW to 375 kW)',
      so_number: 'S.O. 1284(E)',
      enforced_date: '01 Oct 2024',
      ministry: 'DPIIT, Ministry of Commerce and Industry',
      status: 'MANDATORY IN FORCE',
    },
    {
      id: 2,
      title: 'Distribution Transformers (Quality Control) Order',
      standard: 'IS 11171 / IS 2026 (BEE Star Rating & ISI Mark)',
      so_number: 'S.O. 2351(E)',
      enforced_date: '15 Jan 2025',
      ministry: 'Ministry of Heavy Industries',
      status: 'MANDATORY IN FORCE',
    },
    {
      id: 3,
      title: 'Structural Steel (Quality Control) Order, 2023',
      standard: 'IS 2062:2011 / IS 1786:2008 (TMT Steel Bars)',
      so_number: 'S.O. 3820(E)',
      enforced_date: '01 Jan 2024',
      ministry: 'Ministry of Steel',
      status: 'MANDATORY IN FORCE',
    },
  ];

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
              Standard: <strong className="text-ink-text">{qco.standard}</strong>
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
    </div>
  );
};
