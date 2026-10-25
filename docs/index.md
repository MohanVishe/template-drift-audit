---
layout: default
title: Running AI locally
description: The six places a local AI setup can go wrong, explained in plain words for everyday users and AI engineers, with a free check-up for your own computer and a measurement of 65 popular models.
---

# Running AI locally: six weak spots, explained simply

<p class="lede">I took 43 of the most popular models in Ollama's library and checked the exact text
each one is given when you use it with tools. For 32 of them, it isn't the text the model's maker
designed. That's one of six weak spots in a local AI setup. This page explains all six in plain
words: what each means if you simply use AI, what it means if you build with AI, how to check it on
your own computer, and what to do about it.</p>

<p class="diagram-note">This started from Kai's video <a href="https://www.youtube.com/watch?v=3mx84MRj8lY"><em>Your Local AI Is Not as Private as You Think</em></a> (October 2026). I followed its leads back to the original sources, read Ollama's code myself, and measured what the model actually reads. <a href="#credits">What's mine and what's the video's</a>.</p>

<div class="box box-accent" markdown="1">

### The short version

<div class="views" markdown="1">
<div class="view" markdown="1">

**If you just use AI on your computer**

- Running AI locally keeps your chats off other companies' computers. It doesn't make your setup
  safe by itself.
- Three things to do today:
  1. Make sure your AI app only accepts connections from your own computer (weak spot 1).
  2. Update Ollama (weak spot 2).
  3. Keep passwords and keys out of any folder an AI helper can read (weak spot 5).
- The [free check-up](guide.html) tells you where you stand in about ten minutes. It changes
  nothing and sends nothing anywhere.

</div>
<div class="view" markdown="1">

**If you build with AI**

- The prompt your model reads can differ from the one its maker trained it on, even when you
  change nothing. In Ollama's library this held for 32 of 43 models on the tool conversations I
  tested. For `qwen2.5`, it cost 45 of 1,240 answers on a tool benchmark
  ([tool test](tool-test.html)).
- Compare the rendered prompt, not the template file.
- Treat a model's template as code that comes with the model, and the folders your agent can read
  as its blast radius.

</div>
</div>
</div>

{% include fig/stats.html %}

## How a local AI setup works

When you run an AI model on your own computer with an app like **Ollama** or **LM Studio**, these
parts work together. The numbers mark the six weak spots described below.

<div class="flow" role="img" aria-label="Your message goes to the app, which uses the chat template to lay out the conversation, which the model then reads. The model file, connected helpers and saved chats sit alongside.">
  <div class="node"><b>You</b><em>type a message in a chat window or a coding helper</em></div>
  <div class="arrow" aria-hidden="true">→</div>
  <div class="node"><b><span class="tag">1</span><span class="tag">2</span>The app</b><em>Ollama or LM Studio, running quietly in the background</em></div>
  <div class="arrow" aria-hidden="true">→</div>
  <div class="node"><b><span class="tag">4</span>The layout step</b><em>turns the whole conversation into one block of text</em></div>
  <div class="arrow" aria-hidden="true">→</div>
  <div class="node"><b>The model</b><em>reads that block, and only that block</em></div>
</div>
<div class="flow-side" aria-hidden="true">
  <div class="node"><b><span class="tag">3</span>The model file</b>the model, its default settings and its layout instructions</div>
  <div class="node"><b><span class="tag">5</span>Helpers</b>tools that let the model read files, run commands or browse</div>
  <div class="node"><b><span class="tag">6</span>Saved chats</b>your conversations, kept as files on your disk</div>
</div>
<p class="diagram-note">The layout instructions inside the model file are called the <strong>chat template</strong>. Unfamiliar words are explained at the <a href="#words-used-on-this-page">end of the page</a>.</p>

Each part can go wrong in its own way. Here's each one.

<section class="spot" markdown="1">

## <span class="num">1</span> The app answers anyone who can reach it

Ollama runs a small **server** on your computer: a program that waits for other programs to send
it messages. It has no login. Anyone who can connect to it can do everything you can: chat with
your models, download new ones, delete them, or create a new model with its own instructions.
These are ordinary features, listed in Ollama's own code
([routes.go](https://github.com/ollama/ollama/blob/v0.40.7/server/routes.go)).

What keeps you safe is the address it listens on. Out of the box, Ollama only accepts connections
from your own computer, through the special address `127.0.0.1`
([config.go](https://github.com/ollama/ollama/blob/v0.40.7/envconfig/config.go)). One setting,
`OLLAMA_HOST`, changes that. People often change it on purpose so they can use their model from a
phone or a second computer. LM Studio has a switch for the same thing, called
**Serve on Local Network**. Once either is on, everyone on the same Wi-Fi can use your AI. If your
router forwards Ollama's connection point (its "port") to the internet, everyone online can too.

**What I found in Ollama's code.** I read the server code of Ollama 0.40.7 to see exactly what an
open port gives away:
- **Its protection against websites switches off.** Ollama checks which address each request was
  sent to, which blocks a known trick where a web page quietly talks to your Ollama ("DNS
  rebinding"). The code runs this check only while Ollama listens on `127.0.0.1`
  ([routes.go](https://github.com/ollama/ollama/blob/v0.40.7/server/routes.go)). Open it to the
  network and the check is skipped.
- **Your ollama.com account comes with it.** If Ollama is signed in to an ollama.com account (for
  cloud models or web search), it forwards some requests to ollama.com signed with your computer's
  own key, whoever sent them
  ([cloud_proxy.go](https://github.com/ollama/ollama/blob/v0.40.7/server/cloud_proxy.go)). Anyone
  who can reach it can read the account's name, email and plan, see its usage and balance, and run
  cloud models and web searches on it.
- **Which websites may talk to it is one setting.** By default, only pages served from your own
  computer and a few kinds of app can read Ollama's answers in a browser. Each address added to
  `OLLAMA_ORIGINS` lets that website do the same
  ([config.go](https://github.com/ollama/ollama/blob/v0.40.7/envconfig/config.go)).

<figure class="fig-img"><picture><source media="(max-width: 640px)" srcset="assets/img/reach-narrow.svg"><img src="assets/img/reach.svg" alt="Who can reach your Ollama: this computer only by default, your network if OLLAMA_HOST is 0.0.0.0, the internet if the port is forwarded; and what anyone who connects can do, including using a signed-in ollama.com account"></picture></figure>

<div class="views" markdown="1">
<div class="view" markdown="1">

**If you just use AI:** think of it as leaving your front door open. On home Wi-Fi the risk is the
people and devices on your network. On café, hostel or office Wi-Fi, it's strangers.

</div>
<div class="view" markdown="1">

**If you build with AI:** a reachable Ollama is an unauthenticated API that can pull, delete and
create models with any system prompt, and a signed-in server lends out its ollama.com account. Put
an authenticating proxy in front of a shared server, and keep `OLLAMA_ORIGINS` to the exact sites
that need it.

</div>
</div>

<div class="tell" markdown="1">
**How to tell:** the check-up looks at the addresses your AI apps are listening on, and at the
`OLLAMA_HOST` setting, and tells you if anything other than your own computer can connect.
**What to do:** delete `OLLAMA_HOST` or set it to `127.0.0.1`, then restart Ollama. In LM Studio,
turn off **Serve on Local Network**.
</div>
</section>

<section class="spot" markdown="1">

## <span class="num">2</span> Older versions have known holes

Ollama is updated often, and some updates fix security problems. Each published problem gets an
ID that starts with "CVE". Two of them show why updating matters:
- **A crafted model upload could leak memory** (CVE-2026-7482). Before version 0.17.1, sending
  Ollama a specially built model file made it read memory it shouldn't
  ([GitHub advisory](https://github.com/advisories/GHSA-x8qc-fggm-mpqg)). The upload uses the
  "create a model" feature from point 1, so an app that others can reach is exposed to this too.
- **The Windows updater accepted unchecked updates** (CVE-2026-42248 and CVE-2026-42249). Ollama for
  Windows didn't verify that a downloaded update was genuine. Versions 0.12.10 to 0.17.5 were
  confirmed affected
  ([advisory](https://github.com/advisories/GHSA-5fjh-wjgp-25ph),
  [advisory](https://github.com/advisories/GHSA-7mp6-jmch-f3fh)). Ollama 0.23.3 hardened its update
  process ([release notes](https://github.com/ollama/ollama/releases/tag/v0.23.3)).

The newest Ollama when this was written is
[0.40.8](https://github.com/ollama/ollama/releases/tag/v0.40.8), released on 21 October 2026.

<div class="views" markdown="1">
<div class="view" markdown="1">

**If you just use AI:** it's the same as updating your phone. Old versions have holes that are
public knowledge.

</div>
<div class="view" markdown="1">

**If you build with AI:** pin the Ollama version in your setup scripts and images, and track its
advisories like any other dependency. Points 1 and 2 add up: an exposed, old server is the worst
case.

</div>
</div>

<div class="tell" markdown="1">
**How to tell:** the check-up asks your running Ollama for its version and compares it with these
fixes. **What to do:** install the latest Ollama from [ollama.com](https://ollama.com) over the
old one. Your models stay where they are.
</div>
</section>

<section class="spot" markdown="1">

## <span class="num">3</span> A model file carries more than the model

A model file isn't only the trained model. It also carries the chat template, which is a small
program, plus default settings. Whoever packages the file decides what goes in them, and you never
see them unless you go looking.

**What I found myself.** My measurement turned up two everyday examples:
- **Outdated copies.** In 9 of 45 model files in Ollama's library, the template inside is an
  older version of the maker's. For example, `falcon3`'s file matches the maker's template from
  17 December 2024. The next day, the maker published a change called "fix chat_template for tool
  use". The file was simply made before it.
- **Rewritten instructions.** On **Hugging Face**, the largest public website for sharing AI
  models, anyone can upload. Two popular custom models there replace the maker's instructions for
  using tools with their own wording. They also add a standing instruction about how to answer.

Neither is an attack. But they show that the instructions travelling with a model can change
between its maker and your computer.

<div class="views" markdown="1">
<div class="view" markdown="1">

**If you just use AI:** where you download a model from matters. The maker's official release or
Ollama's own library is the safer default, especially for a model that can use tools.

</div>
<div class="view" markdown="1">

**If you build with AI:** a template is code from the same source as the weights. A malicious one
was enough for remote code execution in llama-cpp-python
([CVE-2024-34359](https://github.com/advisories/GHSA-56xg-wfcc-g829)), and a tampered one can plant
a hidden backdoor that passes a hub's automated scans
([Pillar Security, 2026](https://www.pillar.security/blog/from-discovery-to-large-scale-validation-chat-template-backdoors-across-18-models-and-4-engines)).
Render templates only in a sandbox. When one differs from the maker's, check the maker's history
first: here, the usual reason was an older version.

</div>
</div>

<div class="tell" markdown="1">
**How to tell:** the check-up lists where each of your models came from: Ollama's own library, or
a named uploader on Hugging Face. It also reads each template for two unusual things: a web
address, or a rule that reacts when you type particular words. I tested that warning on 95 real
templates. It went off for 3, and all 3 turned out to be ordinary, visible features. So it's rare,
and worth a look when it happens. **What to do:** if you didn't expect it, remove the model
(`ollama rm <name>`) and get it from the maker's official source.
</div>
</section>

<section class="spot" markdown="1">

## <span class="num">4</span> The layout step can change what the model reads

This is the weak spot I measured, because I couldn't find anyone who had counted it.

A model learns to read conversations laid out in one exact way: who is speaking, where
instructions go, how a tool is described, how a tool's answer comes back. Its maker publishes the
chat template that produces that layout. If the app lays the conversation out differently, the
model is reading something it wasn't trained on. It's like being handed a familiar form where the
boxes have moved.

Does that matter? Researchers have shown that formatting alone, such as which separators and
spaces a prompt uses, can move a model's accuracy by up to 76 percentage points on some tasks
([Sclar and others, ICLR 2024](https://arxiv.org/abs/2310.11324)). That study used a different
kind of prompt, so I tested it directly on one model. Given the maker's layout instead of
Ollama's, `qwen2.5` answered 45 more of 1,240 tool questions correctly: 87.0% instead of 83.4%
([the tool test](tool-test.html)).

{% include fig/specimen.html %}

### What I measured, step by step

1. **I picked the models:** the 50 most popular chat models in Ollama's library and the 30 most
   downloaded chat models on Hugging Face, as they were on 22 October 2026.
2. **I set some aside, with a written reason for each.** For example, some makers never published
   a template, so there's nothing to compare against. That left **65 models**: 43 from Ollama's
   library and 22 from Hugging Face. The [results page](results.html) lists every reason.
3. **I wrote twelve harmless practice conversations.** Six of them use tools: a tool list, a tool
   request and its answer, two requests at once, and so on.
4. **I turned each conversation into the text the model reads, three ways,** and compared each with
   the maker's:

<div class="flow" role="img" aria-label="Three versions of the same conversation: from the maker's template, from the copy inside the model file, and from what Ollama uses. Each is compared with the maker's.">
  <div class="node"><b>The maker's template</b><em>published with the model. This is the reference.</em></div>
  <div class="arrow" aria-hidden="true">→</div>
  <div class="node"><b>The copy in the model file</b><em>made when the model was packaged for apps like Ollama</em></div>
  <div class="arrow" aria-hidden="true">→</div>
  <div class="node"><b>What Ollama uses</b><em>often Ollama's own rewritten version</em></div>
</div>

<ol start="5">
<li><strong>I sorted each difference by kind:</strong> a tool's answer missing, an instruction added
or dropped, tools written in another format, and so on. Changes to spaces, line breaks or the date
don't count.</li>
</ol>

For 41 of the 45 library model files, the Ollama step runs Ollama's own code, so nothing is
guessed. For three others, and for the Hugging Face models, it's a close copy written in Python.
All of it ran on my local setup with no GPU and no model downloads: the tool reads only the small
header of each model file (7.3 MB of a multi-gigabyte file for `qwen2.5`).
[How it works](how-it-works.html) explains the method and how it was checked.

### What I found

**In Ollama's library, 32 of 43 models read their tool conversations differently from what
their maker designed.** "Differently" means a change to what the model is told: a tool's answer
missing, an instruction added or dropped, tools described in another format.

In four of the 32, the only change is the order of the fields in a tool's description. That's the
mildest kind, so here's the count without them: **28 of 43**.

Some of these models weren't built for tools at all. Counting only the 19 whose maker's template
does show the model a list of tools: **15 of 19** differ, or **11 of 19** without the
order-only cases.

{% include fig/grid.html %}

**Most differences come from Ollama's own version of the template.** In 24 of the 32, the copy
inside the model file gives the same conversations as the maker's, apart from harmless spacing. In
6, the model file already holds an older copy of the maker's template, and Ollama's version changes
it further. In 2, the model file has no template of its own to compare.

{% include fig/origin.html %}

{% include fig/classes.html %}

**Hugging Face downloads fare better.** For all 22 measured here, Ollama used the template inside
the file instead of its own. Only 5 differ, and in all 5 the difference is already in the
uploaded file. Ollama adds no meaningful change of its own.

**A template that looks different can still be fine.** In 7 of the Hugging Face models, the
template text differs from the maker's, yet all twelve conversations came out exactly the same.
Reading templates side by side doesn't tell you much. Comparing the text the model actually
receives does.

### One model, step by step: `qwen2.5`

`qwen2.5` is the fourth most popular chat model in Ollama's library.
- **The model file holds an outdated template.** It matches the maker's template as it was on
  18 September 2024. The maker updated it the next day.
- **Ollama's version describes tools in the wrong format,** as the figure above shows. The model
  was trained on JSON. It gets the internal format of Go, the programming language Ollama is
  written in. This is already reported to Ollama
  ([issue #14601](https://github.com/ollama/ollama/issues/14601)), and fixes have been proposed.
  The measurement shows how far it reaches: 4 of the 43 library models (`qwen2`, `qwen2.5`,
  `qwen2.5-coder` and `qwen3`).
- **A popular Hugging Face copy loses a default instruction.** In an earlier test of bartowski's
  widely used copy of this model, the template inside the file matched the maker's exactly. But
  Hugging Face supplies its own Ollama-style template for it, and Ollama uses that one. It leaves
  out the short default instruction the maker's template adds when you don't write one yourself.
- **And the layout changes its answers.** On 1,240 tool questions from a public benchmark, the
  same model on the same server got 1,034 right with Ollama's layout and 1,079 with the maker's.
  The biggest gap: with Ollama's layout it more often called a tool when none fitted the question.
  [Read the tool test](tool-test.html).

<div class="views" markdown="1">
<div class="view" markdown="1">

**If you just use AI:** if a local model is clumsy with tools, the layout may be part of the
reason, not only the model. The [results page](results.html) shows which models came out with no
difference at all.

</div>
<div class="view" markdown="1">

**If you build with AI:** run `ollama show --modelfile <model>` to see the package's template; on
0.40.7 or newer, `/api/show` also reports `template_source`. Diff rendered prompts, not template
files. Pin the reference in time: the original as of when? If you depend on tool calling, test it
on the exact package you ship, and set your own `TEMPLATE` in a Modelfile when the shipped one
drifts.

</div>
</div>

<div class="tell" markdown="1">
**How to tell:** the full comparison needs a few more tools and is described in
[How it works](how-it-works.html). The quick check-up covers the parts you can act on: where your
models came from, and whether their templates have warning signs.
</div>
</section>

<section class="spot" markdown="1">

## <span class="num">5</span> Helpers turn the model's words into actions

On its own, a model only writes text. Once you connect a helper that can read files, run commands
or browse, its text becomes actions on your computer. Two things can then go wrong:
- **The model makes a mistake.** The layout problems in point 4 can make that more likely.
- **The model is misled by what it reads.** A web page, an email or a file can contain text
  written to give the AI orders. The model can't reliably tell those apart from yours. This is
  called **prompt injection**. OWASP, a long-standing security community, lists it as the number
  one risk for AI applications
  ([OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)).

Either way, what the helper can reach is what's at risk. Project folders often hold a file called
`.env` with passwords and keys in it, or a private key for logging in to servers.

<div class="views" markdown="1">
<div class="view" markdown="1">

**If you just use AI:** only point an AI helper at the folder it needs, and read what it plans to
do before you let it run commands.

</div>
<div class="view" markdown="1">

**If you build with AI:** treat everything the model reads (pages, files, tool results) as
untrusted input. Give each agent the least access that works, keep secrets in a secret store
rather than the working folder, and ask for approval before actions that are hard to undo.

</div>
</div>

<div class="tell" markdown="1">
**How to tell:** point the check-up at the folder your helper works in. It lists any file whose
name suggests it holds a secret. It reads only the names, never the contents. **What to do:** move
those files out, or give the helper its own folder with only what it needs.
</div>
</section>

<section class="spot" markdown="1">

## <span class="num">6</span> Your chats are kept as ordinary files

"Local" means your conversations stay on your computer. It also means they sit on your disk,
where anything that can read your files can read them too. **What I found myself**, going through
Ollama's code and LM Studio's documentation:
- **Ollama in a terminal** (a window where you type commands) keeps the last 100 lines you typed
  in a file called `.ollama/history` in your home folder, unless you set `OLLAMA_NOHISTORY`
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

<div class="views" markdown="1">
<div class="view" markdown="1">

**If you just use AI:** treat your AI chats like any other private document on your computer.

</div>
<div class="view" markdown="1">

**If you build with AI:** request logging helps while you debug and leaks afterwards. Turn it off
when you're done, and keep chat folders out of shared drives and sync.

</div>
</div>

<div class="tell" markdown="1">
**How to tell:** the check-up lists where your chats are saved and how big those files are,
without opening them. It warns you if the debugging setting is on. **What to do:** delete old
chats you don't need, and set `OLLAMA_NOHISTORY` to `1` to stop the terminal history.
</div>
</section>

## Run the check-up

The check-up looks at all of this on your own computer in about ten minutes. It needs Python and
nothing else. It changes nothing and sends nothing anywhere.

**[Step-by-step instructions →](guide.html)**

## What this shows, and what comes next

- **A clean check-up looks for known warning signs.** It can't prove a model or an app is
  trustworthy.
- **A different layout changes what the model does.** For `qwen2.5`, the maker's layout gave
  about 4 more correct tool answers in every 100 ([the tool test](tool-test.html)). Next: the same
  test on more models, and on conversations with several turns.
- **The measurement is a snapshot.** It covers the most popular models on 22 October 2026, as they
  were that day, with Ollama 0.40.7.
- **Some parts are close copies, not Ollama's own code.** For the Hugging Face models, and for
  three library models, Ollama fills in the template with a separate engine. I reproduced that
  engine's behaviour in Python. It's very close, but not byte-for-byte Ollama.
- **Practice conversations have limits.** Mistral's own template, for example, rejects the made-up
  tool request numbers my practice conversations use, so a few of its comparisons couldn't run.
  The [results page](results.html) lists every gap like this.

## Credits

Kai's video [*Your Local AI Is Not as Private as You Think*](https://www.youtube.com/watch?v=3mx84MRj8lY)
(@kaiexplainsYT, October 2026) gave me the starting point. It covers weak spots 1, 2, 3 and 5 from
the security side, and is worth watching. For those, this page cites the original advisories and
research. The rest is my own work: the measurement of 65 models (weak spot 4), the evidence on old
and rewritten templates (weak spot 3), what Ollama's code exposes on an open port (weak spot 1),
where chats are saved (weak spot 6), the [tool test](tool-test.html), and the check-up.

## Words used on this page

<dl class="gloss">
  <dt>Model</dt><dd>The trained AI itself: a large file of numbers that turns text into more text.</dd>
  <dt>Ollama, LM Studio</dt><dd>Free apps that download models and run them on your own computer.</dd>
  <dt>Hugging Face</dt><dd>The largest public website for sharing AI models. Anyone can upload.</dd>
  <dt>Chat template</dt><dd>The small set of layout instructions that turns a conversation into the one block of text a model reads.</dd>
  <dt>Tool</dt><dd>Something a model can ask to use, such as a calculator, a file reader or a web search.</dd>
  <dt>Server, port</dt><dd>A program that waits for messages from other programs, and the numbered door it listens on (Ollama's is 11434).</dd>
  <dt><code>127.0.0.1</code></dt><dd>The address that means "this computer only".</dd>
  <dt>JSON</dt><dd>A standard, widely used way of writing data so that programs and models can read it.</dd>
  <dt>CVE</dt><dd>The ID given to a published security problem, so everyone can refer to the same one.</dd>
  <dt>Prompt injection</dt><dd>Text hidden in a page, email or file that tries to give an AI orders.</dd>
  <dt>Terminal</dt><dd>A window where you type commands instead of clicking.</dd>
  <dt>Modelfile</dt><dd>Ollama's recipe file for a model. Its <code>TEMPLATE</code> line sets the chat template.</dd>
</dl>

## Sources

- Kai, *Your Local AI Is Not as Private as You Think*, YouTube, October 2026.
- Ollama source code, version 0.40.7: `server/routes.go`, `server/cloud_proxy.go`, `envconfig/config.go`,
  `readline/history.go`, `internal/onboarding/app_state.go`.
- Ollama release notes for 0.23.3 and 0.40.8, and issue #14601.
- GitHub Advisory Database and the US National Vulnerability Database: CVE-2026-7482,
  CVE-2026-42248, CVE-2026-42249, CVE-2024-34359.
- A. Fogel and O. Hofman, chat template backdoors across 18 models and 4 engines, Pillar Security,
  10 February 2026.
- LM Studio documentation, "Manage chats".
- OWASP Top 10 for LLM Applications 2025, LLM01: Prompt Injection.
- Sclar, Choi, Tsvetkov and Suhr, "Quantifying Language Models' Sensitivity to Spurious Features in
  Prompt Design", ICLR 2024.
- This project's measurement runs of 22 October 2026, published with the code on
  [GitHub](https://github.com/MohanVishe/template-drift-audit).
