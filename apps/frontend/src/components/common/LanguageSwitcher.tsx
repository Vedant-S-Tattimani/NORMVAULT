import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, Check, X, Search } from 'lucide-react';
import { SUPPORTED_LANGUAGES, LanguageOption } from '../../i18n/languages';
import { changeAppLanguage } from '../../i18n';

interface LanguageSwitcherProps {
  className?: string;
  variant?: 'header' | 'floating' | 'compact';
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  className = '',
  variant = 'header',
}) => {
  const { t, i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const currentLang = useMemo(() => {
    const code = i18n.language || 'en';
    return (
      SUPPORTED_LANGUAGES.find((l) => l.code === code) ||
      SUPPORTED_LANGUAGES[0]
    );
  }, [i18n.language]);

  const filteredLanguages = useMemo(() => {
    if (!searchQuery.trim()) return SUPPORTED_LANGUAGES;
    const q = searchQuery.toLowerCase().trim();
    return SUPPORTED_LANGUAGES.filter(
      (l) =>
        l.name.toLowerCase().includes(q) ||
        l.nativeName.toLowerCase().includes(q) ||
        l.code.toLowerCase().includes(q) ||
        l.region.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  const handleSelectLanguage = (lang: LanguageOption) => {
    changeAppLanguage(lang.code);
    setIsOpen(false);
    setSearchQuery('');
  };

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono transition-all border shadow-2xs cursor-pointer select-none ${
          variant === 'compact'
            ? 'bg-parchment-surface/90 hover:bg-parchment-subtle text-ink-text border-parchment-border'
            : 'bg-parchment-surface hover:bg-parchment-subtle text-ink-text border-parchment-border hover:border-mineral-blue/40'
        } ${className}`}
        title={`Change Language / भाषा बदलें (${currentLang.nativeName})`}
        aria-label="Change Language"
      >
        <Globe size={13} className="text-mineral-blue shrink-0 animate-pulse-slow" />
        <span className="font-semibold text-ink-text">{currentLang.nativeName}</span>
        <span className="text-[10px] text-ink-muted uppercase">({currentLang.code})</span>
      </button>

      {/* Language Selection Modal */}
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink-text/50 backdrop-blur-xs animate-fadeIn"
          onClick={() => setIsOpen(false)}
        >
          <div
            className="parchment-card rounded-2xl p-5 sm:p-6 w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl border border-parchment-border animate-scaleUp"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-start justify-between gap-4 pb-4 border-b border-parchment-border">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-mineral-light text-mineral-dark font-semibold border border-mineral-blue/20">
                    20 Official Indian Languages
                  </span>
                  <span className="text-[10px] font-mono text-ink-muted hidden sm:inline">
                    Eighth Schedule Aligned
                  </span>
                </div>
                <h3 className="text-xl font-bold font-serif text-ink-text">
                  {t('lang_modal_title', 'Select Display Language / भाषा चुनें')}
                </h3>
                <p className="text-xs text-ink-muted font-serif mt-0.5">
                  {t(
                    'lang_modal_sub',
                    'Choose from 20 official Indian languages plus English for complete translation across all pages and features.'
                  )}
                </p>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-ink-muted hover:text-ink-text hover:bg-parchment-subtle border border-transparent hover:border-parchment-border transition-all cursor-pointer"
                aria-label="Close language selector"
              >
                <X size={18} />
              </button>
            </div>

            {/* Search Input */}
            <div className="pt-3 pb-2">
              <div className="relative">
                <Search
                  size={14}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted"
                />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('lang_search_placeholder', 'Search language name, script, or state...')}
                  className="w-full pl-9 pr-4 py-2 text-xs font-mono bg-parchment-surface border border-parchment-border rounded-lg text-ink-text placeholder-ink-muted/60 focus:outline-hidden focus:border-mineral-blue focus:ring-1 focus:ring-mineral-blue/20"
                  autoFocus
                />
              </div>
            </div>

            {/* Language Grid */}
            <div className="flex-1 overflow-y-auto pr-1 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 py-2">
              {filteredLanguages.map((lang) => {
                const isActive = lang.code === currentLang.code;
                return (
                  <button
                    key={lang.code}
                    onClick={() => handleSelectLanguage(lang)}
                    className={`flex items-start justify-between p-3 rounded-xl border text-left transition-all cursor-pointer group ${
                      isActive
                        ? 'bg-mineral-blue text-white border-mineral-blue shadow-xs font-medium'
                        : 'bg-parchment-surface hover:bg-parchment-subtle text-ink-text border-parchment-border hover:border-mineral-blue/30'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`text-sm font-bold ${
                            isActive ? 'text-white' : 'text-ink-text group-hover:text-mineral-blue'
                          }`}
                        >
                          {lang.nativeName}
                        </span>
                        <span
                          className={`text-[10px] font-mono uppercase px-1 rounded ${
                            isActive ? 'bg-white/20 text-white' : 'bg-parchment-subtle text-ink-muted'
                          }`}
                        >
                          {lang.code}
                        </span>
                      </div>
                      <div
                        className={`text-xs mt-0.5 ${
                          isActive ? 'text-white/90' : 'text-ink-muted'
                        }`}
                      >
                        {lang.name} • {lang.script}
                      </div>
                      <div
                        className={`text-[10px] mt-1 line-clamp-1 ${
                          isActive ? 'text-white/75' : 'text-ink-faint'
                        }`}
                      >
                        {lang.region}
                      </div>
                    </div>

                    {isActive && (
                      <span className="shrink-0 p-1 rounded-full bg-white/20 text-white mt-0.5">
                        <Check size={12} strokeWidth={3} />
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Footer */}
            <div className="pt-3 border-t border-parchment-border flex items-center justify-between text-[11px] font-mono text-ink-muted">
              <span>20 Official Indian Languages • 8th Schedule</span>
              <button
                onClick={() => setIsOpen(false)}
                className="px-3 py-1 rounded bg-parchment-subtle hover:bg-parchment-border text-ink-text border border-parchment-border transition-all cursor-pointer"
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
