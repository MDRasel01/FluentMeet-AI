# Product Requirements Document (PRD)

**Project Title:** AI Meeting English Coach  
**Document ID:** PRD-V1.0-FOUNDATION  
**Product Category:** AI-Powered Multi-Tenant B2B/B2C SaaS  
**Version:** 1.0.0  
**Phase:** Step 01 — Product Planning & Requirement Finalization  

---

## 1. Executive Summary

In today's globalized, remote-first economy, English is the default lingua franca of cross-border business, technology, and engineering. Hundreds of millions of non-native English-speaking knowledge workers participate daily in virtual meetings on platforms such as Google Meet, Zoom, and Microsoft Teams. While these professionals possess deep domain expertise, many experience persistent anxiety, self-doubt, grammatical hesitations, limited vocabulary, and pronunciation barriers that undermine their perceived authority, collaboration velocity, and career growth.

Traditional language learning applications (e.g., Duolingo, grammar workbooks, generic ESL tutors) are disconnected from real-world work contexts. They test generic phrases rather than evaluating how individuals communicate under the cognitive pressure of actual business meetings.

**AI Meeting English Coach** bridges this critical gap. It is an ambient, intelligent, multi-tenant SaaS platform that captures meeting audio via a browser-based Chrome Extension, isolates individual speakers using diarization, and delivers automated, highly contextual, evidence-backed English coaching reports post-meeting. It empowers individual professionals to track their spoken progress over time and equips enterprise managers with aggregated communication insights while strictly safeguarding employee privacy.

---

## 2. Problem Statement & Market Opportunity

### 2.1 The Individual Professional's Dilemma
- **In-the-Moment Blindness:** During high-stakes meetings, participants cannot objectively track their own grammar blunders, repetitive filler words, or awkward idioms while attempting to explain complex technical or business ideas.
- **Lack of Actionable Feedback:** Colleague feedback is rarely provided due to politeness or social awkwardness. Individuals continue making the same recurring mistakes for years without realizing it.
- **Fragmented Learning:** Generic language apps teach vocabulary in isolation, with no correlation to real professional discourse (e.g., negotiating deadlines, presenting architecture, handling pushback).

### 2.2 The Enterprise Team Challenge
- **Global Team Misalignment:** Subtle misunderstandings caused by imprecise grammar, unclear pronunciation, or vague expressions cause engineering rework, missed sprint goals, and client friction.
- **L&D Spend Inefficiency:** Organizations spend billions on generic corporate English training seminars that show negligible measurable return on investment because training is divorced from actual meeting performance.
- **Privacy & Psychological Safety Concerns:** Employees fear punitive surveillance; managers need aggregate communication capability benchmarking without invasive snooping into private conversations.

---

## 3. Product Vision & Value Proposition

### 3.1 Vision Statement
To become the world's most trusted, non-intrusive AI communication coach for international knowledge workers—transforming everyday meetings into frictionless, high-impact language learning experiences.

### 3.2 Value Propositions

| Stakeholder | Core Value Proposition |
|---|---|
| **Individual Users** | "Turn every work meeting into an objective, private, AI-powered English coaching session without spending hours on homework." |
| **Team Managers** | "Accelerate cross-border team delivery velocity by identifying communication bottlenecks and coaching needs without micromanaging." |
| **Enterprise Admins** | "Equip global talent with high-impact, measurable English development while maintaining strict enterprise compliance and data isolation." |

---

## 4. Key Performance Indicators (KPIs) & Success Metrics

| Dimension | Metric | MVP Target (v1.0) | v1.1 / Year 1 Target |
|---|---|---|---|
| **Adoption & Usage** | Extension Weekly Active Users (WAU) | 60% of registered users | 75% WAU |
| **Engagement** | Post-Meeting Report Review Rate | > 70% within 2 hours of meeting | > 85% within 1 hour |
| **Coaching Efficacy** | Repeat Mistake Reduction | 15% reduction in recurring grammar mistakes over 30 days | 35% reduction over 60 days |
| **Processing Reliability**| End-to-End Pipeline Success Rate | > 98.5% of sessions without error | > 99.8% SLA |
| **Processing Latency** | Report Generation Turnaround | < 3x meeting duration (e.g., < 9 mins for 30m meeting) | < 1x meeting duration (or real-time) |
| **AI Accuracy** | User Feedback Disagreement Rate | < 5% mistake corrections flagged as inaccurate | < 2% flagged |

---

## 5. Target Personas

### 5.1 Persona 1: Priya Sharma — Senior Software Engineer (Individual User)
- **Background:** Non-native speaker, works for a US-based enterprise from Bangalore.
- **Pain Point:** Frequently uses incorrect prepositions, struggles with past vs. present perfect tense under pressure, and worries that native colleagues perceive her as less confident.
- **Goal:** Receive private, bite-sized, non-judgmental reports highlighting exact phrases she spoke and how to rephrase them natively.

### 5.2 Persona 2: Carlos Mendez — Engineering Team Lead (Team Member / Manager)
- **Background:** Leads a distributed team of 8 engineers across Latin America and Europe.
- **Pain Point:** Noticeable team misunderstandings during sprint planning. Does not want to embarrass his team members by pointing out language flaws in public.
- **Goal:** View aggregate team communication trends (e.g., top 5 recurring grammatical bottlenecks) to schedule relevant targeted group workshops.

### 5.3 Persona 3: Sarah Jenkins — VP of People & L&D (Organization Admin)
- **Background:** Oversees workforce development for a 500-person global SaaS company.
- **Pain Point:** No quantitative metric to measure if corporate English training initiatives are actually improving spoken workplace communication.
- **Goal:** Standardize a company-wide tool with strict privacy controls, seat management, and usage metering.

---

## 6. System Architecture & High-Level Interfaces

The platform comprises three deeply integrated interfaces:

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│  ┌─────────────────────────┐   ┌─────────────────────────┐  │
│  │     Chrome Extension    │   │      Web Dashboard      │  │
│  │ (Manifest V3 SidePanel) │   │    (Next.js App Router) │  │
│  └───────────┬─────────────┘   └────────────┬────────────┘  │
│              │                              │               │
│              │ WebSockets (Audio Chunks)     │ HTTPS / REST  │
└──────────────┼──────────────────────────────┼───────────────┘
               ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway & Core                      │
│  FastAPI (Python) • JWT Auth • RBAC • Multi-Tenant Routing  │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Asynchronous Processing Queue               │
│                   Redis Streams / Celery                    │
└──────┬───────────────────────┬───────────────────────┬──────┘
       ▼                       ▼                       ▼
┌──────────────┐        ┌──────────────┐        ┌─────────────┐
│  Audio & ASR │        │  Diarization │        │  Gemini AI  │
│ Dual-Stream  │───────►│  Speaker ID  │───────►│  Analysis   │
│ Processing   │        │   & Mapping  │        │   Engine    │
└──────────────┘        └──────────────┘        └─────────────┘
                                                       │
                                                       ▼
                                            ┌─────────────────────┐
                                            │ Multi-Tenant Store  │
                                            │ Postgres + S3/MinIO │
                                            └─────────────────────┘
```

1. **Chrome Extension (Manifest V3):** Embedded in the browser side panel. Automatically detects active meeting URLs, discovers participants from DOM structures, prompts for recording consent, captures dual-channel audio (tab and mic), and streams binary audio chunks over secure WebSockets.
2. **Web Dashboard (Next.js / Tailwind CSS):** The central hub for meeting history, interactive transcript playback, multi-dimensional English analytics (Grammar, Vocabulary, Fluency, Pronunciation, IELTS benchmarks), and customized daily practice.
3. **Admin Panel:** Administrative console for super-admins and organization managers to manage tenants, seat allocations, billing, AI token consumption, worker queue health, and data audit logs.

---

## 7. Core Product Pillars & Capabilities

### 7.1 Pillar 1: Passive, Privacy-Centric Audio Ingestion
- In-browser capture eliminates the need for annoying meeting bots or unauthorized room joins.
- Strict visual consent confirmation required prior to initiating any capture.
- Ephemeral audio processing options with configurable data retention policies (7, 30, or 90 days, or immediate deletion post-analysis).

### 7.2 Pillar 2: High-Fidelity Diarization & Speaker Matching
- Dual-track capture: Local user microphone is separated from incoming remote meeting audio (tab stream).
- Intelligent speaker clustering maps remote speech segments to detected participant identities.
- Explicit low-confidence fallback: Unmatched audio is tagged as "Unknown Speaker" rather than guessing identities.

### 7.3 Pillar 3: Multi-Dimensional English Evaluation
- **Grammar & Syntax:** Identifies tense consistency errors, subject-verb mismatches, incorrect prepositions, and awkward sentence constructions.
- **Lexical Resource:** Flags repetitive words, informal jargon in executive settings, and suggests precise idioms and business vocabulary.
- **Fluency & Temporal Dynamics:** Tracks Words Per Minute (WPM), speech-to-pause ratios, filler word frequencies ("um", "uh", "you know"), and run-on sentences.
- **Pronunciation & Articulation:** Audits acoustic phoneme fidelity (on supported engines) or flags commonly mispronounced professional terms with phonetic IPA guides.

### 7.4 Pillar 4: Long-Term Behavioral Reinforcement
- Mistake aggregation engine highlights recurring patterns across weeks and months.
- Daily 3-minute personalized practice drills generated directly from real meeting mistakes.

---

## 8. Release Strategy & Phased Rollout

- **Phase 1: MVP (v1.0):** Browser-based Google Meet capture, dual audio streaming, ASR + Diarization, core Grammar + Vocabulary + Basic Fluency analysis via Gemini API, Web Dashboard with meeting viewer and individual reports.
- **Phase 2: Version 1.1:** Zoom Web & Teams Web deep support, Advanced Pronunciation acoustic analysis, Team Analytics, IELTS-style speaking benchmarking, automated daily practice drills.
- **Phase 3: Version 2.0 (Future):** Desktop Native companion app (electron-based for native Zoom/Teams desktop clients), live real-time whisper prompts, and corporate LMS integration.

---

## 9. Regulatory & Ethical Compliance Mandates

- **Two-Party Wiretapping Compliance:** The platform strictly enforces that the user asserts consent from all participants before recording begins.
- **Zero Hallucination / Evidence Requirement:** No linguistic flaw may be flagged without attaching the exact transcript snippet, timestamp, and acoustic backing.
- **Anti-Bias Policy:** Regional accents (e.g., Indian, Latin American, East Asian, Scottish) must never be penalized as grammatical or lexical errors unless intelligibility is demonstrably compromised.

