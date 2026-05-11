import { virtualLogLines } from '../model/detectionData';

export function LogCodeViewer() {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-700/80 bg-slate-950/20">
      <div className="grid max-h-[330px] grid-cols-[52px_1fr] overflow-y-auto font-mono text-[16px] leading-[1.85] tracking-[-0.04em]">
        <div className="border-r border-slate-700/80 py-4 text-center text-slate-400">
          {virtualLogLines.map((line) => (
            <div key={line.line}>{line.line}</div>
          ))}
        </div>
        <pre className="m-0 py-4 pl-5 pr-4">
          {virtualLogLines.map((line) => (
            <div key={line.line}>
              {line.line > 1 && line.line < 8 ? <span className="text-slate-600">| </span> : null}
              {line.line > 1 && line.line < 8 ? <span className="pl-2" /> : null}
              {line.content.map((part, index) => (
                <span key={`${line.line}-${index}`} className={part.color}>
                  {part.text}
                </span>
              ))}
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
}
