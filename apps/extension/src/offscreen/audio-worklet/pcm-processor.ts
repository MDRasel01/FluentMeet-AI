/**
 * FluentMeet AI - PCM AudioWorkletProcessor
 * Runs on dedicated Web Audio rendering thread.
 * Buffers audio frames and emits chunked Float32 data to the Offscreen controller.
 * Specification: Step 05 - Section 9.4
 */

declare abstract class AudioWorkletProcessor {
  readonly port: MessagePort;
  abstract process(
    inputs: Float32Array[][],
    outputs: Float32Array[][],
    parameters: Record<string, Float32Array>
  ): boolean;
}
declare function registerProcessor(
  name: string,
  processorCtor: new () => AudioWorkletProcessor
): void;

class FluentMeetPcmProcessor extends AudioWorkletProcessor {
  private bufferSize: number = 2048; // ~128ms @ 16kHz or ~42ms @ 48kHz
  private buffer: Float32Array;
  private bufferIndex: number = 0;

  constructor() {
    super();
    this.buffer = new Float32Array(this.bufferSize);

    this.port.onmessage = (event: MessageEvent) => {
      if (event.data?.type === 'CONFIGURE') {
        if (event.data.bufferSize && typeof event.data.bufferSize === 'number') {
          this.bufferSize = event.data.bufferSize;
          this.buffer = new Float32Array(this.bufferSize);
          this.bufferIndex = 0;
        }
      }
    };
  }

  process(
    inputs: Float32Array[][],
    _outputs: Float32Array[][],
    _parameters: Record<string, Float32Array>
  ): boolean {
    const input = inputs[0];
    if (!input || input.length === 0) {
      return true;
    }

    // Downmix to mono: average channels if multi-channel
    const channelCount = input.length;
    const frameCount = input[0].length;

    for (let i = 0; i < frameCount; i++) {
      let sample = 0;
      for (let ch = 0; ch < channelCount; ch++) {
        sample += input[ch][i];
      }
      sample /= channelCount;

      this.buffer[this.bufferIndex++] = sample;

      if (this.bufferIndex >= this.bufferSize) {
        // Emit chunk to port
        const chunkToSend = new Float32Array(this.buffer);
        this.port.postMessage({
          type: 'AUDIO_CHUNK',
          samples: chunkToSend,
        }, [chunkToSend.buffer]);

        this.buffer = new Float32Array(this.bufferSize);
        this.bufferIndex = 0;
      }
    }

    return true;
  }
}

registerProcessor('fluentmeet-pcm-processor', FluentMeetPcmProcessor);
