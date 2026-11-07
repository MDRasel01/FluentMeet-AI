/**
 * FluentMeet AI - Binary Audio Frame Encoder & Decoder
 * Specification: Step 05 - Section 12.1
 *
 * Framing Layout:
 * [00] Protocol Version (Uint8) - 1 byte
 * [01] Source ID (Uint8: 0=Tab, 1=Mic) - 1 byte
 * [02..05] Sequence Number (Uint32 Big-Endian) - 4 bytes
 * [06..13] Timestamp Ms (Float64 Big-Endian) - 8 bytes
 * [14..15] Sample Rate (Uint16 Big-Endian) - 2 bytes
 * [16] Channel Count (Uint8) - 1 byte
 * [17] Encoding (Uint8: 1=PCM_S16LE) - 1 byte
 * [18..21] Sample Count (Uint32 Big-Endian) - 4 bytes
 * [22] Meeting ID Length N (Uint8) - 1 byte
 * [23..23+N-1] Meeting ID String (UTF-8 bytes) - N bytes
 * [23+N..End] Raw PCM S16LE Audio Bytes
 */

import { AudioChunkMetadata, AudioChunkPayload, AudioSourceId } from '../types/audio.types';

export const PROTOCOL_VERSION = 1;
export const ENCODING_PCM_S16LE = 1;

export class AudioFrameEncoder {
  public static encode(
    metadata: AudioChunkMetadata,
    pcmData: Int16Array
  ): ArrayBuffer {
    const textEncoder = new TextEncoder();
    const meetingIdBytes = textEncoder.encode(metadata.meetingId);
    const meetingIdLength = Math.min(meetingIdBytes.length, 255);
    const headerSize = 23 + meetingIdLength;
    const pcmByteLength = pcmData.byteLength;
    const totalLength = headerSize + pcmByteLength;

    const buffer = new ArrayBuffer(totalLength);
    const view = new DataView(buffer);
    const uint8View = new Uint8Array(buffer);

    // Header fields
    view.setUint8(0, metadata.protocolVersion || PROTOCOL_VERSION);
    view.setUint8(1, metadata.sourceId);
    view.setUint32(2, metadata.sequenceNumber, false); // Big-Endian
    view.setFloat64(6, metadata.sessionRelativeTimestampMs, false);
    view.setUint16(14, metadata.sampleRate, false);
    view.setUint8(16, metadata.channels);
    view.setUint8(17, ENCODING_PCM_S16LE);
    view.setUint32(18, metadata.sampleCount, false);
    view.setUint8(22, meetingIdLength);

    // Meeting ID string
    uint8View.set(meetingIdBytes.subarray(0, meetingIdLength), 23);

    // Audio payload (S16LE)
    const pcmSourceBytes = new Uint8Array(pcmData.buffer, pcmData.byteOffset, pcmByteLength);
    uint8View.set(pcmSourceBytes, headerSize);

    return buffer;
  }

  public static decode(buffer: ArrayBuffer): AudioChunkPayload {
    if (buffer.byteLength < 23) {
      throw new Error(`Invalid binary audio frame: buffer size ${buffer.byteLength} is too small.`);
    }

    const view = new DataView(buffer);
    const uint8View = new Uint8Array(buffer);

    const protocolVersion = view.getUint8(0);
    const sourceId = view.getUint8(1) as AudioSourceId;
    const sequenceNumber = view.getUint32(2, false);
    const sessionRelativeTimestampMs = view.getFloat64(6, false);
    const sampleRate = view.getUint16(14, false);
    const channels = view.getUint8(16);
    const encoding = view.getUint8(17);
    const sampleCount = view.getUint32(18, false);
    const meetingIdLength = view.getUint8(22);

    const headerSize = 23 + meetingIdLength;
    if (buffer.byteLength < headerSize) {
      throw new Error('Frame truncated in meeting ID section.');
    }

    const textDecoder = new TextDecoder();
    const meetingId = textDecoder.decode(uint8View.subarray(23, 23 + meetingIdLength));
    const audioPayload = buffer.slice(headerSize);

    return {
      protocolVersion,
      meetingId,
      sourceId,
      sequenceNumber,
      sessionRelativeTimestampMs,
      sampleRate,
      channels,
      sampleCount,
      data: audioPayload,
    };
  }
}

