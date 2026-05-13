// src/hooks/morse/useMorseInput.ts
import { useCallback } from 'react';
import { useMorseStore } from '../../store/morseStore';
import { MorseSignal } from '../../types/morse';
import { socketService } from '../../services/socket/socket';

export const useMorseInput = () => {
  const {
    currentInput,
    decodedText,
    isTransmitting,
    inputMode,
    signals,
    addSignal,
    setDecodedText,
    setTransmitting,
    clearInput,
    completeLetter,
  } = useMorseStore();

  const addMorseSignal = useCallback((signal: '.' | '-') => {
    const morseSignal: MorseSignal = {
      signal,
      timestamp: new Date(),
    };

    addSignal(morseSignal);

    // Send to server for real-time decoding
    socketService.emit('morse_signal', {
      signal,
      conversationId: 'active-conversation', // Will be dynamic
      isComplete: false,
    });

    setTransmitting(true);
  }, [addSignal, setTransmitting]);

  const finishLetter = useCallback(() => {
    completeLetter();

    socketService.emit('morse_signal', {
      signal: ' ',
      conversationId: 'active-conversation',
      isComplete: true,
    });

    setTransmitting(false);
  }, [completeLetter, setTransmitting]);

  const finishWord = useCallback(() => {
    // Add word separator
    const wordSignal: MorseSignal = {
      signal: '/',
      timestamp: new Date(),
    };

    addSignal(wordSignal);
    setTransmitting(false);
  }, [addSignal, setTransmitting]);

  return {
    currentInput,
    decodedText,
    isTransmitting,
    inputMode,
    signals,
    addMorseSignal,
    finishLetter,
    finishWord,
    clearInput,
    setDecodedText,
  };
};