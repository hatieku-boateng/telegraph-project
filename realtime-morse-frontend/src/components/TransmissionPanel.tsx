import { Card, CardContent } from '@/components/ui/card';
import { ArrowRight, Sparkles } from 'lucide-react';

interface TransmissionPanelProps {
  currentSignals: string;
  rawSequence: string;
  decodedText: string;
  isPressing: boolean;
}

const beamPoints = Array.from({ length: 6 }, (_, index) => index);

export function TransmissionPanel({ currentSignals, rawSequence, decodedText, isPressing }: TransmissionPanelProps) {
  const activeSequence = rawSequence.length > 0 ? rawSequence : '.-.-.-';
  const displaySignals = currentSignals || 'waiting';
  const statusText = isPressing ? 'TRANSMITTING' : rawSequence ? 'RECEIVING' : 'STANDBY';

  return (
    <Card className="border-telegraph-border bg-telegraph-card overflow-hidden">
      <CardContent className="relative p-6 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.16),_transparent_35%),radial-gradient(circle_at_bottom_right,_rgba(245,158,11,0.16),_transparent_30%)]" />
        <div className="relative space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-telegraph-muted">Futuristic Link</p>
              <h2 className="mt-2 text-lg font-semibold text-telegraph-text">Holo-Transmission</h2>
            </div>
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-emerald-200">
              <Sparkles className="h-3.5 w-3.5 text-emerald-300" />
              {statusText}
            </div>
          </div>

          <div className="relative rounded-3xl border border-telegraph-border bg-telegraph-bg/80 p-5 shadow-[inset_0_0_60px_rgba(255,255,255,0.04)]">
            <div className="absolute inset-x-0 top-1/2 h-px bg-gradient-to-r from-emerald-400/40 via-emerald-200/30 to-transparent" />
            <div className="relative h-24 overflow-hidden">
              {beamPoints.map((index) => {
                const point = activeSequence[index % activeSequence.length];
                const width = point === '.' ? 10 : 24;
                const animationDelay = `-${index * 0.35}s`;

                return (
                  <span
                    key={index}
                    className="absolute top-1/2 inline-flex items-center justify-center rounded-full bg-emerald-300/80 shadow-[0_0_18px_rgba(34,197,94,0.45)] text-[10px] text-telegraph-bg animate-signal-drive"
                    style={{
                      left: `${index * 16}%`,
                      width,
                      height: width,
                      marginTop: `-${width / 2}px`,
                      animationDelay,
                    }}
                  >
                    <span className={point === '.' ? 'h-2 w-2 rounded-full bg-telegraph-bg block' : 'h-1.5 w-6 rounded-full bg-telegraph-bg block'} />
                  </span>
                );
              })}
              <span className="absolute -left-6 top-1/2 h-3 w-3 rounded-full bg-emerald-400 shadow-[0_0_24px_rgba(34,197,94,0.65)] animate-ping" />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_280px]">
            <div className="rounded-2xl border border-telegraph-border bg-telegraph-card p-4">
              <p className="text-[11px] uppercase tracking-[0.24em] text-telegraph-muted">Waveform</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {displaySignals.split('').map((signal, index) => (
                  <span
                    key={`${signal}-${index}`}
                    className={`inline-flex items-center justify-center rounded-full border px-2 py-1 text-xs font-semibold ${signal === '.' ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-200' : 'border-sky-400/30 bg-sky-400/10 text-sky-200'}`}
                  >
                    {signal}
                  </span>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-telegraph-border bg-telegraph-card p-4">
              <div className="flex items-center justify-between text-xs uppercase tracking-[0.24em] text-telegraph-muted">
                <span>Message</span>
                <ArrowRight className="h-3.5 w-3.5 text-telegraph-accent" />
              </div>
              <p className="mt-3 min-h-[3rem] font-mono text-sm leading-relaxed text-telegraph-text">
                {decodedText || <span className="text-telegraph-muted italic">No decoded message yet.</span>}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
