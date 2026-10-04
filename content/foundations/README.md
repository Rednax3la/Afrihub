# Foundations: reviewable drafts, not published pronunciation

There are four stable modules for each of the repository's 14 canonical languages: orthography, letter/sound relationships, meaningful contrasts, then listening/practice. The 56 records in `drafts.json` are **all unpublished**. They are editorial scaffolding with language-specific review targets, not 56 finished lessons or fabricated recordings.

`orthography_evidence.json` records pinned Unicode CLDR release-47 URLs, file checksums and exemplar sets for 13 locale codes. CLDR exemplars are useful writing-system evidence, not a complete alphabet or phonetic authority. Preserve the accompanying `UNICODE-LICENSE.txt` when redistributing that data. Twi is explicitly blocked for an Asante-specific orthography review; Akan-wide data is not substituted. Kalenjin/Nandi and Luhya/Lubukusu require a specialist to approve the intended variety, even where CLDR has a broader locale.

Kikuyu's seven vowel letters include **ĩ and ũ**. Their tildes are neither circumflexes nor generic tone marks; deleting them changes the written vowel distinction. The draft references [Seth Cable's UMass field-methods notes](https://people.umass.edu/scable/LING404-FA10/Materials/Kikuyu-Basics.pdf) and the [Rice Gĩkũyũ sketch](https://www.ruf.rice.edu/~reng/kik/sketch.pdf). Those sources inform a short original teaching note; no whole lesson or recording is copied. Other language-specific contrasts remain review targets until a specialist supplies reliable phonetic descriptions and attested examples.

Use `TUTOR_RECORDINGS.md` for each language's grapheme/contrast, examples or explicit example-selection task, recording requirements and review status. Only Kikuyu includes a few source-grounded example words; do not invent example words for rows still awaiting a tutor. Preserve original marks, record the actual variety, and retain consent for commercial playback, speaker attribution and reviewer sign-off. No synthetic audio is represented as a human authority.

## Safe import and publication

```text
python backend/scripts/import_foundations.py content/foundations/drafts.json
```

That default dry run validates all records and makes no database connection. After the owner resolves infrastructure and chooses the existing `MONGODB_URI` and `DB_NAME` in a trusted execution environment, `--apply` creates the separate `foundations` collection/indexes and inserts missing drafts. Repeat runs preserve existing reviewed records. **No units, lesson IDs, XP, completions or subscriptions are written.** Foundations appear ahead of lessons in the dashboard but are not mandatory gates. Existing `order > 3` premium enforcement is unchanged.

To publish a reviewed subset, prepare a separate JSON file retaining the IDs, set `status=published`, `reviewed_by`, and `reviewed_at`. Sound/contrast/listening modules also require `recordings` with HTTPS `audio_url`, `grapheme`, `example`, `speaker_consent`, and `reviewed_by`. Dry-run with `--publish-reviewed`, then repeat with `--publish-reviewed --apply`. This explicit mode updates approved records. The API exposes only published modules, with a maximum of four per language. The player renders the selected text/audio; interactive pronunciation scoring is not implemented.

No import or recording was made in production. Until review and publication, the user-facing page honestly reports “Coming soon” and allows continuing existing lessons. The migration scripts and content files should be run from a trusted repository checkout; if Railway builds only `backend/`, copy the reviewed content artifact into the operator environment rather than changing the app's database configuration.
