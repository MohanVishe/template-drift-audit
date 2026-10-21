# Labelling guide for rendered-prompt diffs

Each pair is (a, b): `a` is the reference side (the author's template, or the earlier layer), `b`
is the other side. A pair gets **every class that applies**, plus the pair's severity, which is the
highest severity among its classes.

## Classes

| Class | Severity | Meaning |
|---|---|---|
| `IDENTICAL` | none | byte-identical after date normalisation |
| `WHITESPACE` | none | only spaces or newlines differ, outside JSON (trailing newline, indentation) |
| `BOS` | none | a leading BOS token added or removed (the tokenizer may add it anyway; reported separately) |
| `DATE` | none | an injected current-date line differs |
| `JSON_SPACING` | minor | the same JSON with different spacing (`{"a": 1}` vs `{"a":1}`), in tool definitions or tool calls |
| `DEFAULT_SYSTEM` | material | a system prompt the conversation did not supply is added, dropped or changed |
| `TOOL_SCHEMA` | material | tool definitions, or the tool-use instructions around them, differ in wording, layout, keys or order |
| `TOOL_SCHEMA_NOT_JSON` | material | tool definitions reach the model in a non-JSON form (e.g. Go struct printing with `<nil>`) |
| `TOOLS_DROPPED` | material | tools were passed but no tool definitions appear |
| `TOOL_CALL` | material | an assistant tool call is dropped, merged, renamed or re-wrapped (spacing alone is `JSON_SPACING`) |
| `TOOL_RESULT` | material | tool results are grouped, re-roled or re-wrapped differently |
| `THINKING` | material | reasoning is kept, dropped or wrapped differently |
| `CONTENT` | material | the text of a user, assistant, system or tool message is altered (escaping, evaluation, truncation) |
| `STRUCTURE` | material | turn or role markers differ outside tools and system (merged turns, missing generation prompt) |
| `RENDER_ERROR` | material | one side failed to render the fixture |
| `OTHER` | material | anything not covered; needs a written note |

## Process

- Labels are written by reading the line diff (`python scripts/show_pairs.py <id>`), **before** the
  classifier exists, and are not edited after the classifier is run.
- If the classifier disagrees, the disagreement is reported, not fixed by relabelling.
- Constructed pairs are labelled from their construction.

Labeller: Claude (Opus 5.5), 2026-10-22. A second human review of a sample is recommended before
the agreement numbers are published.

**Split:** dev = `q25-L0-L1`, `q25-L1-L3` and even-numbered constructed pairs. Test = `q25-L0-L3-hf`,
`coder7-L1-L3` and odd-numbered constructed pairs. The test half includes two templates the dev half
never shows, the HF-converted one and the coder one.
