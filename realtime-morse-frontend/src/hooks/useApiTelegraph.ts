import { useState, useCallback, useEffect } from 'react';
import { processSignal, getCalibrationStatus } from '@/lib/api';

export interface UseApiTelegraphOptions {
  useBackend?: boolean;
}

export function useApiTelegraph(options: UseApiTelegraphOptions = {}) {
  const [modelTrained, setModelTrained] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if model is trained on mount
  useEffect(() => {
    const checkModel = async () => {
      try {
        const status = await getCalibrationStatus();
        setModelTrained(status.is_trained);
      } catch (err) {
        console.warn('Could not check model status:', err);
      }
    };
    checkModel();
  }, []);

  // Process a signal duration to classify as dot/dash
  const classifySignalDuration = useCallback(
    async (durationMs: number): Promise<{ signal: string; valid: boolean; reason?: string } | null> => {
      if (!options.useBackend) return null;

      setLoading(true);
      setError(null);
      try {
        const result = await processSignal(durationMs, modelTrained);
        return {
          signal: result.signal_type || '?',
          valid: result.validation.valid,
          reason: result.validation.reason,
        };
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [options.useBackend, modelTrained]
  );

  return {
    modelTrained,
    loading,
    error,
    classifySignalDuration,
  };
}
