/**
 * FluentMeet AI - Local Microphone Audio Capture Engine (Pipeline B)
 * Requests audio-only getUserMedia -> AudioContext -> AudioWorklet.
 * Note: Never connected to audioContext.destination to avoid ear feedback.
 * Specification: Step 05 - Section 4.2.D & Section 9.2
 */

export interface MicrophoneCaptureCallbacks {
  onChunk: (samples: Float32Array, inputSampleRate: number) => void;
  onError: (error: Error) => void;
  onEnded: () => void;
}

export class MicrophoneCapture {
  private mediaStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private sourceNode: MediaStreamAudioSourceNode | null = null;
  private workletNode: AudioWorkletNode | null = null;
  private isCapturing: boolean = false;

  public async startCapture(
    workletUrl: string,
    callbacks: MicrophoneCaptureCallbacks
  ): Promise<void> {
    if (this.isCapturing) {
      throw new Error('Microphone audio capture is already active.');
    }

    try {
      // 1. Request audio-only permission (never camera per Section 9.2)
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        video: false,
      });

      this.mediaStream = stream;

      // Handle microphone unplugged or track stopped
      const audioTrack = stream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.onended = () => {
          this.stopCapture();
          callbacks.onEnded();
        };
      }

      // 2. Setup AudioContext
      this.audioContext = new AudioContext();
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      // 3. Load AudioWorklet
      await this.audioContext.audioWorklet.addModule(workletUrl);

      // 4. Create Source Node
      this.sourceNode = this.audioContext.createMediaStreamSource(stream);

      // 5. Connect strictly to worklet (NOT to destination)
      this.workletNode = new AudioWorkletNode(this.audioContext, 'fluentmeet-pcm-processor');
      this.workletNode.port.onmessage = (event) => {
        if (event.data?.type === 'AUDIO_CHUNK') {
          callbacks.onChunk(event.data.samples, this.audioContext?.sampleRate || 48000);
        }
      };

      this.sourceNode.connect(this.workletNode);
      this.isCapturing = true;
    } catch (err: unknown) {
      this.stopCapture();
      callbacks.onError(err instanceof Error ? err : new Error(String(err)));
      throw err;
    }
  }

  public stopCapture(): void {
    if (this.workletNode) {
      try {
        this.workletNode.disconnect();
      } catch (_) {}
      this.workletNode = null;
    }

    if (this.sourceNode) {
      try {
        this.sourceNode.disconnect();
      } catch (_) {}
      this.sourceNode = null;
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }

    if (this.audioContext) {
      try {
        this.audioContext.close();
      } catch (_) {}
      this.audioContext = null;
    }

    this.isCapturing = false;
  }

  public isActive(): boolean {
    return this.isCapturing;
  }
}

