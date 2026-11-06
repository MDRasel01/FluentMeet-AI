# AI Meeting English Coach — Step 01: Product Foundation, Requirements & UI/UX Blueprint

**Product Name:** AI Meeting English Coach  
**Product Type:** Multi-Tenant SaaS Platform  
**Target Interfaces:** Chrome Extension (Manifest V3) + Web Dashboard (Next.js) + Admin Panel (Enterprise Console)  
**Document Status:** Foundation Specification (Single Source of Truth)  
**Version:** 1.0.0  
**Phase:** Step 01 Execution & Sign-off  

---

## 1. Executive Summary

**AI Meeting English Coach** is an enterprise-ready, multi-tenant AI SaaS platform designed to systematically measure, analyze, and elevate professional spoken English during real-world online meetings. Operating seamlessly across browser-based meeting clients (**Google Meet Web**, **Zoom Web**, and **Microsoft Teams Web**), the platform pairs a non-intrusive Chrome Extension with a high-performance cloud processing pipeline.

By orchestrating dual-channel audio capture, Speech-to-Text (ASR), Speaker Diarization, participant identity alignment, and language model evaluation powered by Google Gemini, the system produces actionable, evidence-backed English proficiency reports. Individual professionals receive granular feedback on **Grammar Accuracy**, **Vocabulary Nuance**, **Fluency Dynamics**, and **Pronunciation**, while enterprise managers gain aggregated communication analytics without violating participant privacy.

---

## 2. Directory Structure & Documentation Map

This documentation suite in `docs/step-01-product-foundation/` establishes the complete, authoritative engineering baseline for the entire product lifecycle (Steps 01 through 12).

```
docs/step-01-product-foundation/
├── README.md                      # Master index, documentation map, and navigation guide (This document)
├── PRD.md                         # Complete Product Requirements Document (Vision, Personas, Objectives)
├── PRODUCT_OVERVIEW.md            # Vision, Target Platforms, Core Objectives & AI Principles
├── PRODUCT_ARCHITECTURE.md        # End-to-End System Architecture, Data Flow & Mermaid Diagrams
├── USER_ROLES.md                  # RBAC, Tenant Isolation Matrix & Permission Boundaries
├── USER_JOURNEYS.md               # Comprehensive User Journeys & State Transition Maps
├── UI_UX_SPECIFICATION.md         # UI/UX Philosophy, Global Layout & Accessibility Standards
├── DESIGN_SYSTEM.md               # Design Tokens, Color Palette, Typography & 30+ Component Specs
├── PAGE_SPECIFICATIONS.md         # Detailed Blueprint for all 12 Web Dashboard Pages
├── EXTENSION_UI_SPEC.md           # Chrome Extension Side Panel (Manifest V3) 7-Screen Specification
├── ADMIN_PANEL_SPEC.md            # Super Admin & Organization Management Console Specification
├── FUNCTIONAL_REQUIREMENTS.md     # Traceable Functional Requirements (FR-001 to FR-028)
├── NON_FUNCTIONAL_REQUIREMENTS.md # Performance, Security, Scalability, Privacy & Compliance (NFR)
├── MVP_SCOPE.md                   # MVP v1.0 vs v1.1 vs v2.0 Scope Boundaries & Explicit Non-Goals
├── ACCEPTANCE_CRITERIA.md         # Verification Matrix, Gate Criteria & Step 01 Checklist
├── OPEN_DECISIONS.md              # Technical Decision Records (TDR) for Pending Architectural Choices
└── CHANGELOG.md                   # Documentation Version History & Modification Rules
```

---

## 3. Engineering Navigation Guide

To ensure rapid onboarding and zero ambiguity across specialized roles, review the documents according to the following role pathways:

| Engineering & Product Role | Recommended Reading Order | Key Deliverables to Inspect |
|---|---|---|
| **Product Manager / Lead** | `PRD.md` → `MVP_SCOPE.md` → `FUNCTIONAL_REQUIREMENTS.md` → `ACCEPTANCE_CRITERIA.md` | Core scope boundaries, Release phases, Feature requirements. |
| **UI/UX Designer** | `UI_UX_SPECIFICATION.md` → `DESIGN_SYSTEM.md` → `PAGE_SPECIFICATIONS.md` → `EXTENSION_UI_SPEC.md` | Token hierarchy, Component states, 12 Web pages, 7 Extension screens. |
| **Frontend Engineer (Web)** | `DESIGN_SYSTEM.md` → `PAGE_SPECIFICATIONS.md` → `UI_UX_SPECIFICATION.md` | Reusable React components, CSS variables, Page routing, Loading/Empty states. |
| **Extension Engineer** | `EXTENSION_UI_SPEC.md` → `PRODUCT_ARCHITECTURE.md` → `FUNCTIONAL_REQUIREMENTS.md` | Manifest V3, Side Panel API, DOM Scrapers, Audio capture, WebSocket streaming. |
| **Backend & Audio Engineer**| `PRODUCT_ARCHITECTURE.md` → `FUNCTIONAL_REQUIREMENTS.md` → `NON_FUNCTIONAL_REQUIREMENTS.md` → `OPEN_DECISIONS.md` | WebSocket audio ingestion, ASR pipeline, Diarization, Gemini AI pipeline, Postgres schema. |
| **Security & DevOps** | `NON_FUNCTIONAL_REQUIREMENTS.md` → `USER_ROLES.md` → `PRODUCT_ARCHITECTURE.md` | Multi-tenant isolation, JWT rotation, Wiretap/Consent compliance, Worker queues. |

---

## 4. Requirement Traceability Matrix Summary

All functional items are codified with permanent identifiers (`FR-001` through `FR-028`) and mapped directly to design specifications and system architecture:

```
[PRD / Business Goal] ───► [FR-001..FR-028] ───► [PAGE_SPECIFICATIONS / EXTENSION_UI_SPEC] ───► [ACCEPTANCE_CRITERIA]
                                  │
                                  ▼
                   [NON_FUNCTIONAL_REQUIREMENTS]
                                  │
                                  ▼
                        [OPEN_DECISIONS (TDR)]
```

---

## 5. Implementation Ground Rules for Coding Agents

1. **Single Source of Truth:** This directory is the immutable reference for Steps 02 through 12. No implementation may introduce features, UI elements, or database schemas that contradict these specifications.
2. **Zero Hardcoded Design Values:** All UI components in Web and Extension must strictly adhere to the tokens defined in `DESIGN_SYSTEM.md`.
3. **No Hallucinated Decisions:** Unresolved technical parameters must remain logged in `OPEN_DECISIONS.md` until formal review.
4. **Mandatory State Handling:** Every view must implement Default, Loading Skeleton, Empty State (strictly without fake/mock metrics), and Actionable Error State.
5. **Ethical AI & Consent Compliance:** In accordance with wiretapping and consent regulations, audio recording cannot occur without clear user authorization. All AI feedback must cite verifiable audio/transcript timestamps and textual evidence.

---

## 6. Step 01 Completion Status

- **Status:** **APPROVED & FINALIZED**
- **Next Phase:** **Step 02: UI/UX Design System Implementation & Component Prototyping**
- **Owner:** Senior Product Management, Architecture & UI/UX Guild

