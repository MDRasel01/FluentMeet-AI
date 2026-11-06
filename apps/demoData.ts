/**
 * AI Meeting English Coach - High-Fidelity Demo Dataset
 * STRICT RULE: Clearly labeled sample data for UI prototyping and design verification.
 */

export interface DemoMeeting {
  id: string;
  title: string;
  platform: 'google-meet' | 'zoom' | 'teams';
  date: string;
  time: string;
  duration: string;
  durationSeconds: number;
  mySpeakingTime: string;
  mySpeakingSeconds: number;
  overallScore: number;
  status: 'completed' | 'processing' | 'failed';
  participants: { name: string; avatar?: string; color: string; speakingShare: number }[];
  summary: string[];
}

export const DEMO_MEETINGS: DemoMeeting[] = [
  {
    id: 'meet-001',
    title: 'Q4 Product Roadmap & Architecture Sync',
    platform: 'google-meet',
    date: 'Today, Nov 6',
    time: '09:30 AM',
    duration: '42 mins',
    durationSeconds: 2520,
    mySpeakingTime: '14m 12s',
    mySpeakingSeconds: 852,
    overallScore: 82,
    status: 'completed',
    participants: [
      { name: 'Priya Sharma (You)', color: '#6366F1', speakingShare: 34 },
      { name: 'Alex Miller', color: '#10B981', speakingShare: 28 },
      { name: 'David Chen', color: '#F59E0B', speakingShare: 22 },
      { name: 'Sarah Jenkins', color: '#EC4899', speakingShare: 16 },
    ],
    summary: [
      'Agreed on decoupling the real-time audio chunking engine from primary database writes.',
      'Approved Deepgram Nova-2 as the primary ASR provider for MVP milestone.',
      'Scheduled follow-up meeting on data retention policies with enterprise legal team.'
    ]
  },
  {
    id: 'meet-002',
    title: 'Weekly Engineering Sprint Retrospective',
    platform: 'google-meet',
    date: 'Yesterday, Nov 5',
    time: '03:00 PM',
    duration: '28 mins',
    durationSeconds: 1680,
    mySpeakingTime: '8m 45s',
    mySpeakingSeconds: 525,
    overallScore: 78,
    status: 'completed',
    participants: [
      { name: 'Priya Sharma (You)', color: '#6366F1', speakingShare: 31 },
      { name: 'Carlos Mendez', color: '#8B5CF6', speakingShare: 42 },
      { name: 'Elena Rostova', color: '#06B6D4', speakingShare: 27 },
    ],
    summary: [
      'Sprint delivery velocity increased by 14% after resolving WebSocket dropped frames.',
      'Identified need for better client-side IndexedDB buffer recovery.'
    ]
  },
  {
    id: 'meet-003',
    title: 'Enterprise Client Discovery: Acme Corp',
    platform: 'zoom',
    date: 'Nov 3, 2026',
    time: '11:00 AM',
    duration: '55 mins',
    durationSeconds: 3300,
    mySpeakingTime: '22m 30s',
    mySpeakingSeconds: 1350,
    overallScore: 85,
    status: 'completed',
    participants: [
      { name: 'Priya Sharma (You)', color: '#6366F1', speakingShare: 41 },
      { name: 'Michael Vance (Acme)', color: '#3B82F6', speakingShare: 38 },
      { name: 'Jessica Taylor', color: '#F97316', speakingShare: 21 },
    ],
    summary: [
      'Client requested SOC2 Type II audit report and custom 7-day ephemeral audio retention.',
      'Proposed pilot expansion for 40 engineering managers in EMEA.'
    ]
  },
  {
    id: 'meet-004',
    title: 'Bi-Weekly AI Infrastructure Standup',
    platform: 'teams',
    date: 'Oct 30, 2026',
    time: '04:15 PM',
    duration: '18 mins',
    durationSeconds: 1080,
    mySpeakingTime: '6m 10s',
    mySpeakingSeconds: 370,
    overallScore: 76,
    status: 'completed',
    participants: [
      { name: 'Priya Sharma (You)', color: '#6366F1', speakingShare: 34 },
      { name: 'Liam O’Connor', color: '#14B8A6', speakingShare: 66 },
    ],
    summary: [
      'Monitored Gemini API p95 latency spikes during peak European business hours.'
    ]
  }
];

export const DEMO_TRANSCRIPT_SEGMENTS = [
  {
    id: 'seg-1',
    speakerName: 'Priya Sharma (You)',
    speakerColor: '#6366F1',
    timestamp: '00:04:12',
    timestampSeconds: 252,
    text: 'Good morning everyone. I want to explain you how the new audio ingestion pipeline handles transient network disconnects.',
    mistakes: [
      {
        id: 'm-1',
        original: 'explain you',
        corrected: 'explain to you',
        explanation: 'The verb "explain" requires the preposition "to" before the indirect object pronoun.',
        type: 'grammar' as const
      }
    ]
  },
  {
    id: 'seg-2',
    speakerName: 'Alex Miller',
    speakerColor: '#10B981',
    timestamp: '00:04:35',
    timestampSeconds: 275,
    text: 'Thanks Priya. Are we buffering chunks in local browser storage if the WebSocket server drops momentarily?',
    mistakes: []
  },
  {
    id: 'seg-3',
    speakerName: 'Priya Sharma (You)',
    speakerColor: '#6366F1',
    timestamp: '00:04:52',
    timestampSeconds: 292,
    text: 'Yes exactly. We discussed about this yesterday. The offscreen document stores up to sixty seconds of linear PCM in IndexedDB, so we will not loose any frames.',
    mistakes: [
      {
        id: 'm-2',
        original: 'discussed about',
        corrected: 'discussed',
        explanation: '"Discuss" is a transitive verb that takes a direct object without the preposition "about".',
        type: 'grammar' as const
      },
      {
        id: 'm-3',
        original: 'loose',
        corrected: 'lose',
        explanation: '"Loose" is an adjective meaning not tight; the verb meaning to misplace or suffer loss is "lose".',
        type: 'vocabulary' as const
      }
    ]
  },
  {
    id: 'seg-4',
    speakerName: 'David Chen',
    speakerColor: '#F59E0B',
    timestamp: '00:05:30',
    timestampSeconds: 330,
    text: 'That sounds very robust. What about speaker diarization confidence when two people talk at the exact same moment?',
    mistakes: []
  },
  {
    id: 'seg-5',
    speakerName: 'Priya Sharma (You)',
    speakerColor: '#6366F1',
    timestamp: '00:05:48',
    timestampSeconds: 348,
    text: 'If confidence drops below seventy-five percent, we fall back to labeling the utterance as Unknown Speaker rather than guessing the wrong person.',
    mistakes: []
  }
];

export const DEMO_MISTAKES = [
  {
    id: 'dm-1',
    original: 'I want to explain you the new pipeline.',
    corrected: 'I want to explain to you the new pipeline.',
    category: 'Preposition Omission',
    severity: 'medium' as const,
    explanation: 'With "explain", the person being addressed must be preceded by "to" (e.g., "explain to someone", never "explain someone").',
    timestamp: '00:04:12'
  },
  {
    id: 'dm-2',
    original: 'We discussed about this topic yesterday.',
    corrected: 'We discussed this topic yesterday.',
    category: 'Redundant Preposition',
    severity: 'low' as const,
    explanation: '"Discuss" already means "to talk about". Adding "about" is redundant in professional business English.',
    timestamp: '00:04:52'
  },
  {
    id: 'dm-3',
    original: 'If I will have time tomorrow, I will review the PR.',
    corrected: 'If I have time tomorrow, I will review the PR.',
    category: 'First Conditional Tense',
    severity: 'high' as const,
    explanation: 'In the conditional "if" clause referring to the future, use the present simple ("if I have"), not "will".',
    timestamp: '00:12:35'
  },
  {
    id: 'dm-4',
    original: 'Everyone in the team have submitted their updates.',
    corrected: 'Everyone in the team has submitted their updates.',
    category: 'Subject-Verb Agreement',
    severity: 'medium' as const,
    explanation: 'Indefinite pronouns like "everyone", "everybody", and "each" take singular verbs ("has", not "have").',
    timestamp: '00:18:14'
  }
];

export const DEMO_VOCABULARY_SUGGESTIONS = [
  {
    original: 'very good',
    suggested: 'highly effective / robust',
    context: 'Architecture description',
    example: 'Instead of "a very good solution", use "a robust architectural solution".'
  },
  {
    original: 'big problem',
    suggested: 'critical bottleneck / impediment',
    context: 'Sprint blocker',
    example: 'Instead of "we have a big problem", use "we encountered a critical impediment".'
  },
  {
    original: 'make it faster',
    suggested: 'optimize / accelerate execution',
    context: 'Performance optimization',
    example: 'Instead of "we must make it faster", use "we must optimize query execution".'
  }
];

export const DEMO_TEAM_ANALYTICS = {
  totalTeamMeetings: 48,
  totalSpeakingHours: '34h 15m',
  averageSpeakingPace: 142, // WPM
  averageFillerDensity: 3.8, // %
  topMistakeCategories: [
    { category: 'Prepositions', count: 42, percentage: 38 },
    { category: 'Conditional Tenses', count: 28, percentage: 25 },
    { category: 'Subject-Verb Agreement', count: 22, percentage: 20 },
    { category: 'Article Usage (a/an/the)', count: 19, percentage: 17 },
  ],
  members: [
    { name: 'Priya Sharma', role: 'Senior Engineer', meetings: 12, pace: 144, fillerRate: '3.2%', score: 82 },
    { name: 'Carlos Mendez', role: 'Staff Engineer', meetings: 10, pace: 138, fillerRate: '4.1%', score: 79 },
    { name: 'Elena Rostova', role: 'Frontend Lead', meetings: 14, pace: 148, fillerRate: '2.9%', score: 86 },
    { name: 'David Chen', role: 'Backend Engineer', meetings: 12, pace: 136, fillerRate: '4.8%', score: 75 },
  ]
};

export const DEMO_ADMIN_DATA = {
  totalUsers: 1420,
  totalOrganizations: 84,
  activeSubscriptions: 78,
  audioMinutesProcessed: 148520,
  aiTokenConsumption: '124.6M',
  estimatedApiCost: '$642.80',
  workerQueueBacklog: 3,
  processingFailureRate: '0.18%',
  systemHealth: {
    apiGateway: 'Healthy (24ms p95)',
    webSocketServer: 'Healthy (1,240 active)',
    redisCluster: 'Healthy (42% memory)',
    postgresPool: 'Healthy (18/100 connections)',
    workerPool: 'Healthy (12/16 workers active)'
  },
  recentAuditLogs: [
    { id: 'log-1', action: 'TENANT_SEAT_EXPANSION', actor: 'sarah.j@acme.com', target: 'Acme Corp (25 -> 40 seats)', time: '12 mins ago' },
    { id: 'log-2', action: 'AUDIO_AUTO_PURGE', actor: 'System Janitor', target: '412 audio files older than 7 days purged', time: '1 hour ago' },
    { id: 'log-3', action: 'USER_ROLE_UPDATED', actor: 'superadmin@meetingcoach.ai', target: 'Carlos Mendez -> Team Manager', time: '3 hours ago' },
  ]
};

