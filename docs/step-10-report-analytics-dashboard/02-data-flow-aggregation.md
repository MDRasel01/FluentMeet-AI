# Step 10 — Multi-Source Data Flow & Aggregation Specification

**Module:** Multi-Source Data Aggregation  
**Component:** `app.reports.collector.ReportDataCollector`  

---

## 1. Upstream Data Sources

The Step 10 collector extracts and harmonizes outputs across four distinct pipelines:

| Stage | Data Source | Primary Entities Extracted |
|---|---|---|
| **Step 06: Audio** | `AudioStream`, `AudioSegment` | Audio duration, channel classification, SNR/signal quality |
| **Step 07: Transcript** | `MeetingSpeaker`, `TranscriptSegment`, `TranscriptWord` | Diarized speaker labels, word counts, active speaking duration, timestamps |
| **Step 08: English Analysis** | `AnalysisSession`, `ParticipantAnalysis`, `AnalysisCategoryScore`, `GrammarIssue`, `VocabularyInsight`, `FluencyMetric`, `ImprovementRecommendation` | Grammatical accuracy, vocabulary range, fluency metrics, WPM, filler word frequency |
| **Step 09: Pronunciation** | `PronunciationAssessment`, `PronunciationWordResult`, `PronunciationProsodyResult`, `IELTSSpeakingPracticeAssessment`, `PronunciationRecommendation` | Acoustic word accuracy, phoneme substitutions, prosody, intonation, IELTS practice estimates |

## 2. Ingestion & Alignment Algorithm

1. **Speaker Registry Construction:**
   - Queries `MeetingSpeaker` records and extracts `speaker_label` (`speaker_0`, `speaker_alice`, etc.).
   - Matches speakers with registered `MeetingParticipant` instances if present.
2. **Transcript Processing:**
   - Filters `TranscriptSegment` items by meeting ID.
   - Computes total spoken words and duration in seconds per speaker.
3. **Step 08 Linguistic Merging:**
   - Identifies completed `AnalysisSession` records.
   - Extracts category scores (`Grammar`, `Vocabulary`, `Fluency`).
   - Normalizes grammar issues into actionable correction models.
4. **Step 09 Acoustic Merging:**
   - Identifies completed `PronunciationAssessment` records.
   - Extracts acoustic scores, mispronounced phonemes, prosodic pitch contours, and IELTS practice estimates.
5. **Output Structure:**
   - Packages all data into an aligned, in-memory `CollectedParticipantData` map keyed by `speaker_label`.
