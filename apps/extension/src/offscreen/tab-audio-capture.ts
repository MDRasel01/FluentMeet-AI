/**
 * FluentMeet AI - Remote Tab Audio Capture Engine (Pipeline A)
 * Uses chrome.tabCapture Stream ID -> getUserMedia -> AudioContext -> AudioWorklet.
 * Preserves normal tab audio playback via audioContext.destination.
 * Specification: Step 05 - Section 4.2.D & Section 9.1 & 9.3
 */

export interface TabAudioCaptureCallbacks {
  onChunk: (samples: Float32Array, inputSampleRate: number) => void;
  onError: (error: Error) => void;
  onEnded: () => void;
}

export class TabAudioCapture {
  private mediaStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private sourceNode: MediaStreamAudioSourceNode | null = null;
  private workletNode: AudioWorkletNode | null = null;
  private isCapturing: boolean = false;

  public async startCapture(
    streamId: string,
    workletUrl: string,
    callbacks: TabAudioCaptureCallbacks
  ): Promise<void> {
    if (this.isCapturing) {
      throw new Error('Tab audio capture is already active.');
    }

    try {
      // 1. Consume Stream ID from tabCapture
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          mandatory: {
            chromeMediaSource: 'tab',
            chromeMediaSourceId: streamId,
          },
        } as unknown as MediaTrackConstraints,
        video: false,
      });

      this.mediaStream = stream;

      // Handle track ended (e.g. user closed tab or stopped capture in browser UI)
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

      // 5. Connect to Audio Destination so user can still hear the meeting!
      // This satisfies Section 9.3 "Preserve Normal Tab Audio Playback"
      this.sourceNode.connect(this.audioContext.destination);

      // 6. Connect to AudioWorkletNode for streaming
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
