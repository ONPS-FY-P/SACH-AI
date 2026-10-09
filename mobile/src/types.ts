export type Language = 'en' | 'hi' | 'mr';
export type Source = { id: string; title: string; text: string; file: string; chunk_id: string; act_name: string; section_number: string | null; section_title: string; provision_type: string };
export type Message = { id: string; role: 'user' | 'assistant'; content: string; language?: Language; sources?: Source[] };
export type LegalSection = { source_id: string; act_name: string; section_number: string; provision_type: string; explanation: string; evidence: string; status: string };
export type Contact = { id: string; name: string; scope: string; phone: string | null; url: string; checked_on: string };
export type Guidance = { summary: string; steps: string[]; contact_ids: string[]; recording_note: string; follow_up: string };
export type ChatResponse = { answer: string; language: Language; sources: Source[]; sections: LegalSection[]; guidance: Guidance | null; contacts: Contact[]; warnings: string[]; guidance_status: 'ok' | 'unavailable' };
