import type { AppConfig } from './lib/types';

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Rime',
  pageTitle: 'Rime Voice Agent',
  pageDescription: 'AI Voice Agent with Personality',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/rime-black.svg',
  accent: '#000000',
  logoDark: '/rime-white.svg',
  accentDark: '#FFFFFF',
  startButtonText: 'Start conversation',
};