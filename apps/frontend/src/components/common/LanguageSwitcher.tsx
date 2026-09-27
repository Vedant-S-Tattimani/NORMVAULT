import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, Check, X, Search, ChevronDown, Sparkles, Languages } from 'lucide-react';
import { SUPPORTED_LANGUAGES, LanguageOption } from '../../i18n/languages';
import { changeAppLanguage } from '../../i18n';

interface LanguageSwitcherProps {
  className?: string;
  variant?: 'header' | 'floating' | 'compact';
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  className = '',
  variant = 'compact',
}) => {
  const { t, i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [regionFilter, setRegionFilter] = useState<'ALL' | 'NORTH' | 'SOUTH' | 'EAST' | 'WEST'>('ALL');

  const currentLang = useMemo(() => {
    const code = i18n.language || 'en';
    return (
      SUPPORTED_LANGUAGES.find((l) => l.code === code) ||
      SUPPORTED_LANGUAGES[0]
    );
  }, [i18n.language]);

  const filteredLanguages = useMemo(() => {
    let list = SUPPORTED_LANGUAGES;

    // Filter by Region
    if (regionFilter !== 'ALL') {
      list = list.filter((l) => {
        const reg = l.region.toLowerCase();
        if (regionFilter === 'SOUTH') return reg.includes('south') || reg.includes('andhra') || reg.includes('tamil') || reg.includes('karnataka') || reg.includes('kerala');
        if (regionFilter === 'NORTH') return reg.includes('north') || reg.includes('central') || reg.includes('punjab') || reg.includes('jammu');
        if (regionFilter === 'EAST') return reg.includes('east') || reg.includes('bengal') || reg.includes('assam') || reg.includes('odisha') || reg.includes('bihar');
        if (regionFilter === 'WEST') return reg.includes('west') || reg.includes('gujarat') || reg.includes('maharashtra') || reg.includes('goa');
        return true;
      });
    }

    if (!searchQuery.trim()) return list;
    const q = searchQuery.toLowerCase().trim();
    return list.filter(
      (l) =>
        l.name.toLowerCase().includes(q) ||
        l.nativeName.toLowerCase().includes(q) ||
        l.code.toLowerCase().includes(q) ||
        l.region.toLowerCase().includes(q) ||
        l.script.toLowerCase().includes(q)
    );
  }, [searchQuery, regionFilter]);

  const handleSelectLanguage = (lang: LanguageOption) => {
    changeAppLanguage(lang.code);
    setIsOpen(false);
    setSearchQuery('');
  };

  // Determine sizing according to variant
  const variantClasses = {
    header: 'px-3 py-1.5 text-xs',
    compact: 'px-2.5 py-1 text-[11px] sm:text-xs',
    floating: 'px-3.5 py-2 text-xs shadow-lg',
  }[variant] || 'px-3 py-1.5 text-xs';

  return (
    <>
      {/* Ultra-Premium Institutional Language Switcher Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`group relative inline-flex items-center gap-2 rounded-full font-serif font-medium bg-gradient-to-r from-[#FFFDF9] via-[#FAF6ED] to-[#F5EFE0] border border-[#C5A059]/45 hover:border-[#B89758] shadow-[0_2px_10px_-2px_rgba(197,160,89,0.30)] hover:shadow-[0_4px_20px_-2px_rgba(197,160,89,0.48)] transition-all duration-200 active:scale-96 cursor-pointer select-none ${variantClasses} ${className}`}
        title={`Change Display Language / भाषा बदलें (${currentLang.nativeName})`}
        aria-label="Change Display Language"
      >
        {/* Subtle Luxury Gold Shimmer Overlay */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[#C5A059]/10 via-[#2C6E80]/5 to-[#C5A059]/15 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

        {/* Globe Icon with Live Glowing Dot */}
        <div className="relative flex items-center justify-center shrink-0">
          <Globe
            size={14}
            className="text-[#2C6E80] group-hover:rotate-45 transition-transform duration-500 ease-out"
          />
          <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-emerald-500 ring-1 ring-white animate-pulse" />
        </div>

        {/* Current Native Language Name with Bold Serif */}
        <span className="font-serif font-bold text-xs text-[#1E2320] tracking-normal group-hover:text-[#2C6E80] transition-colors whitespace-nowrap">
          {currentLang.nativeName}
        </span>

        {/* Luxury Gold/Teal Code Badge */}
        <span className="px-1.5 py-0.2 rounded text-[9px] font-mono tracking-wider uppercase bg-[#EBF3F4] text-[#2C6E80] border border-[#2C6E80]/25 font-bold shrink-0">
          {currentLang.code}
        </span>

        {/* Chevron Micro-Indicator */}
        <ChevronDown
          size={12}
          className="text-[#787165] group-hover:text-[#1E2320] group-hover:translate-y-0.5 transition-all duration-200 shrink-0"
        />
      </button>

      {/* Language Selection Modal */}
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200"
          onClick={() => setIsOpen(false)}
        >
          <div
            className="bg-[#FCFAF6] border border-[#8C8275]/40 rounded-2xl w-full max-w-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden font-sans text-[#1E2320]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Top Header */}
            <div className="px-6 py-4 bg-[#EDE7DB] border-b border-[#8C8275]/25 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase bg-[#2C6E80]/15 text-[#2C6E80] font-bold border border-[#2C6E80]/30 flex items-center gap-1">
                    <Sparkles size={11} />
                    <span>20 Official Indian Languages</span>
                  </span>
                  <span className="text-[10px] font-mono text-[#787165] hidden sm:inline">
                    Constitution of India • Eighth Schedule
                  </span>
                </div>
                <h3 className="text-xl sm:text-2xl font-bold font-serif text-[#1E2320] tracking-tight flex items-center gap-2">
                  <Languages size={22} className="text-[#2C6E80]" />
                  <span>{t('lang_modal_title', 'Select Display Language / भाषा चुनें')}</span>
                </h3>
                <p className="text-xs text-[#525650] font-serif mt-0.5">
                  {t(
                    'lang_modal_sub',
                    'Choose from 20 official Indian languages plus English for complete translation across all pages and features.'
                  )}
                </p>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-[#787165] hover:text-[#1E2320] hover:bg-[#E2DACB] transition-colors cursor-pointer"
                aria-label="Close language selector"
              >
                <X size={20} />
              </button>
            </div>

            {/* Region Filter Bar & Search Input */}
            <div className="px-6 pt-4 pb-2 bg-[#F6F2EA] border-b border-[#8C8275]/20 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
              {/* Search Box */}
              <div className="relative flex-1">
                <Search
                  size={14}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[#787165]"
                />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('lang_search_placeholder', 'Search language name, script, or state...')}
                  className="w-full pl-9 pr-8 py-2 text-xs font-mono bg-[#FCFAF6] border border-[#8C8275]/40 rounded-xl text-[#1E2320] placeholder-[#787165]/60 focus:outline-hidden focus:border-[#2C6E80] focus:ring-1 focus:ring-[#2C6E80]/20 shadow-2xs"
                  autoFocus
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#787165] hover:text-[#1E2320] p-0.5"
                  >
                    <X size={12} />
                  </button>
                )}
              </div>

              {/* Region Chips */}
              <div className="flex items-center gap-1.5 overflow-x-auto text-[11px] font-mono shrink-0 pb-1 sm:pb-0">
                {(['ALL', 'NORTH', 'SOUTH', 'EAST', 'WEST'] as const).map((reg) => (
                  <button
                    key={reg}
                    onClick={() => setRegionFilter(reg)}
                    className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                      regionFilter === reg
                        ? 'bg-[#1E231D] text-[#FCFAF6] font-bold shadow-2xs'
                        : 'bg-[#EDE7DB] text-[#525650] hover:bg-[#E2DACB]'
                    }`}
                  >
                    {reg === 'ALL' ? 'All (21)' : reg}
                  </button>
                ))}
              </div>
            </div>

            {/* Language Selection Grid */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {filteredLanguages.map((lang) => {
                const isActive = lang.code === currentLang.code;
                return (
                  <button
                    key={lang.code}
                    onClick={() => handleSelectLanguage(lang)}
                    className={`flex items-start justify-between p-3.5 rounded-xl border text-left transition-all duration-150 cursor-pointer group ${
                      isActive
                        ? 'bg-[#2C6E80] text-white border-[#2C6E80] shadow-md ring-2 ring-[#2C6E80]/30 font-medium'
                        : 'bg-[#FCFAF6] hover:bg-[#FAF7F0] text-[#1E2320] border-[#8C8275]/30 hover:border-[#2C6E80]/60 hover:shadow-xs'
                    }`}
                  >
                    <div className="pr-2">
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className={`text-base font-serif font-bold ${
                            isActive ? 'text-white' : 'text-[#1E2320] group-hover:text-[#2C6E80]'
                          } transition-colors`}
                        >
                          {lang.nativeName}
                        </span>
                        <span
                          className={`px-1.5 py-0.2 rounded text-[9px] font-mono font-bold uppercase tracking-wider ${
                            isActive
                              ? 'bg-white/20 text-white'
                              : 'bg-[#EAE4D8] text-[#525650] border border-[#8C8275]/20'
                          }`}
                        >
                          {lang.code}
                        </span>
                      </div>

                      <div
                        className={`text-xs font-medium font-sans ${
                          isActive ? 'text-white/90' : 'text-[#4A4E49]'
                        }`}
                      >
                        {lang.name} • {lang.script}
                      </div>

                      <div
                        className={`text-[10px] font-serif mt-1 ${
                          isActive ? 'text-white/75' : 'text-[#787165]'
                        }`}
                      >
                        {lang.region}
                      </div>
                    </div>

                    {isActive && (
                      <div className="w-5 h-5 rounded-full bg-white text-[#2C6E80] flex items-center justify-center shrink-0 mt-0.5 shadow-2xs">
                        <Check size={13} strokeWidth={3} />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Modal Bottom Footer */}
            <div className="px-6 py-3 bg-[#EDE7DB] border-t border-[#8C8275]/25 flex items-center justify-between text-xs font-mono text-[#787165]">
              <div>
                <span>{filteredLanguages.length} Languages Available</span>
                <span className="hidden sm:inline"> • Instant Live Switch</span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="px-3.5 py-1 rounded-lg border border-[#8C8275]/30 hover:bg-[#E2DACB] text-[#1E2320] font-semibold transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
