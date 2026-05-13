/**
 * API client for Telegraph Backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const API_KEY = import.meta.env.VITE_API_KEY || '';

function withApiHeaders(extra: HeadersInit = {}): HeadersInit {
  const headers: Record<string, string> = {
    ...(extra as Record<string, string>),
  };

  if (API_KEY) {
    headers['X-API-Key'] = API_KEY;
  }

  return headers;
}

export interface DecodedResult {
  decoded: string;
}

export interface EncodedResult {
  morse_code: string;
}

export interface CalibrationResponse {
  status: string;
  accuracy: number;
  samples_bg: number;
  samples_tap: number;
}

export interface CalibrationStatus {
  is_trained: boolean;
  model_type: string;
}

export interface TapClassification {
  tap_probability: number;
  is_tap: boolean;
  signal_type: string;
  duration_ms: number;
  model_trained: boolean;
}

export interface SignalProcessing {
  signal_type: string | null;
  duration_ms: number;
  validation: {
    valid: boolean;
    reason: string;
  };
  model_trained: boolean;
}

export interface Settings {
  dot_threshold_ms: number;
  letter_gap_ms: number;
  word_gap_ms: number;
  gain: number;
  spike_factor: number;
  sample_rate: number;
}

// ─────────────────────────────────────────────────────────────
// Health Check
// ─────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<{ status: string; model_trained: boolean }> {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) throw new Error(`Health check failed: ${response.statusText}`);
  return response.json();
}

// ─────────────────────────────────────────────────────────────
// Morse Decoding/Encoding
// ─────────────────────────────────────────────────────────────

export async function decodeMorse(morseChars: string[]): Promise<string> {
  const response = await fetch(`${API_URL}/decode`, {
    method: 'POST',
    headers: withApiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ morse_chars: morseChars }),
  });
  if (!response.ok) throw new Error(`Decode failed: ${response.statusText}`);
  const result: DecodedResult = await response.json();
  return result.decoded;
}

export async function encodeText(text: string): Promise<string> {
  const response = await fetch(`${API_URL}/encode`, {
    method: 'POST',
    headers: withApiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ text }),
  });
  if (!response.ok) throw new Error(`Encode failed: ${response.statusText}`);
  const result: EncodedResult = await response.json();
  return result.morse_code;
}

// ─────────────────────────────────────────────────────────────
// Calibration
// ─────────────────────────────────────────────────────────────

export async function calibrateModel(bgBlob: Blob, tapsBlob: Blob): Promise<CalibrationResponse> {
  const formData = new FormData();
  formData.append('background', bgBlob, 'background.wav');
  formData.append('taps', tapsBlob, 'taps.wav');

  const response = await fetch(`${API_URL}/calibrate`, {
    method: 'POST',
    headers: withApiHeaders(),
    body: formData,
  });
  if (!response.ok) throw new Error(`Calibration failed: ${response.statusText}`);
  return response.json();
}

export async function getCalibrationStatus(): Promise<CalibrationStatus> {
  const response = await fetch(`${API_URL}/calibrate-status`, {
    headers: withApiHeaders(),
  });
  if (!response.ok) throw new Error(`Status check failed: ${response.statusText}`);
  return response.json();
}

// ─────────────────────────────────────────────────────────────
// Audio Processing
// ─────────────────────────────────────────────────────────────

export async function classifyTap(audioBlob: Blob): Promise<TapClassification> {
  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'audio.wav');

  const response = await fetch(`${API_URL}/classify-tap`, {
    method: 'POST',
    headers: withApiHeaders(),
    body: formData,
  });
  if (!response.ok) throw new Error(`Classification failed: ${response.statusText}`);
  return response.json();
}

export async function processSignal(durationMs: number, useMl: boolean = true): Promise<SignalProcessing> {
  const response = await fetch(`${API_URL}/process-signal`, {
    method: 'POST',
    headers: withApiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ duration_ms: durationMs, use_ml: useMl }),
  });
  if (!response.ok) throw new Error(`Signal processing failed: ${response.statusText}`);
  return response.json();
}

// ─────────────────────────────────────────────────────────────
// Settings
// ─────────────────────────────────────────────────────────────

export async function getSettings(): Promise<Settings> {
  const response = await fetch(`${API_URL}/settings`, {
    headers: withApiHeaders(),
  });
  if (!response.ok) throw new Error(`Settings fetch failed: ${response.statusText}`);
  return response.json();
}
