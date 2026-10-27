# Writing the glossary definitions

Hover Glossary shows a short pop-up definition when you hover a hard medical term on an
Anki card (AnKing Step 1/2 deck + in-house NJMS cards). This file is the brief for turning
`data/candidates/batch_NNN.jsonl` into `data/defs/batch_NNN.jsonl`.

The reader is a first- or second-year medical student. Terms and wording sit at a
**college reading level or above**. Never define what any college graduate already knows.

## Input

One JSON object per line:

| field | meaning |
|---|---|
| `id` | candidate number; echo it back |
| `kind` | `mesh` (MeSH heading), `eponym`, `word` (a word from AnKing not in MeSH), `abbr` (an abbreviation) |
| `name` | MeSH heading, eponym phrase, word, or abbreviation |
| `scope` | MeSH's official definition (mesh only); for grounding, never copied |
| `seen_as` | how the term actually appears on cards (lowercased) |
| `notes` | how many AnKing notes contain it |
| `ctx` | 1-2 snippets of real card text showing it in use |

## Output

Exactly one JSON line per input line, same order, in `data/defs/batch_NNN.jsonl`.

A kept term:

```json
{"id": 1234, "term": "Holoprosencephaly", "def": "The forebrain fails to split into left and right halves early in development, causing midline face defects (single central incisor, close-set eyes, cleft lip; cyclopia when severe). Linked to Sonic hedgehog mutations, trisomy 13 and fetal alcohol exposure.", "syn": [], "abbr": ["HPE"]}
```

A skipped term:

```json
{"id": 1235, "skip": "obvious"}
```

Skip reasons:
- `obvious`: a college graduate knows it.
- `not-medical`: ordinary English, attribution or boilerplate ("wikimedia", "licensed", "openstax"), or names of people or places that aren't part of a medical eponym.
- `wrong-sense`: the MeSH heading doesn't match how the word is used on cards ("will" → Volition, "lead" → the metal when cards mean ECG leads).
- `fragment`: a broken or truncated word ("ystonia", "epatocellular").
- `ambiguous`: an abbreviation with several common meanings on these cards and no dominant one.

## What to keep

Keep a term when a smart college graduate with no medical training would have to look it
up, or would likely misunderstand it.

- **Skip:** hives, fever, cancer, kidney, heart, aspirin, insulin, vaccine, pregnancy,
  blood pressure, stroke, asthma, allergy, bacteria, virus, cells, diagnosis, treatment,
  x-ray.
- **Keep:** urticaria, pyrexia, holoprosencephaly, myocardial infarction, koilonychia,
  dysdiadochokinesia, pseudopalisading, Janeway lesions, Chvostek sign, edrophonium,
  sirolimus, kernicterus, steatorrhea, hemozoin, osteophyte, iridocyclitis, keloid, SIADH,
  G6PD, ARDS, DIC.
- Drugs: keep every drug that isn't a household name (keep "neostigmine", "carbidopa";
  skip "aspirin", "ibuprofen", "penicillin").
- Broad categories whose meaning is plain from the words ("gastrointestinal diseases",
  "recombinant proteins", "chronic pain"): skip as `obvious`.
- Bugs, genes, enzymes, signs, histology findings, lab tests, syndromes, eponyms: keep.
- `word` candidates are mostly noise. Keep only real medical vocabulary.

## How to write the definition

- **1-3 sentences, about 20-45 words**, hard cap 60.
- Open by saying plainly what it is: "Spoon-shaped nails…", "A short-acting drug that
  blocks acetylcholinesterase…". Don't open with the term itself or "A term for".
- Then add the **single most useful association**: the classic cause, the disease it
  signals, the mechanism, or the gene. Use First Aid / Boards & Beyond level facts, not
  obscure trivia.
- Explain jargon instead of stacking more jargon.
- Accuracy above all. If you aren't sure of a fact, leave it out. Never invent.
- American spelling. Plain text only: no markdown, HTML or emoji. No mnemonics or exam
  tips.
- MeSH `scope` is for grounding; rewrite it, never copy it.

## `term`, `syn`, `abbr`

- `term`: the name students use, in normal word order and sentence case ("Disseminated
  intravascular coagulation", not "Coagulation, Disseminated Intravascular"). Eponyms keep
  their capitals ("Kayser-Fleischer rings").
- `syn`: other names and spellings that appear on cards and **only** mean this thing:
  the correct `seen_as` forms, plural and possessive variants ("Chvostek's sign"). Never a
  form that usually means something else on cards, never an ordinary English word.
  **Never a lay/plain-English form** ("blood clot", "shortness of breath", "heart attack",
  "hives"): the pop-up must only appear on the technical word, never on words a college
  graduate already knows. Never a single word that has everyday senses ("sensitivity",
  "lead", "culture").
- One concept per entry. Don't fold distinct terms into an umbrella entry (stridor,
  wheezing and crackles each get their own entry if they are candidates; otherwise leave
  them out). Don't add synonyms that are only related, not the same thing (Addison disease
  is not a synonym of adrenal insufficiency).
- Use the `id` field from each input line, never the line position.
- A bare surname or a piece of a longer name ("wiskott", "hoffmann", "schlatter",
  "granulomatis", "spinosum") is `fragment`. Never put a bare surname in `syn`; only the
  full eponym ("Wiskott-Aldrich syndrome", "Osgood-Schlatter disease").
- `abbr`: common, unambiguous abbreviations as written on cards, case-sensitive ("SIADH",
  "G6PD", "NSAIDs"). Leave out anything that is also a common word or has several meanings
  (IV, PT, ST, OR, NO, CO, PE, MS, AS, CA).
- For an `abbr` candidate: keep it only if it has one dominant meaning on these cards, and
  write the entry for the **expanded term** (`"term": "Syndrome of inappropriate
  antidiuretic hormone secretion"`, `"abbr": ["SIADH"]`). Keep well-known abbreviations
  too (HIV, DNA, MRI): the pop-up just spells them out in one short sentence.

## Process

- Do your assigned batches in order. Write each output file completely before moving on.
- Run `python3 tools/check_defs.py data/candidates/batch_NNN.jsonl data/defs/batch_NNN.jsonl`
  on each file; fix anything it reports.
- Commit and push after every few batches so nothing is lost.
- You may hand batches to subagents in parallel. Give each subagent this whole file and
  its batch numbers, and have it write the output files itself.
