import React, { useState, useEffect, useMemo } from 'react';
import { IndianStandard, StandardsDependencyGraph, CurrentnessEvaluation } from '../types/standard';
import { searchStandards, getStandardDependencies, getCurrentness } from '../api/standards';
import { StandardHeaderCard } from '../components/standards/StandardHeaderCard';
import { DependencyGraph } from '../components/standards/DependencyGraph';
import { EditionTimeline } from '../components/standards/EditionTimeline';
import { QcoMandateDrawer } from '../components/standards/QcoMandateDrawer';
import { SupersessionDiffModal } from '../components/standards/SupersessionDiffModal';
import { StatusBadge } from '../components/common/StatusBadge';
import { Toast } from '../components/common/Toast';
import { ViewType } from '../components/common/EditorialHeader';
import {
  Search,
  Scale,
  GitFork,
  History,
  X,
  Filter,
  ArrowUpDown,
  BookOpen,
  Loader2,
  ArrowLeft
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface StandardsPageProps {
  initialQuery?: string;
  onNavigate?: (view: ViewType, query?: string) => void;
}

type DivisionFilter = 'ALL' | 'ETD' | 'CED' | 'MED' | 'MTD' | 'ITD' | 'FAD' | 'TXD';

export const StandardsPage: React.FC<StandardsPageProps> = ({
  initialQuery,
  onNavigate,
}) => {
  const { t } = useTranslation();
  const [standards, setStandards] = useState<IndianStandard[]>([]);
  const [selectedStandard, setSelectedStandard] = useState<IndianStandard | null>(null);
  const [graph, setGraph] = useState<StandardsDependencyGraph | null>(null);
  const [currentness, setCurrentness] = useState<CurrentnessEvaluation | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [divisionFilter, setDivisionFilter] = useState<DivisionFilter>('ALL');
  const [qcoOnly, setQcoOnly] = useState(false);
  const [sortBy, setSortBy] = useState<'number' | 'year' | 'qco'>('number');
  const [activeTab, setActiveTab] = useState<'dependencies' | 'timeline' | 'qco'>('dependencies');
  const [qcoDrawerStandard, setQcoDrawerStandard] = useState<IndianStandard | null>(null);
  const [showSupersessionModal, setShowSupersessionModal] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [mobileViewTab, setMobileViewTab] = useState<'catalog' | 'details'>('catalog');

  // Load standards list
  useEffect(() => {
    let isMounted = true;
    async function load() {
      setIsLoading(true);
      let queryToUse = '';
      let targetDivision: DivisionFilter = 'ALL';

      if (initialQuery) {
        const clean = initialQuery.trim();
        const upper = clean.toUpperCase();

        const categoryAliases: Record<string, DivisionFilter> = {
          'ETD': 'ETD',
          'ELECTROTECHNICAL': 'ETD',
          'ELECTRICAL': 'ETD',
          'CED': 'CED',
          'CIVIL': 'CED',
          'STRUCTURAL': 'CED',
          'MED': 'MED',
          'MECHANICAL': 'MED',
          'MTD': 'MTD',
          'METALLURGICAL': 'MTD',
          'METALLURGY': 'MTD',
          'ITD': 'ITD',
          'INFORMATION TECH': 'ITD',
          'IT': 'ITD',
          'FAD': 'FAD',
          'FOOD': 'FAD',
          'AGRICULTURE': 'FAD',
          'TXD': 'TXD',
          'TEXTILE': 'TXD',
          'TEXTILES': 'TXD',
        };

        if (categoryAliases[upper]) {
          targetDivision = categoryAliases[upper];
          setDivisionFilter(targetDivision);
          setSearchQuery(''); // keep search input empty so user sees all standards in division
          queryToUse = '';
        } else {
          setDivisionFilter('ALL');
          setSearchQuery(clean);
          queryToUse = clean;
        }
      } else {
        setDivisionFilter('ALL');
        setSearchQuery('');
      }

      const data = await searchStandards(queryToUse);
      if (!isMounted) return;

      setStandards(data);

      // Select first standard matching the active division filter
      const matching = targetDivision !== 'ALL'
        ? data.filter((s) => s.division_code?.toUpperCase() === targetDivision)
        : data;

      const first = matching[0] || data[0];
      if (first) {
        setSelectedStandard(first);
        const [g, c] = await Promise.all([
          getStandardDependencies(first.id, first),
          getCurrentness(first.id, first),
        ]);
        if (isMounted) {
          setGraph(g);
          setCurrentness(c);
        }
      } else {
        setSelectedStandard(null);
        setGraph(null);
        setCurrentness(null);
      }
      setIsLoading(false);
    }
    load();
    return () => {
      isMounted = false;
    };
  }, [initialQuery]);

  // Handle Division Filter Click
  const handleDivisionChange = async (div: DivisionFilter) => {
    setDivisionFilter(div);
    let currentList = standards;
    const hasMatches = div === 'ALL' ? currentList.length > 0 : currentList.some((s) => s.division_code?.toUpperCase() === div);
    if (!hasMatches && !searchQuery.trim()) {
      setIsLoading(true);
      const all = await searchStandards('');
      setStandards(all);
      currentList = all;
      setIsLoading(false);
    }
    const matching = div === 'ALL'
      ? currentList
      : currentList.filter((s) => s.division_code?.toUpperCase() === div);
    if (matching.length > 0) {
      handleSelectStandard(matching[0]);
    }
  };

  // Handle Search Input Submission
  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    const results = await searchStandards(searchQuery, divisionFilter !== 'ALL' ? divisionFilter : undefined);
    setStandards(results);
    if (results.length > 0) {
      handleSelectStandard(results[0]);
    } else {
      setSelectedStandard(null);
      setGraph(null);
      setCurrentness(null);
    }
    setIsLoading(false);
  };

  // Live Search Clear
  const handleClearSearch = async () => {
    setSearchQuery('');
    setDivisionFilter('ALL');
    setQcoOnly(false);
    setIsLoading(true);
    const results = await searchStandards('');
    setStandards(results);
    if (results.length > 0) {
      handleSelectStandard(results[0]);
    }
    setIsLoading(false);
  };

  // Select a standard to view its details, graph, and timeline
  const handleSelectStandard = async (std: IndianStandard) => {
    setSelectedStandard(std);
    const [g, c] = await Promise.all([
      getStandardDependencies(std.id, std),
      getCurrentness(std.id, std),
    ]);
    setGraph(g);
    setCurrentness(c);
    // On mobile screens, automatically show the details view
    if (window.innerWidth < 1024) {
      setMobileViewTab('details');
    }
  };

  // Switch to a standard by standard number (e.g. from dependency graph)
  const handleNavigateToStandardNumber = async (stdNumber: string) => {
    // Check if it exists in current loaded list
    const found = standards.find(
      (s) => s.standard_number.toLowerCase().includes(stdNumber.toLowerCase()) ||
             stdNumber.toLowerCase().includes(s.standard_number.toLowerCase())
    );

    if (found) {
      handleSelectStandard(found);
      setToastMessage(`Switched to standard: ${found.standard_number}`);
    } else {
      // Search for it
      setSearchQuery(stdNumber);
      const results = await searchStandards(stdNumber);
      setStandards(results);
      if (results.length > 0) {
        handleSelectStandard(results[0]);
        setToastMessage(`Loaded standard: ${results[0].standard_number}`);
      } else {
        setToastMessage(`Standard ${stdNumber} is referenced normatively but not yet fully indexed in primary catalog.`);
      }
    }
  };

  // Navigate to Workspace to analyze tender against this standard
  const handleNavigateToAnalyze = (stdNumber: string) => {
    if (onNavigate) {
      onNavigate('analyze', stdNumber);
    }
  };

  // Filter & Sort Standards List
  const filteredAndSortedStandards = useMemo(() => {
    let result = [...standards];

    // Filter by QCO
    if (qcoOnly) {
      result = result.filter((s) => s.is_qco_mandatory);
    }

    // Filter by Division
    if (divisionFilter !== 'ALL') {
      result = result.filter((s) => s.division_code?.toUpperCase() === divisionFilter);
    }

    // Sort
    result.sort((a, b) => {
      if (sortBy === 'qco') {
        if (a.is_qco_mandatory && !b.is_qco_mandatory) return -1;
        if (!a.is_qco_mandatory && b.is_qco_mandatory) return 1;
        return a.standard_number.localeCompare(b.standard_number);
      }
      if (sortBy === 'year') {
        return (b.year || 0) - (a.year || 0);
      }
      return a.standard_number.localeCompare(b.standard_number);
    });

    return result;
  }, [standards, qcoOnly, divisionFilter, sortBy]);

  return (
    <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Banner */}
      <div className="parchment-card rounded-xl p-6 mb-6 shadow-xs border border-parchment-border">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-mono uppercase text-ink-muted mb-1">
              <span className="px-2 py-0.5 rounded bg-mineral-light text-mineral-dark font-semibold border border-mineral-blue/30">
                BIS AUTHORITATIVE KNOWLEDGE GRAPH
              </span>
              <span className="hidden sm:inline-block text-ink-faint">•</span>
              <span className="hidden sm:inline-block font-mono text-mineral-blue">
                22,418 Authoritative BIS Standards Mapped
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold font-serif text-ink-text tracking-tight">
              {t('standards_heading', 'Indian Standards Catalog & Dependency Intelligence')}
            </h1>
            <p className="text-xs sm:text-sm text-ink-muted mt-1 font-serif">
              {t('standards_subheading', 'Comprehensive Bureau of Indian Standards (BIS) knowledge repository tracking editions, normative dependencies, and statutory Quality Control Orders (QCOs).')}
            </p>
          </div>

          {/* QCO Quick Filter Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setQcoOnly(!qcoOnly)}
              className={`inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-mono transition-all border ${
                qcoOnly
                  ? 'bg-status-indigo text-white border-status-indigo font-bold shadow-xs'
                  : 'bg-parchment-surface text-ink-muted border-parchment-border hover:bg-parchment-subtle'
              }`}
            >
              <Scale size={13} />
              <span>{qcoOnly ? t('standards_showing_qco', 'Showing Mandatory QCOs') : t('standards_filter_qco', 'Filter QCO Mandates')}</span>
            </button>
          </div>
        </div>

        {/* Division Filter Chips */}
        <div className="flex items-center gap-2 mt-4 pt-4 border-t border-parchment-border overflow-x-auto pb-1 text-xs font-mono">
          <span className="text-[10px] uppercase text-ink-muted font-semibold flex items-center gap-1 shrink-0">
            <Filter size={11} />
            <span>{t('standards_divisions_label', 'Divisions:')}</span>
          </span>

          <button
            onClick={() => handleDivisionChange('ALL')}
            className={`px-3 py-1.5 rounded-lg transition-all shrink-0 cursor-pointer ${
              divisionFilter === 'ALL'
                ? 'bg-ink-text text-parchment-surface font-semibold shadow-2xs'
                : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle border border-parchment-border'
            }`}
          >
            {t('standards_all', 'All Standards')} ({standards.length})
          </button>

          <button
            onClick={() => handleDivisionChange('ETD')}
            className={`px-3 py-1.5 rounded-lg transition-all shrink-0 cursor-pointer ${
              divisionFilter === 'ETD'
                ? 'bg-mineral-blue text-white font-semibold shadow-2xs'
                : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle border border-parchment-border'
            }`}
          >
            {t('cat_etd', '⚡ Electrotechnical (ETD)')} ({standards.filter((s) => s.division_code?.toUpperCase() === 'ETD').length})
          </button>

          <button
            onClick={() => handleDivisionChange('CED')}
            className={`px-3 py-1.5 rounded-lg transition-all shrink-0 cursor-pointer ${
              divisionFilter === 'CED'
                ? 'bg-mineral-blue text-white font-semibold shadow-2xs'
                : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle border border-parchment-border'
            }`}
          >
            {t('cat_ced', '🏛️ Civil & Structural (CED)')} ({standards.filter((s) => s.division_code?.toUpperCase() === 'CED').length})
          </button>

          <button
            onClick={() => handleDivisionChange('MED')}
            className={`px-3 py-1.5 rounded-lg transition-all shrink-0 cursor-pointer ${
              divisionFilter === 'MED'
                ? 'bg-mineral-blue text-white font-semibold shadow-2xs'
                : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle border border-parchment-border'
            }`}
          >
            {t('cat_med', '⚙️ Mechanical (MED)')} ({standards.filter((s) => s.division_code?.toUpperCase() === 'MED').length})
          </button>

          <button
            onClick={() => handleDivisionChange('MTD')}
            className={`px-3 py-1.5 rounded-lg transition-all shrink-0 cursor-pointer ${
              divisionFilter === 'MTD'
                ? 'bg-mineral-blue text-white font-semibold shadow-2xs'
                : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle border border-parchment-border'
            }`}
          >
            {t('cat_mtd', '🔬 Metallurgical (MTD)')} ({standards.filter((s) => s.division_code?.toUpperCase() === 'MTD').length})
          </button>

          <button
            onClick={() => handleDivisionChange('ITD')}
            className={`px-3 py-1.5 rounded-lg transition-all shrink-0 cursor-pointer ${
              divisionFilter === 'ITD'
                ? 'bg-mineral-blue text-white font-semibold shadow-2xs'
                : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle border border-parchment-border'
            }`}
          >
            {t('cat_itd', '💻 Information Tech (ITD)')} ({standards.filter((s) => s.division_code?.toUpperCase() === 'ITD').length})
          </button>

          <button
            onClick={() => handleDivisionChange('FAD')}
            className={`px-3 py-1.5 rounded-lg transition-all shrink-0 cursor-pointer ${
              divisionFilter === 'FAD'
                ? 'bg-mineral-blue text-white font-semibold shadow-2xs'
                : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle border border-parchment-border'
            }`}
          >
            {t('cat_fad', '🌾 Food & Agriculture (FAD)')} ({standards.filter((s) => s.division_code?.toUpperCase() === 'FAD').length})
          </button>

          <button
            onClick={() => handleDivisionChange('TXD')}
            className={`px-3 py-1.5 rounded-lg transition-all shrink-0 cursor-pointer ${
              divisionFilter === 'TXD'
                ? 'bg-mineral-blue text-white font-semibold shadow-2xs'
                : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle border border-parchment-border'
            }`}
          >
            {t('cat_txd', '🧵 Textiles & Fabrics (TXD)')} ({standards.filter((s) => s.division_code?.toUpperCase() === 'TXD').length})
          </button>
        </div>
      </div>

      {/* Mobile Catalog vs Details Segment Switcher (Hidden on Desktop) */}
      <div className="lg:hidden flex items-center bg-[#EAE4D8] p-1 rounded-xl mb-4 border border-[#8C8275]/25 text-xs font-mono">
        <button
          onClick={() => setMobileViewTab('catalog')}
          className={`flex-1 py-2 px-3 text-center rounded-lg font-medium transition-all cursor-pointer ${
            mobileViewTab === 'catalog'
              ? 'bg-[#1E2320] text-[#FCFAF6] shadow-xs font-semibold'
              : 'text-[#525650] hover:text-[#1E2320]'
          }`}
        >
          {t('standards_catalog_tab', '📋 Catalog')} ({filteredAndSortedStandards.length})
        </button>
        <button
          onClick={() => setMobileViewTab('details')}
          className={`flex-1 py-2 px-3 text-center rounded-lg font-medium transition-all cursor-pointer ${
            mobileViewTab === 'details'
              ? 'bg-[#1E2320] text-[#FCFAF6] shadow-xs font-semibold'
              : 'text-[#525650] hover:text-[#1E2320]'
          }`}
        >
          🔍 {selectedStandard ? selectedStandard.standard_number : 'Details & Graph'}
        </button>
      </div>

      {/* Main Catalog Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Sidebar: Search & List */}
        <div className={`lg:col-span-4 space-y-4 ${mobileViewTab === 'details' ? 'hidden lg:block' : 'block'}`}>
          <div className="parchment-card rounded-xl p-4 border border-parchment-border shadow-xs">
            {/* Search Box */}
            <form onSubmit={handleSearchSubmit} className="flex gap-2 mb-3">
              <div className="relative flex-1">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('standards_search_placeholder', 'Search IS 12615, motor, rebar...')}
                  className="w-full pl-8 pr-7 py-2 text-xs bg-parchment-surface border border-parchment-border rounded-lg text-ink-text font-mono focus:outline-none focus:border-mineral-blue"
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={handleClearSearch}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-ink-faint hover:text-ink-text p-0.5"
                  >
                    <X size={13} />
                  </button>
                )}
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="px-3.5 py-2 rounded-lg bg-ink-text text-parchment-surface text-xs font-semibold hover:bg-ink-dark transition-colors shrink-0 disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
              >
                {isLoading && <Loader2 size={12} className="animate-spin text-parchment-surface" />}
                <span>{isLoading ? '...' : t('hero_search_btn', 'Search')}</span>
              </button>
            </form>

            {/* List Header & Sorting */}
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-parchment-border text-[11px] font-mono text-ink-muted">
              <span>
                {filteredAndSortedStandards.length} {filteredAndSortedStandards.length === 1 ? 'Standard' : 'Standards'}
              </span>

              <div className="flex items-center gap-1.5">
                <ArrowUpDown size={11} className="text-ink-faint" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="bg-transparent text-[10px] font-mono text-ink-muted focus:outline-none cursor-pointer"
                >
                  <option value="number">{t('standards_sort_code', 'Code (A-Z)')}</option>
                  <option value="year">{t('standards_sort_year', 'Latest Year')}</option>
                  <option value="qco">{t('standards_sort_qco', 'QCO Mandated First')}</option>
                </select>
              </div>
            </div>

            {/* Standards Scrollable List */}
            <div className="space-y-2 max-h-[620px] overflow-y-auto pr-1">
              {filteredAndSortedStandards.length > 0 ? (
                filteredAndSortedStandards.map((std) => {
                  const isSelected = selectedStandard?.id === std.id;
                  return (
                    <div
                      key={std.id}
                      onClick={() => handleSelectStandard(std)}
                      className={`p-3 rounded-lg border text-left cursor-pointer transition-all ${
                        isSelected
                          ? 'border-mineral-blue bg-parchment-subtle shadow-xs ring-1 ring-mineral-blue/50'
                          : 'border-parchment-border bg-parchment-surface hover:bg-parchment-subtle/60'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-1.5">
                          <span className="font-bold font-serif text-ink-text text-xs">
                            {std.standard_number}
                          </span>
                          {std.year && (
                            <span className="text-[10px] font-mono text-ink-muted">
                              :{std.year}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-1">
                          {std.division_code && (
                            <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-parchment-subtle border border-parchment-border text-ink-muted uppercase">
                              {std.division_code}
                            </span>
                          )}
                          <StatusBadge status={std.status} size="sm" />
                        </div>
                      </div>

                      <div className="text-[11px] text-ink-text font-sans line-clamp-2 leading-relaxed">
                        {std.title}
                      </div>

                      {std.is_qco_mandatory && (
                        <div className="mt-2 text-[10px] font-mono text-status-indigo flex items-center gap-1 font-semibold">
                          <Scale size={11} />
                          <span>{t('standards_status_qco', 'DPIIT Statutory QCO Mandate')}</span>
                        </div>
                      )}
                    </div>
                  );
                })
              ) : (
                /* Empty Search State */
                <div className="p-8 text-center bg-parchment-surface rounded-lg border border-dashed border-parchment-border my-4">
                  <Search size={24} className="mx-auto text-ink-faint mb-2" />
                  <p className="font-serif font-bold text-ink-text text-xs">
                    No Matching Standards Found
                  </p>
                  <p className="text-[11px] text-ink-muted font-sans mt-1">
                    No Indian Standards match "{searchQuery}" with the current filters.
                  </p>
                  <button
                    onClick={handleClearSearch}
                    className="mt-3 px-3 py-1.5 rounded text-xs font-mono bg-parchment-subtle hover:bg-parchment-border border border-parchment-border text-ink-text transition-colors cursor-pointer"
                  >
                    Reset Search & Filters
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Detail Panel */}
        <div className={`lg:col-span-8 space-y-6 ${mobileViewTab === 'catalog' ? 'hidden lg:block' : 'block'}`}>
          {selectedStandard ? (
            <>
              {/* Mobile Back Button to Catalog */}
              <button
                onClick={() => setMobileViewTab('catalog')}
                className="lg:hidden inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#EFEAE0] hover:bg-[#EAE4D8] border border-[#8C8275]/30 text-ink-text text-xs font-mono font-medium transition-colors cursor-pointer mb-1"
              >
                <ArrowLeft size={13} />
                <span>{t('standards_back_to_list', '← Back to Standards List')} ({filteredAndSortedStandards.length})</span>
              </button>
              {/* Selected Standard Overview Card */}
              <StandardHeaderCard
                standard={selectedStandard}
                onOpenQcoDrawer={() => setQcoDrawerStandard(selectedStandard)}
                onOpenSupersessionDiff={() => setShowSupersessionModal(true)}
                onNavigateToAnalyze={handleNavigateToAnalyze}
              />

              {/* Sub-Tabs: Dependencies vs Timeline vs QCO */}
              <div className="flex items-center gap-2 pb-2 border-b border-parchment-border flex-wrap">
                <button
                  onClick={() => setActiveTab('dependencies')}
                  className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-all ${
                    activeTab === 'dependencies'
                      ? 'bg-ink-text text-parchment-surface font-semibold shadow-xs'
                      : 'text-ink-muted hover:bg-parchment-subtle'
                  }`}
                >
                  <GitFork size={13} />
                  <span>{t('standards_tab_deps', 'Normative Dependencies & Graph')}</span>
                </button>

                <button
                  onClick={() => setActiveTab('timeline')}
                  className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-all ${
                    activeTab === 'timeline'
                      ? 'bg-ink-text text-parchment-surface font-semibold shadow-xs'
                      : 'text-ink-muted hover:bg-parchment-subtle'
                  }`}
                >
                  <History size={13} />
                  <span>{t('standards_tab_timeline', 'Edition & Amendments Timeline')}</span>
                </button>

                <button
                  onClick={() => setShowSupersessionModal(true)}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono bg-parchment-surface hover:bg-parchment-subtle border border-parchment-border text-ink-text transition-colors cursor-pointer"
                  title="Compare technical shifts with superseded standard revisions"
                >
                  <History size={13} className="text-mineral-blue" />
                  <span>{t('standards_tab_diff', 'Supersession Diff Engine')}</span>
                </button>

                {selectedStandard.is_qco_mandatory && (
                  <button
                    onClick={() => setQcoDrawerStandard(selectedStandard)}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono bg-status-indigoBg text-status-indigo border border-status-indigoBorder font-semibold hover:bg-status-indigo hover:text-white transition-colors sm:ml-auto"
                  >
                    <Scale size={13} />
                    <span>{t('standards_tab_gazette', 'View Statutory Gazette Order')}</span>
                  </button>
                )}
              </div>

              {/* Active Tab Views */}
              {activeTab === 'dependencies' && graph && (
                <DependencyGraph
                  graph={graph}
                  onSelectNode={(id) => setToastMessage(`Inspecting dependency clause: ${id}`)}
                  onNavigateToStandard={handleNavigateToStandardNumber}
                />
              )}

              {activeTab === 'timeline' && currentness && (
                <EditionTimeline currentness={currentness} />
              )}
            </>
          ) : (
            /* No Standard Selected State */
            <div className="parchment-card rounded-xl p-12 text-center border border-parchment-border">
              <BookOpen size={32} className="mx-auto text-ink-faint mb-3" />
              <h3 className="text-lg font-serif font-bold text-ink-text">
                Select an Indian Standard
              </h3>
              <p className="text-xs text-ink-muted font-serif max-w-md mx-auto mt-1">
                Choose a standard from the catalog on the left to inspect its scope, normative cross-references, edition timeline, and statutory Quality Control Orders.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* QCO Drawer */}
      <QcoMandateDrawer
        standard={qcoDrawerStandard}
        isOpen={!!qcoDrawerStandard}
        onClose={() => setQcoDrawerStandard(null)}
      />

      {/* Supersession Diff Modal */}
      <SupersessionDiffModal
        isOpen={showSupersessionModal}
        onClose={() => setShowSupersessionModal(false)}
        defaultStandardNumber={selectedStandard?.standard_number}
      />

      {/* Toast Notification */}
      {toastMessage && (
        <Toast message={toastMessage} onClose={() => setToastMessage(null)} />
      )}
    </div>
  );
};
