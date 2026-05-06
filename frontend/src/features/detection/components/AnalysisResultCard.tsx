import type { analysisResults } from '../model/detectionData';
import { detectionColorClasses, type DetectionColor } from '../model/detectionTheme';

type AnalysisResultCardProps = {
  item: (typeof analysisResults)[number];
};

export function AnalysisResultCard({ item }: AnalysisResultCardProps) {
  const Icon = item.icon;
  const palette = detectionColorClasses[item.color as DetectionColor];

  return (
    <article className="grid min-h-[88px] grid-cols-[56px_1fr_auto] items-center gap-4 rounded-xl border border-slate-700/80 bg-slate-900/20 px-5 py-4 shadow-panel">
      <div className={`grid h-12 w-12 place-items-center rounded-full ${palette.bg}`}>
        <Icon className={`h-7 w-7 ${palette.icon}`} strokeWidth={2.2} />
      </div>
      <h3 className="text-[22px] font-black tracking-[-0.05em] text-white">{item.label}</h3>
      <p className={`text-right text-[23px] font-black tracking-[-0.05em] ${palette.text}`}>{item.value}</p>
    </article>
  );
}
