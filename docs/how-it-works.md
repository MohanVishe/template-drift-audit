---
layout: default
title: How it works
description: How the template measurement was made, in plain words first and in technical detail after.
---

# How it works

## The short version

A chat model is trained to read text laid out in one exact way. Think of a form where every box
has its place. The model's maker publishes a small program, the **chat template**, that lays your
conversation out in that format.

By the time your words reach a model in Ollama, that layout has been copied twice:

1. **The maker's original.** It lives on the maker's Hugging Face page.
2. **The copy inside the model file.** It's made when someone converts the model into the GGUF
   file format that Ollama and similar apps use.
3. **What Ollama actually uses.** Ollama packages often carry their own version of the template,
   in a different language (Go instead of Jinja). A rule inside Ollama decides which one to use.

The project writes the same twelve harmless practice conversations through all three, and
compares the exact text the model would receive. When the texts differ, it sorts the difference
into a plain category. For example:
- "the default instructions were dropped";
- "tool descriptions arrive in a form that isn't JSON";
- "only spacing changed".

## What makes the numbers trustworthy

- **Ollama's own code does the Ollama step.** A small helper program loads Ollama's real
  template code (version 0.40.7) and runs it, so nothing is guessed.
  - It was checked against a real, isolated Ollama: the texts matched byte for byte on 12 of 12
    practice conversations.
  - The rule Ollama uses to pick a template was copied line by line. It passes all nine of
    Ollama's own tests for that rule.
- **No model is ever run, and no large file is downloaded.** Only the first few megabytes of each
  model file, where the template is stored, are read over the internet.
- **The sorting was checked by hand first.** 52 differences were labelled by hand before the
  sorting code existed.
  - The code's rules were tuned on half of them and then frozen.
  - Then it was scored once on the other half: it agreed with the hand labels on 28 of 28.
- **Old problems aren't presented as new.** Differences that are already reported to Ollama are
  marked with a link to the existing report.
- **Every number has a source.** Each figure on this site comes from a saved run or from a cited
  publication, and every download is logged with its address, time and size.

## How the check-up decides

The quick [check-up](guide.html) is separate from the measurement. It only reads:
- **Network:** the list of open network ports your computer already keeps, to see which address
  each AI app listens on.
- **Version:** Ollama's version number, asked from Ollama itself on `127.0.0.1`. That's the only
  connection the check-up makes.
- **Models:** the names and chat templates of your installed Ollama models.
- **Secrets:** the names of files in the folder you point it at.
- **Saved chats:** whether the usual chat files exist, and their sizes.

It never opens a file's contents, apart from your models' chat templates, and it changes no
settings.

## Running the full measurement yourself

This part is for people comfortable with a terminal. The quick [check-up](guide.html) needs none
of it.

You need:
- Python 3.12 or newer, with `jinja2`.
- The Go helper, built on Linux or in WSL on Windows:

  ```
  bash go-helper/build.sh
  ```

  Set `TDA_WSL_DISTRO` and `TDA_GO_HELPER` if your setup differs from the defaults.

Install the project:

```
pip install -e .
```

Then run any of these:

```
tda local
```

```
tda library --mapping population/mapping.yaml
```

```
tda hf --mapping population/mapping.yaml
```

```
tda report runs/<run-id>
```

- `tda local` compares the models on this computer.
- `tda library` compares the popular Ollama library models.
- `tda hf` compares the popular Hugging Face models.
- `tda report` rebuilds a run's report.

## The technical record

The design and each stage's results are kept in the repository, in the order they were made:
- [DESIGN.md](https://github.com/MohanVishe/template-drift-audit/blob/main/DESIGN.md): what is
  measured and why, and the threats to validity.
- [P0-RESULTS.md](https://github.com/MohanVishe/template-drift-audit/blob/main/P0-RESULTS.md): the
  feasibility spike, and the live check against a real Ollama.
- [P1-RESULTS.md](https://github.com/MohanVishe/template-drift-audit/blob/main/P1-RESULTS.md): the
  classifier, the hand-labelled set and the pipeline.
- [P2-RESULTS.md](https://github.com/MohanVishe/template-drift-audit/blob/main/P2-RESULTS.md): the
  measurement of the popular models, the hand review, and the check-up's warning rate.
- [labels/GUIDE.md](https://github.com/MohanVishe/template-drift-audit/blob/main/labels/GUIDE.md):
  every category, with its meaning.
- [population/README.md](https://github.com/MohanVishe/template-drift-audit/blob/main/population/README.md):
  how the 80 popular models were chosen and matched to their makers.
