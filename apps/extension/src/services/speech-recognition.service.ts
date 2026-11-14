/**
 * FluentMeet AI - Speech Recognition Service for Chrome Extension
 * Implements real-time microphone capture and continuous speech-to-text recognition
 * using the Web Speech Recognition API with comprehensive state management and interim transcripts.
 * Specification: Part B - Section 4
 */

export type VoiceRecognitionState =
  | 'IDLE'
  | 'REQUESTING_PERMISSION'
  | 'INITIALIZING'
  | 'LISTENING'
  | 'PROCESSING'
  | 'RESULT_RECEIVED'
  | 'ERROR'
  | 'STOPPED';

export interface RecognizedTranscriptItem {
  id: string;
  text: string;
  isFinal: boolean;
  confidence: number;
  timestampMs: number;
}

export interface SpeechRecognitionCallbacks {
  onStateChange: (state: VoiceRecognitionState) => void;
  onInterimResult: (text: string) => void;
  onFinalResult: (item: RecognizedTranscriptItem) => void;
  onError: (errorMessage: string, errorCode?: string) => void;
  onEnd: () => void;
}

// Type declaration for Web Speech API in Chrome
declare global {
  interface Window {
    SpeechRecognition?: any;
    webkitSpeechRecognition?: any;
  }
}

export class SpeechRecognitionService {
  private recognition: any = null;
  private mediaStream: MediaStream | null = null;
  private state: VoiceRecognitionState = 'IDLE';
  private callbacks: SpeechRecognitionCallbacks | null = null;
  private isExplicitlyStopped: boolean = false;
  private language: string = 'en-US';
  private sessionStartTime: number = 0;

  constructor(language: string = 'en-US') {
    this.language = language;
  }

  public getState(): VoiceRecognitionState {
    return this.state;
  }

  public isSupported(): boolean {
    return typeof window !== 'undefined' && Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
  }

  public setLanguage(lang: string): void {
    this.language = lang;
    if (this.recognition) {
      try {
        this.recognition.lang = lang;
      } catch (_) {}
    }
  }

  /**
   * Starts capturing microphone audio and begins speech-to-text recognition.
   */
  public async start(callbacks: SpeechRecognitionCallbacks): Promise<void> {
    this.callbacks = callbacks;
    this.isExplicitlyStopped = false;
    this.sessionStartTime = Date.now();

    // 1. Verify Browser Support
    const SpeechRecognitionClass =
      typeof window !== 'undefined' ? window.SpeechRecognition || window.webkitSpeechRecognition : null;

    if (!SpeechRecognitionClass) {
      this.updateState('ERROR');
      callbacks.onError(
        'Speech Recognition API is not supported in this browser. Please use Google Chrome 116+.',
        'NOT_SUPPORTED'
      );
      return;
    }

    try {
      // 2. Request Microphone Access
      this.updateState('REQUESTING_PERMISSION');
      if (typeof navigator !== 'undefined' && navigator.mediaDevices?.getUserMedia) {
        try {
          this.mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true,
            },
            video: false,
          });
        } catch (permErr: any) {
          console.warn('[FluentMeet Speech] Direct getUserMedia note:', permErr);
          // Do not fatal-abort here; Web Speech API will prompt or handle audio stream directly
        }
      }

      // 3. Initialize Recognition Engine
      this.updateState('INITIALIZING');
      this.recognition = new SpeechRecognitionClass();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = this.language;
      this.recognition.maxAlternatives = 1;

      // Handle speech recognition lifecycle events
      this.recognition.onstart = () => {
        if (!this.isExplicitlyStopped) {
          this.updateState('LISTENING');
        }
      };

      this.recognition.onaudiostart = () => {
        if (this.state !== 'LISTENING' && !this.isExplicitlyStopped) {
          this.updateState('LISTENING');
        }
      };

      this.recognition.onresult = (event: any) => {
        if (this.isExplicitlyStopped) return;

        let interimAccumulator = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const result = event.results[i];
          const transcriptText = result[0]?.transcript?.trim() || '';

          if (!transcriptText) continue;

          if (result.isFinal) {
            this.updateState('RESULT_RECEIVED');
            const item: RecognizedTranscriptItem = {
              id: `trans-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
              text: transcriptText,
              isFinal: true,
              confidence: result[0]?.confidence || 0.92,
              timestampMs: Date.now() - this.sessionStartTime,
            };
            callbacks.onFinalResult(item);
            callbacks.onInterimResult('');
            // Return to listening state for subsequent speech
            this.updateState('LISTENING');
          } else {
            interimAccumulator += (interimAccumulator ? ' ' : '') + transcriptText;
          }
        }

        if (interimAccumulator) {
          this.updateState('PROCESSING');
          callbacks.onInterimResult(interimAccumulator);
        }
      };

      this.recognition.onerror = (event: any) => {
        if (this.isExplicitlyStopped) return;

        const errorCode = event.error;
        let humanMsg = `Speech recognition encountered an issue: ${errorCode}`;

        if (errorCode === 'no-speech') {
          // No speech detected is a normal timeout, resume listening
          return;
        } else if (errorCode === 'not-allowed') {
          humanMsg = 'Microphone permission blocked. Please allow mic access to enable speech coaching.';
        } else if (errorCode === 'network') {
          humanMsg = 'Network connection issue with Chrome speech service. Check internet connection.';
        } else if (errorCode === 'audio-capture') {
          humanMsg = 'Failed to capture audio from the microphone device.';
        } else if (errorCode === 'language-not-supported') {
          humanMsg = `Selected recognition language '${this.language}' is not supported.`;
        }

        this.updateState('ERROR');
        callbacks.onError(humanMsg, errorCode);
      };

      this.recognition.onend = () => {
        if (!this.isExplicitlyStopped && this.state === 'LISTENING') {
          // Auto-restart continuous recognition if Chrome stops after silence
          try {
            this.recognition.start();
          } catch (_) {
            this.updateState('STOPPED');
            callbacks.onEnd();
          }
        } else {
          this.updateState('STOPPED');
          callbacks.onEnd();
        }
      };

      // 4. Start Recognition
      this.recognition.start();
    } catch (err: any) {
      this.updateState('ERROR');
      callbacks.onError(err?.message || 'Failed to initialize speech recognition engine.', 'INIT_FAILED');
      this.stop();
    }
  }

  /**
   * Stops the active speech recognition session and cleanly releases all media tracks.
   */
  public stop(): void {
    this.isExplicitlyStopped = true;

    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (_) {
        try {
          this.recognition.abort();
        } catch (_) {}
      }
      this.recognition = null;
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch (_) {}
      });
      this.mediaStream = null;
    }

    this.updateState('STOPPED');
    if (this.callbacks) {
      this.callbacks.onEnd();
      this.callbacks = null;
    }
  }

  private updateState(newState: VoiceRecognitionState): void {
    this.state = newState;
    if (this.callbacks?.onStateChange) {
      this.callbacks.onStateChange(newState);
    }
  }
}

export const speechRecognitionService = new SpeechRecognitionService();

