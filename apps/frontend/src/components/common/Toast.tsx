import React from 'react';
import { Check, X } from 'lucide-react';

interface ToastProps {
  message: string;
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, onClose }) => {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-2.5 rounded-lg bg-ink-text text-parchment-surface border border-parchment-border shadow-parchment-lg text-xs font-mono">
      <Check size={14} className="text-emerald-400" />
      <span>{message}</span>
      <button onClick={onClose} className="ml-2 text-ink-faint hover:text-white">
        <X size={12} />
      </button>
    </div>
  );
};
