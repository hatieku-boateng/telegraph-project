// src/types/morse.ts
export interface MorseSignal {
  signal: '.' | '-' | ' ';
  duration?: number;
  timestamp: Date;
  confidence?: number;
}

export interface MorseState {
  currentInput: string;
  decodedText: string;
  isTransmitting: boolean;
  inputMode: 'keyboard' | 'microphone' | 'text';
  signals: MorseSignal[];
}

export interface AudioFeatures {
  rms: number;
  peak: number;
  crestFactor: number;
  zeroCrossingRate: number;
  spectralCentroid: number;
  attackSharpness: number;
}

export interface TapDetectionResult {
  isTap: boolean;
  probability: number;
  signalType: '.' | '-' | null;
  duration: number;
}

export type InputMode = 'keyboard' | 'microphone' | 'text';