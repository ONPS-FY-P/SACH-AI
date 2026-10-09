# Dataset ingestion audit

The supplied 11 raw JSON files are unchanged byte-for-byte. The loader produces **3020 chunks** using 1,200-character windows with 180-character overlap within provision boundaries. This is a parsing audit, not a live embedding run.

| Input file | Records | Chunks | Distinct numbered provisions |
|---|---:|---:|---:|
| `THE_CONSUMER_PROTECTION_ACT_2019.json` | 1 | 177 | 107 |
| `THE_ENVIRONMENT.json` | 1 | 44 | 26 |
| `THE_INFORMATION_TECHNOLOGY_ACT_2000.json` | 1 | 169 | 108 |
| `THE_JUVENILE_JUSTICE_(CARE_AND_PROTECTION_OF_CHILDREN)_ACT_2015.json` | 1 | 201 | 110 |
| `THE_PROTECTION_OF_CHILDREN_FROM_SEXUAL_OFFENCES_ACT_2012.json` | 1 | 74 | 47 |
| `THE_PROTECTION_OF_WOMEN_FROM_DOMESTIC_VIOLENCE_ACT_2005.json` | 1 | 53 | 37 |
| `The_Motor_Vehicles_Act_1988.json` | 1 | 523 | 248 |
| `a202345.json` | 1 | 536 | 358 |
| `constitution_full_dataset.json` | 715 | 965 | 493 |
| `the prevention of coruption act 1988.json` | 32 | 33 | 32 |
| `the_bharatiya_sakshya_adhiyanayam_2023.json` | 1 | 245 | 170 |

## Warnings retained in the audit

- `THE_INFORMATION_TECHNOLOGY_ACT_2000.json`: Unparsed material after section 19; no inferred section labels assigned.
- `THE_INFORMATION_TECHNOLOGY_ACT_2000.json`: Unparsed material after section 47; no inferred section labels assigned.
- `THE_INFORMATION_TECHNOLOGY_ACT_2000.json`: Unparsed material after section 52D; no inferred section labels assigned.
- `THE_INFORMATION_TECHNOLOGY_ACT_2000.json`: Unparsed material after section 55; no inferred section labels assigned.
- `The_Motor_Vehicles_Act_1988.json`: Unparsed material after section 139; no inferred section labels assigned.
- `The_Motor_Vehicles_Act_1988.json`: Unparsed material after section 190; no inferred section labels assigned.
- `The_Motor_Vehicles_Act_1988.json`: Unparsed material after section 194F; no inferred section labels assigned.

## Interpretation

Most whole-Act inputs supplied `section: "1"` for an entire Act. That field is ignored for those records; actual body headings are parsed after the enactment preamble. Ambiguous spans retain all their text as unnumbered references, preventing a guessed number from being presented as an applicable section. Preambles, contents and schedules are indexed as reference material. Duplicate exact chunks are deduplicated; no file is silently excluded.

Distinct numbered provisions means distinct identifiers found in the supplied text, including inserted identifiers and omitted provisions. It is not a claim about the current legal count of an Act or Constitution. Existing Constitution record metadata is preserved.

A separate BNSS corpus is absent. Statutory amendments, OCR completeness, source authenticity and multilingual legal meaning need review. Some supplied documents are summaries. The vector store does not correct inaccurate source text. Exact-quote/ID checks verify provenance, not semantic entailment or legal currency.

No Chroma database made with fake vectors is shipped. Run `python ingest.py` locally to produce genuine Ollama embeddings. The automated persistence test uses explicit small fixture vectors in temporary test storage only.
