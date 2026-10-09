from typing import Literal
from pydantic import BaseModel, Field, model_validator

Language = Literal['en', 'hi', 'mr']

class Message(BaseModel):
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=2500)

class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=8)
    language: Language = 'en'

    @model_validator(mode='after')
    def conversation(self):
        if self.messages[-1].role != 'user' or not self.messages[-1].content.strip():
            raise ValueError('End the conversation with a nonempty user question.')
        if sum(len(m.content) for m in self.messages) > 16000:
            raise ValueError('History is too long. Start a new chat.')
        return self

class Source(BaseModel):
    id: str
    title: str
    text: str
    file: str
    chunk_id: str
    act_name: str
    provision_type: str
    section_number: str | None = None
    section_title: str

class LegalSection(BaseModel):
    source_id: str
    act_name: str
    section_number: str
    provision_type: str
    explanation: str
    evidence: str
    status: str = 'potentially_relevant'

class Contact(BaseModel):
    id: str
    name: str
    scope: str
    phone: str | None = None
    url: str
    checked_on: str

class Guidance(BaseModel):
    summary: str
    steps: list[str]
    contact_ids: list[str]
    recording_note: str
    follow_up: str

class ChatResponse(BaseModel):
    answer: str
    language: Language
    sources: list[Source]
    sections: list[LegalSection]
    guidance: Guidance | None
    contacts: list[Contact]
    warnings: list[str]
    guidance_status: Literal['ok', 'unavailable']

# Models cannot set statute names or numbers; the server copies these from the index.
class Selection(BaseModel):
    source_id: str
    explanation: str = Field(min_length=1, max_length=600)
    evidence: str = Field(min_length=15, max_length=500)

class SelectionResult(BaseModel):
    matches: list[Selection] = Field(max_length=4)

class SearchPlan(BaseModel):
    query: str = Field(min_length=2, max_length=900)

class GuidanceResult(BaseModel):
    summary: str = Field(min_length=1, max_length=650)
    steps: list[str] = Field(min_length=1, max_length=7)
    contact_ids: list[str] = Field(max_length=4)
    recording_note: str = Field(max_length=700)
    follow_up: str = Field(max_length=350)
