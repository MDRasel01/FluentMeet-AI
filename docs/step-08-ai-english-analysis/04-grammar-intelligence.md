# Step 08 — Grammar Intelligence Specification

## 1. Grammatical Error Taxonomy
The Grammar Intelligence module evaluates spoken English across eight core grammatical categories:
1. **Subject-Verb Agreement**: Plural vs singular past continuous (`we was` -> `we were`), third-person singular present (`he don't` -> `he doesn't`).
2. **Verb Tense & Aspect**: Auxiliary base form consistency (`didn't went` -> `didn't go`), present perfect vs past simple usage.
3. **Preposition Collocation**: Transitive verb redundancies (`discuss about` -> `discuss`), dependent prepositions (`depend of` -> `depend on`).
4. **Articles (a / an / the)**: Generic vs definite reference, missing singular count noun determiners.
5. **Modal Verbs & Conditionals**: Real vs unreal conditionals, modal auxiliary ordering.
6. **Double Negatives**: Elimination of conversational double negative patterns (`don't have no` -> `don't have any`).
7. **Pronoun Cases**: Subject vs object pronoun confusion.
8. **Word Order & Sentence Construction**: Inversion and adverb placement.

## 2. Severity Classification
- **Major**: Severely hinders comprehension or creates immediate executive credibility friction (e.g., plural subject-verb mismatches, double negatives).
- **Moderate**: Noticeable grammatical slip that violates standard formal English rules (e.g., dependent preposition error).
- **Minor**: Stylistic or slight redundancy in spoken cadence (e.g., `discuss about`).

## 3. Deductions & Calibrated Scoring Formula
$$Score_{grammar} = \max\left(40.0, \min\left(100.0, 100.0 - \sum \text{Deductions} - 2.0 \times \text{Error Density}\right)\right)$$
where Error Density is errors per 100 spoken words.
The final score is blended 50/50 with Gemini contextual scoring.

