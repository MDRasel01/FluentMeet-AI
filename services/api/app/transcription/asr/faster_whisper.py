"""
FluentMeet AI - Faster-Whisper ASR Provider
Specification: Step 07 - Section 4 (Speech-to-Text Pipeline)
"""

import io
import math
import logging
from typing import Optional, List, Any
import numpy as np
from app.transcription.asr.base import BaseASRProvider, ASRResult, ASRSegment, ASRWord

logger = logging.getLogger("transcription.asr")

class FasterWhisperASRProvider(BaseASRProvider):
    def __init__(
        self,
        model_size_or_path: str = "base.en",
        device: str = "cpu",
        compute_type: str = "int8",
        model_instance: Optional[Any] = None
    ):
        self.model_size_or_path = model_size_or_path
        self.device = device
        self.compute_type = compute_type
        self._model = model_instance

    def _get_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(f"Loading faster-whisper model: {self.model_size_or_path} on {self.device} ({self.compute_type})")
                self._model = WhisperModel(
                    self.model_size_or_path,
                    device=self.device,
                    compute_type=self.compute_type
                )
            except Exception as e:
                logger.error(f"Failed to load faster-whisper model: {e}")
                raise e
        return self._model

    def transcribe(
        self,
        pcm_bytes: bytes,
        sample_rate: int = 16000,
        language: str = "en"
    ) -> ASRResult:
        if not pcm_bytes:
            return ASRResult(text="", language=language, segments=[], confidence=None)

        # Convert Int16 PCM bytes to Float32 NumPy array normalized to [-1.0, 1.0]
        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        model = self._get_model()

        # Execute transcription with word-level timestamps
        segments_gen, info = model.transcribe(
            samples,
            beam_size=5,
            language=language,
            word_timestamps=True,
            vad_filter=False,  # Step 07 handles VAD explicitly in pipeline
        )

        all_segments: List[ASRSegment] = []
        full_text_parts: List[str] = []

        for seg in segments_gen:
            words: List[ASRWord] = []
            if hasattr(seg, "words") and seg.words:
                for w in seg.words:
                    conf = getattr(w, "probability", None)
                    if conf is not None:
                        conf = round(float(conf), 4)
                    words.append(ASRWord(
                        word=w.word.strip(),
                        start_ms=int(round(w.start * 1000.0)),
                        end_ms=int(round(w.end * 1000.0)),
                        confidence=conf
                    ))

            # Calibrate segment confidence from avg_logprob
            seg_conf = None
            if hasattr(seg, "avg_logprob") and seg.avg_logprob is not None:
                try:
                    seg_conf = round(float(math.exp(seg.avg_logprob)), 4)
                    seg_conf = min(1.0, max(0.0, seg_conf))
                except OverflowError:
                    seg_conf = None

            cleaned_text = seg.text.strip()
            if cleaned_text:
                full_text_parts.append(cleaned_text)

            all_segments.append(ASRSegment(
                start_ms=int(round(seg.start * 1000.0)),
                end_ms=int(round(seg.end * 1000.0)),
                text=cleaned_text,
                confidence=seg_conf,
                words=words
            ))

        full_text = " ".join(full_text_parts)
        overall_conf = None
        confs = [s.confidence for s in all_segments if s.confidence is not None]
        if confs:
            overall_conf = round(float(np.mean(confs)), 4)

        detected_lang = getattr(info, "language", language) or language

        return ASRResult(
            text=full_text,
            language=detected_lang,
            segments=all_segments,
            confidence=overall_conf
        )

