import { ChatResponse, Language, Message } from '../types';
export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? '').trim().replace(/\/+$/, '');
export class ApiError extends Error { constructor(message: string, public status: number) { super(message); } }
async function request<T>(path: string, body?: unknown, form?: FormData): Promise<T> {
  if (!/^https?:\/\//.test(API_URL)) throw new Error('Set EXPO_PUBLIC_API_URL in mobile/.env, then restart Expo.');
  const controller = new AbortController();
  // Three serial local CPU stages can take several minutes on an i3.
  const timer = setTimeout(() => controller.abort(), form ? 90000 : 810000);
  try {
    const response = await fetch(API_URL + path, {
      method: body || form ? 'POST' : 'GET', signal: controller.signal,
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: form ?? (body ? JSON.stringify(body) : undefined),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new ApiError(typeof payload.detail === 'string' ? payload.detail : `Request failed (${response.status}).`, response.status);
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof Error && error.name === 'AbortError') throw new Error('Request timed out. Check Ollama; local CPU processing can be slow.');
    throw new Error('Cannot reach the server. Check its address, your Wi-Fi and whether the backend is running.');
  } finally { clearTimeout(timer); }
}
export const api = {
  chat: (messages: Message[], language: Language) => request<ChatResponse>('/api/chat', {
    // Keep request content within the backend limit, preserving the latest question.
    messages: messages.slice(-6).map(({ role, content }) => ({ role, content: content.slice(0, 2500) })), language,
  }),
  transcribe: (uri: string, language: Language) => {
    const form = new FormData();
    form.append('file', { uri, name: 'question.m4a', type: 'audio/m4a' } as unknown as Blob);
    form.append('language', language);
    return request<{ text: string }>('/api/transcribe', undefined, form);
  },
};
