# FluentMeet AI — AI Meeting English Coach

[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19.0-61dafb.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-6.1-646cff.svg)](https://vitejs.dev/)
[![Manifest V3](https://img.shields.io/badge/Chrome_Extension-Manifest_V3-green.svg)](https://developer.chrome.com/docs/extensions/mv3/)

> **FluentMeet AI** (formerly *AI Meeting English Coach*) is an enterprise-grade, multi-tenant AI SaaS platform that analyzes spoken English during virtual meetings and delivers deeply personalized, actionable feedback to accelerate language proficiency in professional workplace environments.

Operating unobtrusively via a modern Chrome Extension (Manifest V3 Side Panel API), FluentMeet AI captures meeting audio across **Google Meet Web**, **Zoom Web Client**, and **Microsoft Teams Web**, isolates individual speakers through diarization, and feeds multi-track audio to Google Gemini and specialized acoustic models for multi-dimensional linguistic evaluation.

---

## 🌟 Key Highlights & Current Milestones

- **Step 01: Product Foundation & Specifications (Completed)**
  - 17 comprehensive specification documents detailing PRD, system architecture, RBAC, 8 user journeys, functional requirements (FR-001 to FR-028), non-functional standards (NFR-001 to NFR-024), and technical decision records.
- **Step 02: High-Fidelity UI/UX Design System (Completed)**
  - **49 / 49 Screens Implemented & Verified (100%)**
  - Centralized design tokens (colors, typography, 4px spacing, radii, shadows, breakpoints).
  - 30+ reusable atomic components (`Button`, `Input`, `Card`, `AudioPlayer`, `TranscriptSegment`, `GrammarErrorCard`, `ScoreIndicator`, `Modal`, etc.).
  - Complete Light & Dark Theme implementations.
  - Multi-device responsive validation (320px to 1600px+).

---

## 🖥️ The Three Core Interfaces (49 Screens Total)

### 1. Web Dashboard (21 Screens)
- **Workspace:** Dashboard Overview, All Meetings Archive, Meeting Details, Interactive Transcript Viewer (with audio scrubber sync).
- **My English:** Individual Coaching Report, Longitudinal Performance Trajectory, Grammar Analysis, Vocabulary Upgrades, Fluency Dynamics (WPM & Fillers), Pronunciation Spectrograms, IELTS Speaking Benchmarking.
- **Learning:** Personalized Learning Center (3-minute adaptive drills), Mistake History Flashcard Bank, 4-Week Mastery Plan.
- **Organization:** Scoped Team Analytics & Widespread Bottleneck Distribution.
- **Settings:** Integrations, Billing & Usage Metering, Profile, Privacy & Ephemeral Audio Retention, Security, and Notifications.

### 2. Chrome Extension (15 Screens)
- Operates in the browser side panel (360–400px width) without obstructing video calls.
- Authentication, Home/Ready, Meeting Detected, Participant List, Two-Party Consent Confirmation, Live Session with Dual VU Signal Meters, Paused Session, Processing, Completed, and 5 Actionable Error Recovery States.

### 3. Super Admin Operations Console (13 Screens)
- Platform Health Overview, User Directory, User Inspection Drawer, Multi-Tenant Organization Management, Subscription Health, Plan Tier Management, Google Gemini Token Economics & Cost Auditing, Asynchronous Task Queue Telemetry, System Health, Error Stream, and SOC2/GDPR Audit Trails.

---

## 📁 Repository Structure

```text
FluentMeet-AI/
├── apps/
│   ├── dashboard/                 # Web Dashboard application (21 screens)
│   ├── extension/                 # Chrome Side Panel extension UI (15 screens)
│   ├── admin/                     # Super Admin console (13 screens)
│   └── demoData.ts                # Transparent prototype dataset
├── design-system/
│   ├── tokens/                    # Colors, typography, spacing, radius, shadows, breakpoints
│   ├── themes/                    # Light and Dark theme configurations
│   ├── components/                # 30+ Reusable atomic UI components
│   └── layouts/                   # Shell layouts
├── docs/
│   ├── step-01-product-foundation/# 17 Architectural specification documents
│   └── step-02-ui-ux/             # 17 Design system & QA specification documents
├── src/
│   ├── App.tsx                    # Master Interactive Workbench & Viewport Resizer
│   ├── main.tsx                   # React 19 entry point
│   └── index.css                  # CSS custom properties & Tailwind entry
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js `v20+` or `v24+`
- npm `v10+`

### Installation
```bash
# Clone the repository
git clone https://github.com/MDRasel01/FluentMeet-AI.git
cd FluentMeet-AI

# Install dependencies
npm install
```

### Running the Interactive Workbench
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser. Use the top workbench bar to:
- Switch between **Web Dashboard**, **Chrome Extension**, **Admin Panel**, and **Design System Showcase**.
- Test responsiveness across **320px, 375px, 430px, 768px, 1024px, 1280px, 1440px**, and fluid widths.
- Toggle between **Light Theme** and **Dark Theme** instantly.

### Production Typecheck & Build
```bash
npm run build
```

---

## 🗺️ Roadmap & Engineering Phases

- [x] **Step 01:** Product Foundation, Requirements & Blueprint
- [x] **Step 02:** UI/UX Design & Complete Design System (49 Screens)
- [ ] **Step 03:** Project Setup & Infrastructure (Monorepo, Next.js 15, FastAPI, Postgres, Redis)
- [ ] **Step 04:** SaaS Authentication & Multi-Tenant User Management
- [ ] **Step 05:** Chrome Extension Development (Manifest V3 Side Panel & DOM Scrapers)
- [ ] **Step 06:** Audio Capture & Real-Time Streaming Engine
- [ ] **Step 07:** Speech-to-Text (ASR) & Speaker Diarization Pipeline
- [ ] **Step 08:** AI Language Analysis Engine (Google Gemini API & Structured Pydantic)
- [ ] **Step 09:** Acoustic Pronunciation & IELTS Evaluation Engine
- [ ] **Step 10:** Report Generation & Dashboard Integration
- [ ] **Step 11:** Testing, Security Audits & Optimization
- [ ] **Step 12:** Production Deployment & Global SaaS Launch

---

## 📄 License & Intellectual Property

Copyright © 2026 Md Rasel Islam. All rights reserved.
Developed as a proprietary Multi-Tenant SaaS platform.
