---
layout: default
title: Running AI at home
description: The six places a home AI setup can go wrong, explained in plain words, with a free check-up for your own computer and a measurement of 65 popular models.
---

# Running AI at home: where the weak spots are

<p class="lede">I took the 43 most popular models in Ollama's library and checked the exact text
each one is given when you use it with tools. For 32 of them, it isn't the text the model's maker
designed. That's one of six weak spots in a home AI setup. This page goes through all six in
plain words, shows how to check each one on your own computer, and says what to do about it.</p>

## What a home AI setup is made of

When you run an AI model on your own computer with an app like **Ollama** or **LM Studio**, these
parts work together:

1. **The app.** It runs quietly in the background as a small server. Other programs, such as a
   chat window, a coding helper or a browser add-on, send it messages and get answers back.
2. **The model file** you downloaded. It holds the trained model, plus two small extras: default
   settings, and a set of layout instructions called the **chat template**.
3. **The layout step.** Every time you send a message, the app uses the chat template to turn
   the whole conversation into one block of text. That block is all the model ever sees.
4. **Helpers you connect.** A coding assistant or an "agent" lets the model read files, run
   commands or open web pages for you.
5. **Saved chats.** Your conversations, kept as files on your disk.

Each part can go wrong in its own way. Here's each one, with what to look for and what to do.

---

## 1. The app answers anyone who can reach it

Ollama's server has no login. Anyone who can connect to it can do everything you can: chat with
your models, download new ones, delete them, or create a new model with its own instructions.
These are ordinary features, listed in Ollama's own code
([routes.go](https://github.com/ollama/ollama/blob/v0.40.7/server/routes.go)).

What keeps you safe is the address it listens on. Out of the box, Ollama only accepts connections
from your own computer, through the special address `127.0.0.1`
([config.go](https://github.com/ollama/ollama/blob/v0.40.7/envconfig/config.go)). One setting,
`OLLAMA_HOST`, changes that. People often change it on purpose so they can use their model from a
phone or a second computer. LM Studio has a switch for the same thing, called
**Serve on Local Network**. Once either is on, everyone on the same Wi-Fi can use your AI. If your
router forwards the port, the whole internet can too.

**How to tell:** the check-up looks at the addresses your AI apps are listening on and tells you
if anything other than your own computer can connect.

## 2. Older versions have known holes

Ollama is updated often, and some updates fix security problems. Two published ones show why
updating matters:
- **A crafted model upload could leak memory** (CVE-2026-7482). Before version 0.17.1, sending
  Ollama a specially built model file made it read memory it shouldn't
  ([GitHub advisory](https://github.com/advisories/GHSA-x8qc-fggm-mpqg)). The upload goes through
  the "create a model" feature from point 1. An app that others can reach is therefore exposed to
  this too.
- **The Windows updater accepted unchecked updates** (CVE-2026-42248 and CVE-2026-42249). Ollama for
  Windows didn't verify that a downloaded update was genuine. Versions 0.12.10 to 0.17.5 were
  confirmed affected
  ([advisory](https://github.com/advisories/GHSA-5fjh-wjgp-25ph),
  [advisory](https://github.com/advisories/GHSA-7mp6-jmch-f3fh)). Ollama 0.23.3 hardened its update
  process ([release notes](https://github.com/ollama/ollama/releases/tag/v0.23.3)).

The newest Ollama when this was written is
[0.40.8](https://github.com/ollama/ollama/releases/tag/v0.40.8), released on 21 October 2026.

**How to tell:** the check-up asks your running Ollama for its version and compares it with these
fixes.

## 3. A model file carries more than the model

A model file isn't only the trained model. It also carries the chat template, which is a small
program, plus default settings. Whoever packages the file decides what goes in them, and you never
see them unless you go looking.

My measurement found two everyday examples of this:
- **Outdated copies.** In 9 of 45 model files in Ollama's library, the template inside is an
  older version of the maker's. For example, `falcon3`'s file matches the maker's template from
  17 December 2024. The next day, the maker published a change called "fix chat_template for tool
  use". The file was simply made before it.
- **Rewritten instructions.** On Hugging Face, where anyone can upload, two popular custom models
  replace the maker's instructions for using tools with their own wording. They also add a
  standing instruction about how to answer.

Neither is an attack. But they show that the instructions travelling with a model can change
between its maker and your computer.

**How to tell:** the check-up lists where each of your models came from: Ollama's own library, or
a named uploader on Hugging Face. It also reads each template for two unusual things: a web
address, or a rule that reacts when you type particular words. I tested that warning on 95 real
templates. It went off for 3, and all 3 turned out to be ordinary, visible features. So it's rare,
and worth a look when it happens.

## 4. The layout step can change what the model reads

This is the weak spot I measured, because nobody had counted it.

A model learns to read conversations laid out in one exact way: who is speaking, where
instructions go, how a tool is described, how a tool's answer comes back. Its maker publishes the
chat template that produces that layout. If the app lays the conversation out differently, the
model is reading something it wasn't trained on. It's like being handed a familiar form where the
boxes have moved. Usually you'd cope, but you'd make more mistakes, and with tools, mistakes turn
into actions.

### What I measured

For each model, I produced the text the model would read in three ways:

1. with **the maker's original** template;
2. with **the copy inside the model file**;
3. with **what Ollama actually uses**. Ollama often ships its own version of the template.

I ran twelve harmless practice conversations through all three and compared the results. Six of
the conversations use tools. For the Ollama step, the comparison runs Ollama's own code, so nothing
is guessed. [How it works](how-it-works.html) explains the method and how it was checked.

The models were the 50 most popular chat models in Ollama's library and the 30 most downloaded
chat models on Hugging Face, as they were on 22 October 2026. Some couldn't be compared fairly,
for example because the maker never published a template. That left **65 models**. The
[results page](results.html) lists all of them, with the reason for each one left out.

### What I found

**In Ollama's library, 32 of 43 models read their tool conversations differently from what
their maker designed.** "Differently" means a change to what the model is told: a tool's answer
missing, an instruction added or dropped, tools described in another format. Changes to spaces,
line breaks or the date don't count.

In four of the 32, the only change is the order of the fields in a tool's description. That's the
mildest kind, so here's the count without them: **28 of 43**.

Some of these models weren't built for tools at all. Counting only the 19 whose maker's template
does show the model a list of tools: **15 of 19** differ, or **11 of 19** without the
order-only cases.

**Where the differences come from:**
- In 24 of the 32, the model file matches the maker's template. Ollama's own version introduces
  the difference.
- In 6, the model file already holds an older copy of the maker's template, and Ollama's version
  changes it further.
- In 2, the model file has no template of its own to compare.

**What changes most often** (out of the 28):
- **Tool answers** (20 models). What a tool sent back is laid out differently, merged with other
  text, or left out.
- **Standing instructions** (10). A default instruction is added that the maker didn't write, or
  one the maker wrote goes missing.
- **Earlier tool requests** (10). The model's own previous request to use a tool is written back
  differently.
- **The list of tools** (7). In some conversations, the model isn't shown its tools at all.

**Hugging Face downloads fare better.** For these, Ollama uses the template inside the file
instead of its own. Only 5 of 22 differ, and in all 5 the difference is already in the uploaded
file. Ollama adds no meaningful change of its own.

**A template that looks different can still be fine.** In 7 of the Hugging Face models, the
template text differs from the maker's, yet all twelve conversations came out exactly the same.
Reading templates side by side doesn't tell you much. Comparing the text the model actually
receives does.

### One model, step by step: `qwen2.5`

`qwen2.5` is the fourth most popular chat model in Ollama's library. Its default download is the
7-billion-parameter instruct model.
- **The model file holds an outdated template.** It matches the maker's template as it was on
  18 September 2024. The maker updated it the next day.
- **Ollama's version describes tools in the wrong format.** The model was trained to read tool
  descriptions written in JSON, a standard data format. Ollama's version hands them over in the
  internal format of its own programming language, with words like `<nil>` mixed in. This is
  already reported to Ollama ([issue #14601](https://github.com/ollama/ollama/issues/14601)), and
  fixes have been proposed. The measurement shows how far it reaches: 4 of the 43 library models
  (`qwen2`, `qwen2.5`, `qwen2.5-coder` and `qwen3`).
- **The Hugging Face copy loses a default instruction.** Downloaded from Hugging Face instead, the
  model file matches the maker's template exactly. But the version Ollama builds for it leaves out
  the short default instruction the maker's template adds when you don't write one yourself.

**How to tell:** the full comparison needs a few more tools and is described in
[How it works](how-it-works.html). The quick check-up covers the parts you can act on: where your
models came from, and whether their templates have warning signs.

## 5. Helpers turn the model's words into actions

On its own, a model only writes text. Once you connect a helper that can read files, run commands
or browse, its text becomes actions on your computer. Two things can then go wrong:
- **The model makes a mistake.** The layout problems in point 4 make this more likely.
- **The model is misled by what it reads.** A web page, an email or a file can contain text
  written to give the AI orders. The model can't reliably tell those apart from yours. OWASP, a
  long-standing security community, lists this ("prompt injection") as the number one risk for AI
  applications ([OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)).

Either way, what the helper can reach is what's at risk. Project folders often hold a file called
`.env` with passwords and keys in it, or a private key for logging in to servers.

**How to tell:** point the check-up at the folder your helper works in. It lists any file whose
name suggests it holds a secret. It reads only the names, never the contents.

## 6. Your chats are kept as ordinary files

"Local" means your conversations stay on your computer. It also means they sit on your disk,
where anything that can read your files can read them too:
- **Ollama in a terminal** keeps the last 100 lines you typed in a file called `.ollama/history` in
  your home folder, unless you set `OLLAMA_NOHISTORY`
  ([history.go](https://github.com/ollama/ollama/blob/v0.40.7/readline/history.go)).
- **The Ollama desktop app** keeps its chats in a database file in its app folder
  ([app_state.go](https://github.com/ollama/ollama/blob/v0.40.7/internal/onboarding/app_state.go)).
- **LM Studio** keeps each chat as a file in `.lmstudio/conversations` in your home folder
  ([LM Studio docs](https://lmstudio.ai/docs/app/basics/chat)).
- **A debugging setting** in Ollama, `OLLAMA_DEBUG_LOG_REQUESTS`, writes the full text of every
  request to your temp folder ([config.go](https://github.com/ollama/ollama/blob/v0.40.7/envconfig/config.go)).
  It's off unless someone turns it on.

None of this is a fault. But backup and sync tools copy these files like any others, and anyone
who uses your account can open them.

**How to tell:** the check-up lists where your chats are saved and how big those files are,
without opening them. It warns you if the debugging setting is on.

---

## Run the check-up

The check-up looks at all of this on your own computer in about ten minutes. It needs Python and
nothing else. It changes nothing and sends nothing anywhere.

**[Step-by-step instructions →](guide.html)**

## What this doesn't tell you

- **A clean check-up isn't a guarantee.** It looks for known warning signs. It can't prove a model
  or an app is trustworthy.
- **A different layout isn't proof of harm.** It shows that the model reads something it wasn't
  trained on. How much that costs in practice, for example in correct tool use, is a separate
  question.
- **The measurement is a snapshot.** It covers the most popular models on 22 October 2026, as they
  were that day.
- **Two parts are close copies, not Ollama's own code.** For Hugging Face downloads, and for three
  library models, Ollama fills in the template with a separate engine. I reproduced that engine's
  behaviour in Python. It's very close, but not byte-for-byte Ollama.
- **Practice conversations have limits.** Mistral's own template, for example, rejects the made-up
  tool request numbers my practice conversations use, so a few of its comparisons couldn't run.
  The [results page](results.html) lists every gap like this.

## Sources

- Ollama source code, version 0.40.7: `server/routes.go`, `envconfig/config.go`,
  `readline/history.go`, `internal/onboarding/app_state.go`.
- Ollama release notes for 0.23.3 and 0.40.8, and issue #14601.
- GitHub Advisory Database and the US National Vulnerability Database: CVE-2026-7482,
  CVE-2026-42248, CVE-2026-42249.
- LM Studio documentation, "Manage chats".
- OWASP Top 10 for LLM Applications 2025, LLM01: Prompt Injection.
- This project's measurement runs of 22 October 2026, published with the code on
  [GitHub](https://github.com/MohanVishe/template-drift-audit).
