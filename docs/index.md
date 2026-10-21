---
layout: default
title: Is your local AI safe?
description: Running AI on your own computer keeps your words private, but private is not the same as safe. Five plain questions to ask about your setup, a free check-up that answers them, and a measurement of popular models.
---

# Is your local AI safe?

<p class="lede">Running an AI model on your own computer keeps your words away from big companies.
That's a real benefit. But private and safe aren't the same thing. Here are five plain questions
to ask about your setup, a free check-up that answers them in ten minutes, and what I found when I
measured 65 popular models.</p>

## Private is not the same as safe

Apps like **Ollama** and **LM Studio** let you download an AI model and run it on your own machine.
Nothing you type goes to a company's servers, and nobody trains on your chats. For many people,
that's the whole reason to do it.

Think of it like hiring a helper who works inside your home instead of calling a call centre. Your
conversations stay in the house. But you would still want to know:
- who else can walk in;
- whether the locks are up to date;
- who the helper really is;
- what's lying on the desk they work at.

There's one more question, which almost nobody asks: does the helper hear your instructions the way
they were trained to?

Those are the five questions below. Each one has a check you can run yourself, and none of them
needs technical knowledge.

---

## 1. Who else can talk to your AI?

Ollama answers requests on your computer, and it has **no password**. By default it only listens to
your own computer, which is the safe setting (it's written into Ollama's code as `127.0.0.1`, which
means "this machine only"). That changes if someone changes the `OLLAMA_HOST` setting. Some
how-to guides tell you to, so that another device can use your model. LM Studio has a similar
switch called **Serve on Local Network**.

Once that door is open, anyone who can reach your computer can use the AI, and anything the AI can
reach. This is not a rare mistake:
- **175,108.** That's how many Ollama servers researchers at SentinelOne and Censys found
  answering the open internet over 293 days of scanning
  ([SentinelOne](https://www.sentinelone.com/labs/silent-brothers-ollama-hosts-form-anonymous-ai-network-beyond-platform-guardrails/)).
- **Some tools open the door themselves.** In August 2026, Cyera showed that NVIDIA's NemoClaw
  agent tool started Ollama listening on every network so its sandbox could reach it. A single
  visit to a malicious web page could then quietly change how the local model behaved
  ([Cyera](https://www.cyera.com/research/nemoclaw-one-website-visit-to-hijack-your-ai-agent)).

**The check:** the check-up looks at which network addresses your AI apps are listening on, and
warns you if anything other than your own computer can connect.

## 2. Is your AI software up to date?

Ollama is software, and software has bugs. Two published ones matter here:
- **Bleeding Llama** (CVE-2026-7482). A specially made model file, uploaded to an exposed Ollama,
  could make it leak pieces of its memory: other chats, system instructions, even passwords stored
  in its settings. It was fixed in Ollama **0.17.1**
  ([Cyera](https://www.cyera.com/blog/bleeding-llama-a-critical-memory-leak-in-the-worlds-most-popular-local-ai-platform),
  [Mondoo](https://mondoo.com/blog/three-ollama-cves-bleeding-llama-and-windows-updater-flaws)).
- **The Windows auto-updater** (CVE-2026-42248 and CVE-2026-42249). Ollama for Windows didn't
  check that an update really came from Ollama. It was fixed in **0.23.3**
  ([Mondoo](https://mondoo.com/blog/three-ollama-cves-bleeding-llama-and-windows-updater-flaws)).

The latest Ollama at the time of writing is 0.40.8 (21 October 2026).

**The check:** the check-up asks your running Ollama for its version number and tells you if it is
older than these fixes.

## 3. Who made your model?

A model file is like a recipe book with no author's name inside it. Anyone can publish one, and
some people publish convincing fakes:
- **Fake downloads.** In May 2026, a fake copy of an OpenAI tool reached number one on Hugging
  Face's trending list before it was taken down. Running its setup file installed software that
  stole saved passwords and crypto wallets. HiddenLayer, who found it, believe its download numbers
  were inflated
  ([HiddenLayer](https://hiddenlayer.com/research/malware-found-in-trending-hugging-face-repository-open-oss-privacy-filter)).
- **Hidden behaviour in the model itself.** In October 2026, ProjectDiscovery trained a popular
  7-billion-parameter model to behave perfectly in 50 out of 50 normal tests, and to misuse its
  tools when it saw a secret phrase. It cost about $8 of computer time
  ([ProjectDiscovery](https://projectdiscovery.io/research/how-abliterated-models-can-get-you-pwned)).
- **It takes very little.** Anthropic and the UK AI Security Institute found that about 250 poisoned
  documents were enough to plant a hidden trigger in models of very different sizes
  ([Anthropic](https://www.anthropic.com/research/small-samples-poison)).

A model can't do anything by itself. It only produces text. The risk appears when you let it use
tools: run commands, read files, browse the web.

**The check:** the check-up lists where each of your models came from: Ollama's own library, or a
named person or group on Hugging Face.

## 4. What can your AI reach?

AI "agents" and coding helpers work inside a folder you choose. Whatever is in that folder, they can
read. Many project folders hold a file called `.env` with passwords and keys in it, or a private key
for logging in to servers. Those are exactly the files a tampered model would be told to send away.

**The check:** point the check-up at the folder your AI helper uses. It lists any file whose name
looks like it holds a secret. It reads only the names and never opens the files.

## 5. Is your model hearing you correctly?

This is the question I set out to measure.

Every model is trained to read conversations laid out in one exact way: who is speaking, where the
instructions go, how a tool is described. The model's maker publishes a small program called a
**chat template** that produces that layout. Every app that runs the model has to reproduce it
exactly. If it doesn't, the model is reading a format it wasn't trained on. That's like getting a
form where the boxes have moved.

The template also travels inside the model file, which is why it has become a target. Researchers at
Pillar Security showed that a tampered template can hide instructions that switch on only when you
type certain words. It worked in four different AI apps, Ollama included, and the tampered files
passed Hugging Face's automatic scans. Their advice is to compare a model's template against the
maker's original
([Pillar Security](https://www.pillar.security/blog/from-discovery-to-large-scale-validation-chat-template-backdoors-across-18-models-and-4-engines)).

How common are tampered templates in practice? Rare, as far as anyone has looked. A scan of more
than 137,000 published templates by the makers of the c4nary scanner found 28 dangerous ones. Its
authors describe all of them as research and test files ([c4nary](https://pypi.org/project/c4nary/)).

So I measured the everyday problem instead: **when nobody is attacking anything, is the text your
model reads in Ollama the text its maker designed?**

### What I measured

For each model, I compared three versions of the layout:

1. **The maker's original** template.
2. **The copy inside the model file.**
3. **What Ollama actually uses.** Ollama packages often carry their own rewritten version.

I ran twelve harmless practice conversations through all three and compared the exact text the
model would receive. Six of the conversations involve tools, because that's where a model's
mistakes have consequences. The comparison uses Ollama's own code for the Ollama step, so nothing
is guessed. [How it works](how-it-works.html) explains the method and how it was checked.

### What I found

I took the 50 most popular chat models in Ollama's library and the 30 most downloaded chat models
on Hugging Face, as they were on 22 October 2026. Some couldn't be compared fairly, for example
because the maker never published a template. That left **65 models**. The full list, with every
reason, is on the [results page](results.html).

**In Ollama's own library, 32 of 43 models read their tool conversations differently from what
their maker designed.** "Differently" here means a change that alters what the model is told: a
missing tool result, an added or missing instruction, tools described in another format. Changes
to spaces, line breaks or the date don't count.

Four of those 32 differ only in the order of the fields in a tool's description. That is the
smallest kind of change, so here is the count without them as well: **28 of 43**.

Some of these models were never built for tools. Counting only the 19 whose maker's template is
designed to show the model a list of tools: **15 of 19** differ, or **11 of 19** without the
order-only cases.

**Where the differences come from:**
- In 24 of the 32, the model file matches the maker's template. The difference was introduced by
  the version that Ollama ships with the model.
- In 6, the model file itself already carries an older copy of the maker's template, and Ollama's
  version changes things further.
- In 2, the model file has no template of its own to compare.

**What changes most often** (out of the 28):
- **Tool results** (20 models). The answer that came back from a tool is laid out differently,
  merged with other text, or left out.
- **Default instructions** (10). A short standing instruction is added that the maker didn't write,
  or one the maker wrote is dropped.
- **Tool calls** (10). The model's own earlier request to use a tool is written back differently.
- **The tool list itself** (7). The tools aren't shown to the model at all in some conversations.

**Hugging Face downloads look better, for a simple reason.** When you download a model from Hugging
Face, Ollama uses the template inside the file instead of writing its own. There, 5 of 22 models
differ, and in all 5 the difference is already inside the file that was uploaded. Ollama's handling
added no further meaningful change. Two of them, for example, are custom versions of other models.
Their uploader replaced the maker's instructions for using tools with their own wording and added a
standing instruction about answer style. That's a visible choice the uploader made, not an attack,
but it means the model reads text its original maker never wrote.

**Comparing templates by eye is not enough.** In 7 of the Hugging Face models, the template text
inside the file differs from the maker's. Yet on all twelve practice conversations, the text the
model would read came out exactly the same. A different-looking template isn't necessarily a
problem. The reliable test is to compare what the model actually receives, which is what this
measurement does.

**Old copies are common.** In 9 of the 45 Ollama library model files I could check, the template
inside is an older version of the maker's. One example is `falcon3`: its file matches the maker's
template from 17 December 2024. The next day, the maker published a change titled "fix
chat_template for tool use".

**One example, step by step: `qwen2.5`, the fourth most popular chat model in Ollama's library.**
(Its default download is the 7-billion-parameter instruct model.)
- **The copy inside the model file is out of date.** It matches the maker's template as it was on
  18 September 2024. The maker updated the template the next day. Nobody tampered with anything:
  the file was simply made before the update.
- **Ollama's version describes tools in the wrong language.** The model was trained to read tool
  descriptions written in JSON, a standard format. Ollama's version hands them over in the internal
  format of Ollama's programming language, with words like `<nil>` mixed in. This is already
  reported to Ollama
  ([issue #14601](https://github.com/ollama/ollama/issues/14601)), and fixes have been proposed.
  What the measurement adds is how many popular models it reaches: 4 of the 43 in the library
  (`qwen2`, `qwen2.5`, `qwen2.5-coder` and `qwen3`).
- **The same model from Hugging Face loses its default instructions.** Downloaded through Hugging
  Face instead, the model file matches the maker's template exactly. But the version Ollama builds
  for it leaves out the short default instruction the maker's template adds when you don't write
  one yourself.

None of this is an attack. But it means "I'm running the official model" doesn't guarantee "the
model is reading what its maker intended", especially when tools are involved.

---

## Run the check-up

The check-up answers questions 1 to 5 for your own computer in about ten minutes. It needs Python
and nothing else, it changes nothing, and it sends nothing anywhere.

**[Step-by-step instructions →](guide.html)**

## What this does not tell you

- **A clean check-up is not a guarantee.** It looks for known warning signs. It can't prove that a
  model is trustworthy.
- **A difference in layout is not proof of harm.** It shows the model reads something it wasn't
  trained on. How much that costs in practice, for example in correct tool use, is a separate
  question.
- **The measurement is a snapshot.** It covers the most popular models on 22 October 2026, as they
  were that day.
- **Two parts are close copies, not Ollama's own code.** For Hugging Face downloads, and for three
  library models, Ollama fills in the template with a separate engine. I reproduced that engine's
  behaviour in Python. It's very close, but it isn't byte-for-byte Ollama.
- **Practice conversations have limits.** Mistral's own template, for example, rejects the made-up
  tool request numbers my practice conversations use, so a few of its comparisons couldn't run.
  The [results page](results.html) lists every gap like this.

## Sources

- SentinelOne SentinelLABS and Censys, exposed Ollama hosts (updated March 2026).
- Cyera, *Bleeding Llama* (May 2026) and *NemoClaw* (August 2026).
- Mondoo, three Ollama CVEs (May 2026).
- HiddenLayer, malware in a trending Hugging Face repository (May 2026).
- ProjectDiscovery, backdoored tool-calling models (October 2026).
- Anthropic, UK AI Security Institute and the Alan Turing Institute, poisoning with a small number
  of samples (October 2025).
- Pillar Security with Fujitsu Research of Europe, chat template backdoors (February 2026).
- Actual Intelligence, c4nary scanner and its scan results (2026).
- Ollama source code v0.40.7 and issue #14601.

This piece grew out of a conversation started by Kai's video
[*Your Local AI Is Not as Private as You Think*](https://www.youtube.com/watch?v=3mx84MRj8lY),
which argues that local AI's risks come from what you download and what you connect it to. The
check-up, the measurement and the findings here are my own.
