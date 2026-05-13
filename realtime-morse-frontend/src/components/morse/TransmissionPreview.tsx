import { Card, CardContent } from '@/components/ui/card';

interface TransmissionPreviewProps {
  source: string;
  decodedText: string;
  rawSequence: string;
}

export function TransmissionPreview({ source, decodedText, rawSequence }: TransmissionPreviewProps) {
  return (
    <Card className="border-gray-700 bg-gray-900">
      <CardContent className="space-y-4 p-4">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span className="font-semibold">Preview</span>
          <span className="rounded-full border border-gray-700 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-gray-300">
            {source}
          </span>
        </div>
        <div className="rounded-md bg-gray-950 border border-gray-800 p-3 text-sm text-gray-100">
          <div className="font-medium text-gray-200 mb-2">Decoded Text</div>
          <div className="whitespace-pre-wrap break-words">{decodedText || 'No decoded message yet.'}</div>
        </div>
        {rawSequence ? (
          <div className="rounded-md bg-gray-950 border border-gray-800 p-3 font-mono text-sm text-amber-300">
            <div className="font-medium text-gray-200 mb-2">Signal Sequence</div>
            <div className="break-words">{rawSequence}</div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
