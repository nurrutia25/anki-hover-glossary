# AnkiWeb listing — copy into ankiweb.net/shared/upload

## File

`dist/hover_glossary-1.0.0.ankiaddon`

## Title

Hover Glossary – plain-English pop-up definitions for medical terms (AnKing compatible)

## Tags

medical glossary definitions hover tooltip anking usmle step1 medicine dictionary abbreviations

## Support Page

https://github.com/nurrutia25/anki-hover-glossary/issues

## Description (paste as-is; AnkiWeb accepts basic HTML)

```html
<b>Hover a hard medical term on any card and get a short, plain-English definition.</b>

<img src="https://raw.githubusercontent.com/nurrutia25/anki-hover-glossary/main/docs/demo.png" width="700">

Hard terms on your cards get a faint dotted underline. Hover one (or click it) and a small pop-up explains what it is, plus the one association that makes the card make sense. Abbreviations work too: hover <b>SIADH</b> and the pop-up spells it out, then defines it.

<b>What's in it</b>
<ul>
<li><b>About 9,000 terms and 1,160 abbreviations</b>, chosen from the vocabulary of the AnKing Step deck and the U.S. National Library of Medicine's MeSH vocabulary. Eponyms and signs are included (Kayser-Fleischer rings, Chvostek sign, Janeway lesions), along with drugs, bugs, enzymes, histology findings and syndromes.</li>
<li><b>Only the terms you'd actually look up.</b> "Urticaria" gets a pop-up and "hives" doesn't. Definitions are written at a college reading level, not dumbed down.</li>
<li><b>Works on every card and note type:</b> AnKing, your own decks, cloze, basic and Image Occlusion.</li>
<li><b>Never changes your notes.</b> Terms are marked on screen only, so AnkiHub/AnKing updates, syncing and shared decks are unaffected.</li>
<li><b>Works offline and collects no data.</b> The whole glossary ships inside the add-on.</li>
</ul>

<b>How to use</b>
<ul>
<li>Hover a dotted term to see its definition. Click it to pin the pop-up; click elsewhere or press Esc to close.</li>
<li>Click <b>edit</b> in a pop-up to reword a definition for yourself. Your edits are kept across updates.</li>
<li>Use <b>Tools → Hover Glossary definitions</b> to switch it on or off.</li>
<li>Settings (Tools → Add-ons → Hover Glossary → Config): show on the question side or only after the answer, underline every occurrence, and hover delay.</li>
</ul>

<b>Compatibility</b>
<ul>
<li>Anki 2.1.50+ on desktop (Mac, Windows, Linux). AnkiMobile and AnkiDroid don't run add-ons.</li>
<li><b>Onigiri:</b> supported. Clicking a term won't flip the card, and the underlines step aside while you edit a card in the reviewer.</li>
<li>Don't run it alongside another add-on that underlines terms (e.g. AMBOSS), or terms get marked twice.</li>
</ul>

<b>Accuracy</b>
The definitions are short study aids, not a clinical reference. They can be incomplete or occasionally wrong, so don't use them for patient care. Spotted a bad or missing definition? Please report it on <a href="https://github.com/nurrutia25/anki-hover-glossary/issues">GitHub</a> with the term and the fix.

<b>Open source</b>
Code is MIT-licensed; the definitions are CC BY-SA 4.0. Source, the full term list and contribution steps are on <a href="https://github.com/nurrutia25/anki-hover-glossary">GitHub</a>. The term list is built in part from MeSH, courtesy of the U.S. National Library of Medicine. Not affiliated with AnKing, AnkiHub, AMBOSS or NLM.
```

## After uploading

1. AnkiWeb gives the add-on a number (the install code). Put it in the README's Install section and in `addon/manifest.json`, then rebuild.
2. The screenshot and GitHub links only work once the repo is public. Until then, upload `docs/demo.png` somewhere public, or leave the image out.
