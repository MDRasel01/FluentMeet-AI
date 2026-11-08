# Step 08 — Communication Intelligence Specification

## 1. Objectives & Qualitative Dimensions
Beyond lexical and grammatical correctness, professional English impact depends on conversational effectiveness:
1. **Active Listening Indicators**: Explicit verbal markers showing engagement with previous speakers (e.g., `building on what Alex noted`, `to clarify your point`, `I agree with that assessment`).
2. **Consultative Diplomacy**: Diplomatic phrasing and polite disagreement structures (e.g., `perhaps we could explore`, `from our perspective`, `would it be feasible`).
3. **Response Relevance**: Staying on topic vs tangential rambling.
4. **Conversational Turn Management**: Yielding turns smoothly without interrupting or monopolizing dialogue.

## 2. Multi-Turn Pattern Discovery
The `SpeakingPatternAnalyzer` synthesizes observations across an entire meeting:
- Identifies sentence starter habits (e.g., speaker initiating 5+ sentences with `Basically` or `So yeah`).
- Correlates speaking time proportion to topic transitions.
- Generates holistic communication insights stored in `communication_insights`.

