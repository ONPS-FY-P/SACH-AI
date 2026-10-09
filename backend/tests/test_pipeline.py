import json
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app import pipeline, groq
from app.schemas import ChatRequest, SelectionResult, SearchPlan, GuidanceResult

CANDIDATE = dict(id='S1', title='Prevention of Corruption Act, 1988 · Section 7',
    act_name='Prevention of Corruption Act, 1988', section_number='7', section_title='Public servant being bribed',
    provision_type='section', text='Any public servant who obtains or accepts an undue advantage may be punishable.',
    file='corruption.json', chunk_id='stable-chunk', record_index=0, part=0)

def selection(id='S1', evidence='obtains or accepts an undue advantage'):
    return SelectionResult(matches=[dict(source_id=id, evidence=evidence, explanation='May be relevant to the alleged demand.')])

def test_fabricated_source_id_or_quote_is_rejected():
    assert pipeline.validate_sections(selection('S99'), [CANDIDATE]) == ([], [])
    assert pipeline.validate_sections(selection(evidence='This quotation is invented and absent.'), [CANDIDATE]) == ([], [])
    sections, sources = pipeline.validate_sections(selection(), [CANDIDATE])
    assert sections[0].section_number == '7' and sources[0].id == 'S1'

def test_unlabelled_or_repealed_reference_cannot_be_returned_as_section():
    for edit in ({'section_number': ''}, {'section_title': 'Omitted or repealed'}):
        assert not pipeline.validate_sections(selection(), [{**CANDIDATE, **edit}])[0]

@pytest.mark.parametrize('bad', ['Call 9999999999.', 'Visit https://fake.example.', 'Section 999 applies.', 'Trust [S99].', 'Call 1064.'])
def test_invented_guidance_references_rejected(bad):
    result = GuidanceResult(summary=bad, steps=['Preserve evidence.'], contact_ids=[], recording_note='', follow_up='')
    with pytest.raises(ValueError):
        pipeline.clean_guidance(result, [])

@pytest.mark.parametrize('language', ['en', 'hi', 'mr'])
async def test_full_pipeline_contract_with_mock_models(monkeypatch, language):
    async def structured(system, content, schema, **kwargs):
        if schema is SearchPlan:
            return SearchPlan(query='police bribe public servant undue advantage')
        assert pipeline.config.LANGUAGES[language] in system
        return selection()
    async def search(query):
        assert 'undue advantage' in query
        return [CANDIDATE]
    async def guidance(system, context):
        assert pipeline.config.LANGUAGES[language] in system
        assert json.loads(context)['sections'][0]['section_number'] == '7'
        return json.dumps(dict(summary='Consider contacting the relevant authority.', steps=['Preserve the original messages.'], contact_ids=['legal_aid', 'maharashtra_acb'], recording_note='Ask a lawyer before further recordings.', follow_up='Which state?'))
    monkeypatch.setattr(pipeline.ollama, 'structured', structured)
    monkeypatch.setattr(pipeline.groq, 'guidance', guidance)
    result = await pipeline.answer_chat(ChatRequest(messages=[{'role': 'user', 'content': 'A police officer asks for a bribe.'}], language=language), SimpleNamespace(collection=True, search=search))
    assert result.language == language and result.guidance_status == 'ok'
    assert result.sections[0].section_number == '7' and '[S1]' in result.answer
    assert result.contacts[0].id == 'legal_aid'
    assert 'maharashtra_acb' not in result.guidance.contact_ids

async def test_groq_failure_preserves_local_sections(monkeypatch):
    async def structured(system, content, schema, **kwargs):
        return SearchPlan(query='bribe public servant') if schema is SearchPlan else selection()
    async def search(query):
        return [CANDIDATE]
    async def failure(*args):
        raise HTTPException(503, 'Invalid key')
    monkeypatch.setattr(pipeline.ollama, 'structured', structured)
    monkeypatch.setattr(pipeline.groq, 'guidance', failure)
    response = await pipeline.answer_chat(ChatRequest(messages=[{'role': 'user', 'content': 'bribe'}]), SimpleNamespace(collection=True, search=search))
    assert response.guidance_status == 'unavailable' and len(response.sections) == 1

async def test_placeholder_key_never_sent(monkeypatch):
    monkeypatch.setattr(groq.config, 'GROQ_API_KEY', 'placeholder-IvUwH1Dq9GCScUlLm4qaNk9')
    with pytest.raises(HTTPException) as caught:
        await groq.call_groq('audio/transcriptions')
    assert caught.value.status_code == 503
