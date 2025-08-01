import type { AppConfig } from './lib/types';

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Rime',
  pageTitle: 'Rime Voice Agent',
  pageDescription: 'AI Voice Agent with Personality',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/rime-white.svg',
  accent: '#000000',
  logoDark: '/rime-black.svg',
  accentDark: '#FFFFFF',
  startButtonText: 'Start conversation',
};
