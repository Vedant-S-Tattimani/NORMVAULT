import React, { useState } from 'react';
import {
  X,
  History,
  AlertTriangle,
  CheckCircle2,
  Copy,
  Check,
  FileText,
  Scale
} from 'lucide-react';
import { copyToClipboard } from '../../utils/clipboard';

interface TechnicalShiftItem {
  parameter: string;
  supersededValue: string;
  currentValue: string;
  auditImpact: string;
  severity: 'CRITICAL' | 'MAJOR' | 'MODERATE';
}

interface SupersessionRecord {
  id: string;
  currentStandard: string;
  currentYear: number;
  currentTitle: string;
  supersededStandard: string;
  supersededYear: number;
  supersededTitle: string;
  supersededStatus: 'WITHDRAWN' | 'SUPERSEDED';
  gazetteCitation: string;
  qcoReference: string;
  legalRiskStatement: string;
  technicalShifts: TechnicalShiftItem[];
  corrigendumDraft: string;
}

const SUPERSESSION_CATALOG: Record<string, SupersessionRecord> = {
  'IS 12615': {
    id: 'IS 12615',
    currentStandard: 'IS 12615:2018',
    currentYear: 2018,
    currentTitle: 'Line Operated Three-Phase A.C. Motors (IE Code) — Specification (Third Revision)',
    supersededStandard: 'IS 325:1996',
    supersededYear: 1996,
    supersededTitle: 'Three-Phase Induction Motors — Specification (Withdrawn by BIS)',
    supersededStatus: 'WITHDRAWN',
    gazetteCitation: 'BIS Gazette Notification ETD 15 / S.O. 1284(E) withdrawing IS 325 & mandating IS 12615',
    qcoReference: 'DPIIT Electric Motors (Quality Control) Order, 2024 (Statutory Compulsory Enforcement)',
    legalRiskStatement: 'GFR 2017 Rule 144(i) and CVC Guidelines strictly prohibit public tenders from specifying obsolete standards. Procuring under IS 325 constitutes procurement of non-QCO compliant equipment punishable under Section 29 of BIS Act 2016.',
    technicalShifts: [
      {
        parameter: 'Energy Efficiency Classification',
        supersededValue: 'No International Efficiency (IE) grading. Standard industrial efficiency thresholds allowed.',
        currentValue: 'Mandatory Minimum IE3 (Premium Efficiency) classification per Clause 6.1.',
        auditImpact: 'Supply of non-IE3 motors leads to rejection at factory acceptance and energy audit penalties.',
        severity: 'CRITICAL',
      },
      {
        parameter: 'Operating Voltage & Frequency',
        supersededValue: '400V / 415V Dual nominal reference tolerated without strict reconciliation.',
        currentValue: 'Strictly unified to 415 V ± 10%, 50 Hz, 3-Phase in accordance with national grid code.',
        auditImpact: 'Tenders citing 400V cause operational mismatch and contractor ambiguity.',
        severity: 'MAJOR',
      },
      {
        parameter: 'Test Method & Loss Verification',
        supersededValue: 'Legacy input-output brake test with conventional stray load loss estimate (0.5%).',
        currentValue: 'Strict adherence to IS 15999 (Part 2/Sec 1) summation of losses with accurate stray load measurement.',
        auditImpact: 'Legacy test certificates are invalid; independent NABL test reports required.',
        severity: 'CRITICAL',
      },
      {
        parameter: 'Statutory Certification Mark',
        supersededValue: 'Voluntary BIS Certification scheme permitted.',
        currentValue: 'Compulsory BIS ISI Certification Mark under Scheme-I with valid CM/L license.',
        auditImpact: 'Zero customs clearance or GeM invoice clearance without active BIS CM/L license.',
        severity: 'CRITICAL',
      },
      {
        parameter: 'Temperature Rise & Insulation',
        supersededValue: 'Class B temperature rise (80°C) with Class B insulation.',
        currentValue: 'Class B temperature rise (70°C / 80°C) strictly evaluated with Class F or H insulation reserve.',
        auditImpact: 'Premature winding breakdown under harsh thermal operating conditions.',
        severity: 'MODERATE',
      },
    ],
    corrigendumDraft: `"CORRIGENDUM ADDENDUM: All references in Tender Specification Section 4.2, Technical Schedule Tab 2, and Equipment Data Sheets citing 'IS 325' or 'IS 12615:2011' are hereby deleted and superseded with 'IS 12615:2018 (Clause 6.1 - IE3 Premium Efficiency)'. Efficiency and losses determination shall be verified strictly in accordance with IS 15999 (Part 2/Sec 1). Bidders must submit a valid BIS CM/L license under Scheme-I in accordance with DPIIT Quality Control Order 2024. All other terms remain unchanged."`,
  },
  'IS 1786': {
    id: 'IS 1786',
    currentStandard: 'IS 1786:2008',
    currentYear: 2008,
    currentTitle: 'High Strength Deformed Steel Bars and Wires for Concrete Reinforcement (Fourth Revision, Reaffirmed 2023)',
    supersededStandard: 'IS 1786:1985',
    supersededYear: 1985,
    supersededTitle: 'High Strength Deformed Steel Bars and Wires (Third Revision - Superseded)',
    supersededStatus: 'SUPERSEDED',
    gazetteCitation: 'Bureau of Indian Standards CED 54 Notification amending Rebar Tensile & Ductility standards',
    qcoReference: 'Ministry of Steel - Steel and Steel Products (Quality Control) Order, 2024',
    legalRiskStatement: 'Structural tenders citing 1985 specifications fail seismic safety norms outlined in IS 13920:2016 and National Building Code 2016 Part 6. Severe legal liability for procuring authority in event of structural failure.',
    technicalShifts: [
      {
        parameter: 'Ductility & Seismic Resistance Grades',
        supersededValue: 'Only standard grades Fe 415 and Fe 500 without enhanced ductility requirements.',
        currentValue: 'Introduction of mandatory "D" grades (Fe 415D, Fe 500D, Fe 550D) with minimum 16% elongation.',
        auditImpact: 'Structures in Seismic Zones III, IV, and V strictly require "D" grade rebar; standard grades non-compliant.',
        severity: 'CRITICAL',
      },
      {
        parameter: 'Ultimate Tensile / Yield Stress Ratio (UTS/YS)',
        supersededValue: 'UTS/YS ratio was not controlled strictly for earthquake energy dissipation.',
        currentValue: 'Mandatory UTS/YS ratio ≥ 1.25 for Fe 415D and ≥ 1.10 for Fe 500D to ensure plastic hinge formation.',
        auditImpact: 'Bars fail ductile detailing inspections during structural audits.',
        severity: 'CRITICAL',
      },
      {
        parameter: 'Maximum Chemical Composition Limits',
        supersededValue: 'Permitted higher Carbon (0.30%), Sulphur (0.060%), and Phosphorus (0.060%).',
        currentValue: 'Strictly reduced to C ≤ 0.25%, S ≤ 0.040%, P ≤ 0.040%, and combined S+P ≤ 0.075%.',
        auditImpact: 'Poor weldability and brittle fractures during on-site fabrication.',
        severity: 'MAJOR',
      },
      {
        parameter: 'Bend and Rebend Test Mandates',
        supersededValue: 'Mandrel diameter 4d for standard bend test.',
        currentValue: 'Mandrel diameter strictly revised with mandatory rebend test after aging at 100°C for 30 minutes.',
        auditImpact: 'Rebar fails QA site bend testing when bent at site corners.',
        severity: 'MAJOR',
      },
    ],
    corrigendumDraft: `"CORRIGENDUM ADDENDUM: In Section 2.1 (Civil Works - Reinforcement Steel), the specification 'TMT Bars conforming to IS 1786:1985 Fe 415' is hereby amended to read: 'Thermo-Mechanically Treated (TMT) High Strength Deformed Steel Bars conforming to IS 1786:2008 Grade Fe 500D with minimum elongation of 16.0% and UTS/YS ratio not less than 1.10'. Material must bear mandatory BIS Standard Mark (ISI) with mill test certificates in compliance with the Ministry of Steel QCO 2024."`,
  },
  'IS 732': {
    id: 'IS 732',
    currentStandard: 'IS 732:2019',
    currentYear: 2019,
    currentTitle: 'Code of Practice for Electrical Wiring Installations (Fourth Revision)',
    supersededStandard: 'IS 732:1989',
    supersededYear: 1989,
    supersededTitle: 'Code of Practice for Electrical Wiring Installations (Third Revision - Superseded)',
    supersededStatus: 'SUPERSEDED',
    gazetteCitation: 'BIS ETD 20 Harmonization with IEC 60364 International Wiring Regulations',
    qcoReference: 'Central Electricity Authority (Measures relating to Safety and Electric Supply) Regulations',
    legalRiskStatement: 'Citing the 1989 edition omits mandatory residual current device (RCD) shock protection and surge protection devices (SPDs), creating severe electrical fire and electrocution liability.',
    technicalShifts: [
      {
        parameter: 'Shock Protection via RCD / ELCB',
        supersededValue: 'Earth leakage circuit breakers recommended only for specific hazardous locations.',
        currentValue: 'Mandatory Residual Current Devices (RCDs) with rated residual operating current ≤ 30 mA for all socket outlets up to 32 A.',
        auditImpact: 'Central Electricity Authority electrical inspectorate safety clearance will be refused.',
        severity: 'CRITICAL',
      },
      {
        parameter: 'Earthing System Architecture',
        supersededValue: 'Conventional pipe/plate earthing described with generic neutral earthing rules.',
        currentValue: 'Harmonized TN-S, TN-C-S, and TT system earthing schemes with calculated touch voltage limits.',
        auditImpact: 'Severe ground fault loop impedance violations during electrical safety commissioning.',
        severity: 'MAJOR',
      },
      {
        parameter: 'Surge Protection Devices (SPD)',
        supersededValue: 'No mandatory surge protection stipulated for building service entrances.',
        currentValue: 'Mandatory Type 1 / Type 2 Surge Protection Devices at main distribution boards per Clause 443.',
        auditImpact: 'Equipment damage to sensitive electronic devices during lightning and grid switching surges.',
        severity: 'MAJOR',
      },
    ],
    corrigendumDraft: `"CORRIGENDUM ADDENDUM: Electrical Installation Specification Clause 8.3 is amended to mandate compliance with IS 732:2019 (Fourth Revision). All final sub-circuits feeding convenience socket outlets shall be provided with 30 mA Residual Current Circuit Breakers (RCCBs) in accordance with CEA Safety Regulations. Type 2 Surge Protection Devices (SPDs) shall be installed at the Main LT Panel."`,
  },
};

interface SupersessionDiffModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultStandardNumber?: string;
}

export const SupersessionDiffModal: React.FC<SupersessionDiffModalProps> = ({
  isOpen,
  onClose,
  defaultStandardNumber = 'IS 12615',
}) => {
  // Normalize default standard key
  const defaultKey = Object.keys(SUPERSESSION_CATALOG).find((k) =>
    defaultStandardNumber.toUpperCase().includes(k)
  ) || 'IS 12615';

  const [selectedKey, setSelectedKey] = useState<string>(defaultKey);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const record = SUPERSESSION_CATALOG[selectedKey] || SUPERSESSION_CATALOG['IS 12615'];

  const handleCopyCorrigendum = async () => {
    await copyToClipboard(record.corrigendumDraft);
    setCopied(true);
    setTimeout(() => setCopied(false), 2200);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-ink-dark/70 backdrop-blur-xs overflow-y-auto animate-fadeIn">
      <div className="bg-parchment-base border border-parchment-border rounded-2xl shadow-2xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden text-ink-text my-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-parchment-border bg-parchment-surface/90 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-mineral-light text-mineral-dark">
              <History size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base sm:text-lg font-bold font-serif text-ink-text">
                  Standards Supersession & Revision Diff Engine
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-bold uppercase">
                  BIS AUDIT RECONCILIATION
                </span>
              </div>
              <p className="text-xs text-ink-muted">
                Side-by-side technical shift analysis between prevailing mandated standards and obsolete predecessors.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-ink-muted hover:text-ink-text hover:bg-parchment-subtle transition-colors cursor-pointer"
            title="Close modal"
          >
            <X size={20} />
          </button>
        </div>

        {/* Standard Selector Tabs */}
        <div className="px-6 py-2.5 bg-parchment-subtle border-b border-parchment-border flex items-center gap-2 overflow-x-auto shrink-0">
          <span className="text-xs font-mono text-ink-muted mr-1 shrink-0 font-semibold">
            Select Comparison Case:
          </span>
          {Object.entries(SUPERSESSION_CATALOG).map(([key, item]) => (
            <button
              key={key}
              onClick={() => setSelectedKey(key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all shrink-0 cursor-pointer ${
                selectedKey === key
                  ? 'bg-ink-text text-parchment-surface font-semibold shadow-xs'
                  : 'bg-parchment-surface text-ink-muted hover:text-ink-text border border-parchment-border'
              }`}
            >
              {item.currentStandard} vs {item.supersededStandard}
            </button>
          ))}
        </div>

        {/* Scrollable Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
          {/* Side-by-Side Standard Comparison Header Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Superseded Standard Card */}
            <div className="p-4 rounded-xl bg-status-crimsonBg/30 border border-status-crimsonBorder/80">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono font-bold uppercase text-status-crimson px-2 py-0.5 rounded bg-status-crimsonBg border border-status-crimsonBorder">
                  OBSOLETE / {record.supersededStatus}
                </span>
                <span className="text-[10px] font-mono text-status-crimson font-semibold">
                  DO NOT SPECIFY
                </span>
              </div>
              <h3 className="text-base font-bold font-serif text-ink-text">
                {record.supersededStandard}
              </h3>
              <p className="text-xs text-ink-muted mt-1 leading-relaxed font-serif">
                {record.supersededTitle}
              </p>
              <div className="mt-3 pt-2.5 border-t border-status-crimsonBorder/50 text-[11px] font-mono text-status-crimson">
                Withdrawal Status: Officially superseded by Bureau of Indian Standards. Citing in tender creates GFR 144(i) irregularity.
              </div>
            </div>

            {/* Mandated Current Standard Card */}
            <div className="p-4 rounded-xl bg-status-sageBg/30 border border-status-sageBorder/80">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono font-bold uppercase text-status-sage px-2 py-0.5 rounded bg-status-sageBg border border-status-sageBorder">
                  CURRENT / MANDATED IN FORCE
                </span>
                <span className="text-[10px] font-mono text-status-sage font-semibold">
                  STATUTORY REQUISITE
                </span>
              </div>
              <h3 className="text-base font-bold font-serif text-ink-text">
                {record.currentStandard}
              </h3>
              <p className="text-xs text-ink-muted mt-1 leading-relaxed font-serif">
                {record.currentTitle}
              </p>
              <div className="mt-3 pt-2.5 border-t border-status-sageBorder/50 text-[11px] font-mono text-status-sage">
                Enforcement: {record.qcoReference}
              </div>
            </div>
          </div>

          {/* Legal Audit & Statutory Risk Statement */}
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start gap-3">
            <AlertTriangle size={18} className="text-amber-700 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-amber-900 block font-serif text-xs">
                Statutory Compliance & Legal Tender Risk Notice
              </span>
              <p className="text-xs text-amber-900/90 mt-1 leading-relaxed font-serif">
                {record.legalRiskStatement}
              </p>
              <div className="mt-2 text-[10px] font-mono text-amber-800 font-semibold">
                Gazette Authority: {record.gazetteCitation}
              </div>
            </div>
          </div>

          {/* Technical Shifts Table */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-bold font-serif text-ink-text">
                Parameter-by-Parameter Technical Shift & Audit Impact
              </h4>
              <span className="text-[10px] font-mono text-ink-muted">
                {record.technicalShifts.length} Core Discrepancies Reconciled
              </span>
            </div>

            <div className="overflow-hidden border border-parchment-border rounded-xl shadow-xs">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-parchment-subtle border-b border-parchment-border text-[10px] font-mono uppercase text-ink-muted">
                    <th className="py-2.5 px-3 font-semibold w-1/4">Technical Parameter</th>
                    <th className="py-2.5 px-3 font-semibold w-1/4 text-status-crimson">
                      Superseded ({record.supersededStandard})
                    </th>
                    <th className="py-2.5 px-3 font-semibold w-1/4 text-status-sage">
                      Current ({record.currentStandard})
                    </th>
                    <th className="py-2.5 px-3 font-semibold w-1/4">Audit & Legal Consequence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-parchment-border bg-parchment-surface">
                  {record.technicalShifts.map((shift, idx) => (
                    <tr key={idx} className="hover:bg-parchment-subtle/40 transition-colors">
                      <td className="py-3 px-3 font-semibold font-serif text-ink-text align-top">
                        <div className="flex items-center gap-1.5">
                          <span>{shift.parameter}</span>
                          {shift.severity === 'CRITICAL' && (
                            <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-rose-100 text-rose-800 font-bold">
                              CRITICAL
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-3 font-mono text-status-crimson bg-status-crimsonBg/10 align-top line-through leading-relaxed">
                        {shift.supersededValue}
                      </td>
                      <td className="py-3 px-3 font-mono text-status-sage bg-status-sageBg/10 align-top font-semibold leading-relaxed">
                        {shift.currentValue}
                      </td>
                      <td className="py-3 px-3 text-ink-muted font-sans align-top leading-relaxed text-[11px]">
                        {shift.auditImpact}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pre-Drafted Corrigendum Template */}
          <div className="p-4 rounded-xl bg-parchment-subtle border border-parchment-border space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText size={15} className="text-mineral-blue" />
                <span className="font-mono text-xs uppercase font-bold text-ink-text">
                  Statutory Pre-Tender Corrigendum Addendum Template
                </span>
              </div>
              <button
                onClick={handleCopyCorrigendum}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-mono font-medium transition-colors shadow-xs cursor-pointer"
              >
                {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                <span>{copied ? 'Corrigendum Copied!' : 'Copy Addendum Text'}</span>
              </button>
            </div>

            <p className="text-xs font-serif italic text-ink-text bg-parchment-surface p-3.5 rounded-lg border border-parchment-border/80 leading-relaxed">
              {record.corrigendumDraft}
            </p>

            <div className="flex items-center justify-between text-[11px] font-mono text-ink-muted">
              <span>Ready for insertion into Government e-Marketplace (GeM) Corrigendum Portal or CPP Portal.</span>
              <span className="text-status-sage font-semibold flex items-center gap-1">
                <CheckCircle2 size={12} />
                <span>Verified against CVC & GFR 2017</span>
              </span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-parchment-surface border-t border-parchment-border flex items-center justify-between shrink-0 text-xs">
          <div className="flex items-center gap-2 text-ink-muted font-mono text-[11px]">
            <Scale size={13} className="text-mineral-blue" />
            <span>Bureau of Indian Standards Act 2016 • Section 16 & Section 29 Statutory Verification</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded text-xs font-mono border border-parchment-border bg-parchment-surface hover:bg-parchment-subtle text-ink-text cursor-pointer transition-colors"
            >
              Close
            </button>
            <button
              onClick={handleCopyCorrigendum}
              className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded text-xs font-mono bg-mineral-blue hover:bg-mineral-dark text-white font-semibold shadow-xs cursor-pointer transition-colors"
            >
              <Copy size={12} />
              <span>{copied ? 'Copied' : 'Copy Rectification Clause'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
