import type { TranscriptionSegment } from 'livekit-client';

export interface CombinedTranscription extends TranscriptionSegment {
  role: 'assistant' | 'user';
  receivedAtMediaTimestamp: number;
  receivedAt: number;
}

export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;
}

export type ModelType = 'arcana' | 'mistv2';



export type AgentType = 'general' | 'finance' | 'legal' | 'medical' | 'tech' | 'marketing';

export interface ModelSettings {
  voice: string;
  temperature?: number;
  repetitionPenalty?: number;
  topP?: number;
  speed?: number;
}

export interface AISettings {
  model: ModelType;
  arcanaSettings: ModelSettings;
  mistv2Settings: ModelSettings;
}

export interface SandboxConfig {
  [key: string]:
  | { type: 'string'; value: string }
  | { type: 'number'; value: number }
  | { type: 'boolean'; value: boolean }
  | null;
}
