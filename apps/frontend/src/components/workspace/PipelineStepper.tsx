import React from 'react';
import { CheckCircle, CircleDot, Circle } from 'lucide-react';

export interface PipelineStage {
  id: number;
  name: string;
  subtitle: string;
  status: 'COMPLETED' | 'ACTIVE' | 'PENDING';
}

interface PipelineStepperProps {
  stages: PipelineStage[];
  activeStage: number;
  onSelectStage: (stageId: number) => void;
}

export const PipelineStepper: React.FC<PipelineStepperProps> = ({
  stages,
  activeStage,
  onSelectStage,
}) => {
  return (
    <div className="w-full bg-parchment-surface border border-parchment-border rounded-xl p-3 sm:p-4 mb-6 shadow-parchment">
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
        {stages.map((stage) => {
          const isCurrent = stage.id === activeStage;
          const isDone = stage.status === 'COMPLETED';

          return (
            <button
              key={stage.id}
              onClick={() => onSelectStage(stage.id)}
              className={`p-2.5 rounded-lg border text-left transition-all ${
                isCurrent
                  ? 'border-ink-text bg-parchment-subtle shadow-xs'
                  : isDone
                  ? 'border-parchment-border bg-parchment-surface hover:bg-parchment-subtle/50'
                  : 'border-parchment-border/60 bg-parchment-surface/40 hover:bg-parchment-subtle/30 opacity-70'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-mono uppercase text-ink-muted">
                  STAGE 0{stage.id}
                </span>
                {isDone ? (
                  <CheckCircle size={13} className="text-status-sage" />
                ) : isCurrent ? (
                  <CircleDot size={13} className="text-mineral-blue animate-subtle-pulse" />
                ) : (
                  <Circle size={13} className="text-ink-faint" />
                )}
              </div>
              <div className="text-xs font-bold text-ink-text truncate font-serif">
                {stage.name}
              </div>
              <div className="text-[10px] text-ink-muted truncate font-mono mt-0.5">
                {stage.subtitle}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
