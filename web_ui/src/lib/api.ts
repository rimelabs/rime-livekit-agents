/**
 * API Client for Profile Search
 */

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SearchRequest {
  name: string;
  company?: string;
  title?: string;
  location?: string;
  session_id?: string;
}

export interface SearchResponse {
  success: boolean;
  search_id: string;
  session_id: string;
  data: any;
  report: string;
  timestamp: string;
}

export interface ChatMessage {
  session_id: string;
  message: string;
  search_id?: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  timestamp: string;
  sources?: Array<{
    type: string;
    title: string;
    url: string;
  }>;
}

export const searchProfile = async (request: SearchRequest): Promise<SearchResponse> => {
  const response = await apiClient.post('/api/search', request);
  return response.data;
};

export const sendChatMessage = async (message: ChatMessage): Promise<ChatResponse> => {
  const response = await apiClient.post('/api/chat', message);
  return response.data;
};

export const getHistory = async (sessionId: string): Promise<any> => {
  const response = await apiClient.get(`/api/history/${sessionId}`);
  return response.data;
};

export const getReport = async (searchId: string, format: string = 'markdown'): Promise<any> => {
  const response = await apiClient.get(`/api/report/${searchId}`, {
    params: { format },
  });
  return response.data;
};

export default apiClient;
