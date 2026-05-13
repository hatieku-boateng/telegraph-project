// src/store/morseStore.ts
import { create } from 'zustand';
import { MorseState, MorseSignal, InputMode } from '../types/morse';

interface MorseStore extends MorseState {
  // Actions
  setInputMode: (mode: InputMode) => void;
  addSignal: (signal: MorseSignal) => void;
  setDecodedText: (text: string) => void;
  setTransmitting: (transmitting: boolean) => void;
  clearInput: () => void;
  completeLetter: () => void;
  completeWord: () => void;
}

export const useMorseStore = create<MorseStore>((set, get) => ({
  currentInput: '',
  decodedText: '',
  isTransmitting: false,
  inputMode: 'text',
  signals: [],

  setInputMode: (inputMode) => set({ inputMode }),

  addSignal: (signal) => set((state) => ({
    signals: [...state.signals, signal],
    currentInput: state.currentInput + signal.signal,
  })),

  setDecodedText: (decodedText) => set({ decodedText }),

  setTransmitting: (isTransmitting) => set({ isTransmitting }),

  clearInput: () => set({
    currentInput: '',
    decodedText: '',
    signals: [],
  }),

  completeLetter: () => set((state) => ({
    currentInput: state.currentInput + ' ',
  })),

  completeWord: () => set((state) => ({
    currentInput: state.currentInput + ' / ',
  })),
}));