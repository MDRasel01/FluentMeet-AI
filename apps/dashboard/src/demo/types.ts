/**
 * FluentMeet AI - Dashboard Data Mode Types
 * Governs the architectural separation between Real Production Data and Isolated Demo Data.
 */

export type TabDataMode = 'REAL' | 'DEMO';

export type DashboardTabKey =
  | 'overview'
  | 'meetings'
  | 'meeting-details'
  | 'transcript-viewer'
  | 'report'
  | 'my-performance'
  | 'grammar'
  | 'vocabulary'
  | 'fluency'
  | 'pronunciation'
  | 'ielts-practice'
  | 'learning-center'
  | 'mistakes'
  | 'improvement-plan'
  | 'team-analytics';

export interface TabModeStateMap {
  [tabKey: string]: TabDataMode;
}
