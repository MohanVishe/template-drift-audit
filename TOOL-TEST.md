# Does the layout change how well a model uses tools?

*Also on the website: https://mohanvishe.github.io/template-drift-audit/tool-test.html*

The [main article](ARTICLE.md) showed that for 32 of 43 popular models in
Ollama's library, the text the model reads when it uses tools isn't the text its maker designed.
The obvious next question: does that change what the model does? I tested one model, qwen2.5, on
1,240 tool questions, once with each layout. With the maker's layout it answered 45 more of them
correctly.

- **83.4%** correct with Ollama's layout (1,034 of 1,240)
- **87.0%** correct with the maker's layout (1,079 of 1,240)
- **70 vs 25:** questions only one layout got right, the maker's vs Ollama's

## The short version

**If you just use AI on your computer**

- The same model, on the same computer, did better at using tools when it was given the layout
  its maker designed: about 4 more correct answers in every 100.
- The biggest single difference: with Ollama's layout, the model more often used a tool when none
  of the tools fitted the question.
- If a local model is clumsy with tools, the app's layout can be part of the reason, not only the
  model.

**If you build with AI**

- On qwen2.5, the layout alone moved tool-calling accuracy from 83.4% to 87.0% on BFCL's five
  single-turn categories. The overall difference is clear (exact paired test, p ≈ 0.000004).
- Every category moved the same way, but no single category is conclusive on its own.
- If you depend on tool calling, test it on the exact package you ship. And if you benchmark on
  Ollama, turn the prompt cache off (details below).

## What I tested

**The model.** `qwen2.5` 7B, the build in Ollama's library (`qwen2.5:latest`, model layer
`2bada8a74506`). It's the same build the main article measured, and its tools arrive in a
different format from the one its maker designed: Go's internal format instead of labelled JSON
([the example](ARTICLE.md#weak-spot-4-the-layout-step-can-change-what-the-model-reads)).

**The two layouts.**

- **Ollama's layout:** the exact text Ollama builds for this model, produced by Ollama's own code.
- **The maker's layout:** the text built by the maker's chat template, from the
  [Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) repository at a fixed
  version (commit `a09a354`).

Everything else stayed the same: the same model file, the same app, the same settings, the same
questions. Only the layout changed.

**The questions.** I used the Berkeley Function Calling Leaderboard (BFCL), a public test of how
well models use tools, from UC Berkeley's Gorilla project. Each question comes with one or more
tools and an answer key. I used its five single-turn categories, 1,240 questions in all:

| Category | What the model has to do | Questions |
|---|---|---|
| One tool, one call | One tool is offered. Call it once, with the right details. | 400 |
| Pick the right tool | Several tools are offered. Choose the right one. | 200 |
| One tool, several calls | Call the same tool a few times in one reply, for example for two cities. | 200 |
| Several tools, several calls | Make several calls, to different tools. | 200 |
| No suitable tool: don't call | None of the tools fits the question. The right answer is not to call any. | 240 |

**How it's scored.** BFCL's own checker, unchanged: it compares each call with the answer key
(the tool's name, the required details and the values allowed).

## What makes the comparison fair

- **Same model, same server.** One Ollama installation (version 0.40.7), kept separate from
  everyday use, with the whole model on the graphics card for every question.
- **No randomness.** The model always picks its most likely next word (temperature 0, fixed
  seed). Asking the same question twice gives the same answer.
- **Checked, not assumed.** I asked 20 questions a second time with each layout. All 40 answers
  came out identical, character for character.
- **The prompt is exactly Ollama's.** On a 50-question trial, the text I built from Ollama's code
  matched the text Ollama itself builds, byte for byte, on every question.
- **The same reader for both.** Both layouts' replies are read by BFCL's own parser, so any
  difference comes from the layout, not from how a reply is read.
- **A hidden cache, found and switched off.** On the first trial, 6 of 50 questions gave
  different answers to identical prompts. The cause: the engine inside Ollama keeps recent prompts
  in memory, and reusing one slightly changes the arithmetic, which can tip the model's choice of
  word. I turned that cache off for this study server only. Every one of the 2,480 replies records
  0 reused tokens.
- **Nothing cut short.** The longest prompt was 1,000 tokens, and no reply hit the length limit.

## Results

![Share of test questions qwen2.5 answered correctly, with Ollama's layout and with the maker's: one tool, one call 92.5% vs 94.5%; pick the right tool 91.0% vs 95.5%; one tool, several calls 86.0% vs 89.5%; several tools, several calls 81.5% vs 84.5%; no suitable tool 61.3% vs 67.5%; all five together 83.4% vs 87.0%](docs/assets/img/tool-test.svg)

| Category | Ollama's layout | Maker's layout | Only maker's right | Only Ollama's right |
|---|---|---|---|---|
| One tool, one call | 370 of 400 | 378 of 400 | 13 | 5 |
| Pick the right tool | 182 of 200 | 191 of 200 | 11 | 2 |
| One tool, several calls | 172 of 200 | 179 of 200 | 10 | 3 |
| Several tools, several calls | 163 of 200 | 169 of 200 | 13 | 7 |
| No suitable tool: don't call | 147 of 240 | 162 of 240 | 23 | 8 |
| **All five** | **1,034 of 1,240** | **1,079 of 1,240** | **70** | **25** |

**How to read this.** For most questions, both layouts gave the same verdict, right or wrong. For
639 of the 1,240, the model wrote exactly the same reply both times. What matters is the
questions where the verdicts differ: 70 that only the maker's layout got right, and 25 that only
Ollama's did.

**Is that more than chance?** If the layout made no difference, a split as lopsided as 70 to 25
would turn up by chance about 4 times in a million (exact paired test, two-sided, p ≈ 0.000004).
So for all five categories together, the difference is clear.

**Category by category, it's a consistent lean, not five separate proofs.** Every category favours
the maker's layout. But each one alone has too few differing questions to rule out chance once
you allow for testing five at a time (Holm correction). The closest is "no suitable tool"
(corrected p = 0.053), then "pick the right tool" (0.090). I decided before seeing the results
that the overall test is the headline.

## Where the difference comes from

**The biggest single gap: calling a tool when none fits.** With Ollama's layout, the model called
a tool on 93 of the 240 "no suitable tool" questions. With the maker's layout, 78. That category
alone accounts for 23 of the 70 questions only the maker's layout got right.

Here is one of them, `irrelevance_11` in BFCL. The question is *"What is the closest integer to
30?"*, and the only tool offered finds the closest prime number below a given number.

- **With Ollama's layout,** the model called the prime-number tool with 30.
- **With the maker's layout,** it called nothing and asked the user to say what they meant. BFCL
  counts not calling as the right answer here.

**The other gaps are small mistakes in the details.** Here's `parallel_21`. The question asks for
people convicted of money laundering in San Francisco in 2019 and in Texas in 2018, and the tool
says that `crime` is plain text.

- **With Ollama's layout,** the model made both calls but wrote the crime as
  `{"type": "money laundering"}`, a small object instead of text. BFCL marks that wrong.
- **With the maker's layout,** it wrote `"crime": "money laundering"`, as the tool asks.

Two examples show what the differences look like, not why they happen. The test shows that the
layout changes the answers. It doesn't show which part of the layout causes which mistake.

## What this means

**If you just use AI**

- On this test, the maker's layout gave about 4 more correct answers in every 100 (3.6, to be
  exact). The biggest gain was the model holding back when no tool fits, so it's less likely to
  do something you didn't ask for.
- You don't need to do anything technical for this. Keep Ollama updated: the tool-format problem
  is reported (issue #14601) and fixes have been proposed, so an update can bring the fix.

**If you build with AI**

- Test tool calling on the exact package you ship, through the same app, not on the model in
  general. The layout is part of what you ship.
- If a model's shipped template drifts from the maker's, you can set your own `TEMPLATE` in a
  Modelfile. Check the rendered prompt against the maker's template before you rely on it.
- If you compare prompts on Ollama, watch the prompt cache. Identical prompts gave different
  answers at temperature 0 until it was off. Run each variant on a fresh server, or check the
  reused-token count in each reply.

## What this covers, and what comes next

- **One model.** I picked qwen2.5 because its tool format is the most visibly changed. Other models
  drift in other ways, and the same harness can run them; that's the next step.
- **Single-turn questions.** Each question is one request and one reply. Conversations where the
  model uses a tool, reads the answer and carries on are the next step, and the harness already
  supports them.
- **The layout alone.** Both layouts' replies were read by BFCL's parser, to isolate the layout.
  In everyday use, Ollama reads the reply with its own parser, which in the trial dropped calls to
  tools that were never offered. That can rescue a few "no suitable tool" answers in real use.
- **A benchmark, not everyday use.** BFCL's questions are short, in English, with an answer key.
  Real conversations are longer and messier.
- **One interruption.** The run paused once when the graphics driver stopped responding, and
  carried on after a restart. The 40 repeated answers were identical before and after.

## Data and code

- Every reply and its score: [`runs/h3-mini/qwen2.5/`](https://github.com/MohanVishe/template-drift-audit/tree/main/runs/h3-mini/qwen2.5)
  (`records.jsonl`, `repeat.jsonl`, `meta.json`, `report.json`).
- The test runner and report: [`scripts/h3_mini.py`](https://github.com/MohanVishe/template-drift-audit/blob/main/scripts/h3_mini.py),
  [`scripts/h3_mini_report.py`](https://github.com/MohanVishe/template-drift-audit/blob/main/scripts/h3_mini_report.py)
  and [`tda/h3/`](https://github.com/MohanVishe/template-drift-audit/tree/main/tda/h3).
- Run on 25 October 2026, about 50 minutes of model time for 2,480 replies.

## Sources

- BFCL, the Berkeley Function Calling Leaderboard (Gorilla project, UC Berkeley), Apache-2.0, at
  commit `6ea5797`: [github.com/ShishirPatil/gorilla](https://github.com/ShishirPatil/gorilla).
  The two example questions are quoted from its data.
- Qwen2.5-7B-Instruct chat template, commit `a09a354`:
  [huggingface.co/Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct).
- Ollama 0.40.7 and issue [#14601](https://github.com/ollama/ollama/issues/14601).
- Holm, "A Simple Sequentially Rejective Multiple Test Procedure", *Scandinavian Journal of
  Statistics*, 1979.
