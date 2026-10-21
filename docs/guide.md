---
layout: default
title: Run the check-up yourself
description: Step-by-step instructions for running the local AI safety check-up on Windows, Mac or Linux. About ten minutes, no technical background needed.
---

# Run the check-up yourself

This takes about ten minutes. You don't need to know how to program. You'll download one folder,
type one line, and read the answers.

**What the check-up does:** it looks at the six weak spots described in the
[article](index.html) on your own computer, and tells you in plain words whether any of them needs
attention.

**What it never does:**
- It never changes your settings.
- It never sends anything over the internet.
- It never opens your private files or your chats. It only looks at their names and sizes.

You can read every line of it on [GitHub](https://github.com/MohanVishe/template-drift-audit).

---

## Step 1: Get Python (one time only)

The check-up is written in Python, a free program many tools use.

- **Windows:**
  1. Go to [python.org/downloads](https://www.python.org/downloads/) and click the yellow
     **Download Python** button.
  2. Run the installer.
  3. On the first screen, **tick "Add python.exe to PATH"**, then click **Install Now**.
- **Mac:**
  1. Go to [python.org/downloads](https://www.python.org/downloads/), download the macOS installer
     and open it.
  2. Click through the installer.
- **Linux:** Python is almost always already installed.

## Step 2: Download the check-up

1. Open [github.com/MohanVishe/template-drift-audit](https://github.com/MohanVishe/template-drift-audit).
2. Click the green **Code** button, then **Download ZIP**.
3. Find the ZIP in your Downloads folder and unzip it:
   - **Windows:** right-click it and choose **Extract All**.
   - **Mac:** double-click it.

You now have a folder called `template-drift-audit-main`.

## Step 3: Open a terminal in that folder

A terminal is a window where you type commands.

- **Windows:** open the `template-drift-audit-main` folder. Right-click an empty spot inside it and
  choose **Open in Terminal**. On older Windows, click the address bar at the top of the folder
  window, type `cmd` and press Enter.
- **Mac:** right-click the folder and choose **Services → New Terminal at Folder**. If you don't
  see that option, open **Terminal**, type `cd ` (with a space after it), drag the folder into the
  window and press Enter.
- **Linux:** right-click inside the folder and choose **Open in Terminal**.

## Step 4: Start your AI app

If you use **Ollama** or **LM Studio**, open it now. The check-up can only see a server that's
running.

## Step 5: Run the check-up

Type this line and press Enter.

**Windows:**

```
python -m tda check
```

**Mac and Linux:**

```
python3 -m tda check
```

On Windows, if a Microsoft Store window opens instead, Python isn't installed yet. Go back to
Step 1 and make sure you ticked **Add python.exe to PATH**.

### Also check the folder your AI helper works in

AI coding helpers and agents read the folder you point them at. To check that folder, add
`--folder` and the folder's location in quotes:

```
python -m tda check --folder "C:\Users\you\Documents\my-project"
```

On a Mac, the location looks like `"/Users/you/Documents/my-project"`. Use `python3` instead of
`python`.

**Tip:** you don't have to type the location. Type everything up to and including `--folder `,
then drag the folder into the terminal window.

---

## Reading the answers

Each answer starts with a mark:

| Mark | Meaning |
|---|---|
| `[OK]` | All good. |
| `[!!]` | Worth fixing. The line underneath says why, and **What to do** says how. |
| `[--]` | Couldn't check. Usually your AI app wasn't open. |

Here's what each check means, and what to do if it shows `[!!]`:

### "A local AI server is reachable from other devices"

Your AI app answers other devices, not just this computer. Ollama has no login, so anyone who
can reach it can chat with your models, add new ones or delete them.

**Fix (Ollama):** find the setting called `OLLAMA_HOST`. On Windows, search the Start menu for
"environment variables". Either delete the setting or set it to `127.0.0.1`. Then quit Ollama and
open it again.

**Fix (LM Studio):** in the server settings, turn off **Serve on Local Network**.

**Really need it on another device?** Ask someone technical to put a login in front of it. Don't
leave the port open.

### "Ollama … is missing published security fixes"

Your version has known security problems that newer versions fix. The message lists which ones.

**Fix:** download the latest Ollama from [ollama.com](https://ollama.com) and install it over the
old one. Your models stay where they are.

### "… models come from outside Ollama's library"

Anyone can upload a model to Hugging Face, and the uploader decides what instructions travel with
it. That matters most when the model can use tools: run commands, read files or browse.

**Fix:** for anything that uses tools, prefer the model maker's official release or Ollama's own
library.

### "… model templates have something worth a look"

Every model file carries a small set of instructions called a chat template. It decides exactly
what text the model reads. The check looks for two unusual things in it:
- a web address;
- a rule that reacts when you type particular words.

Both could let a template behave differently from what you expect. This doesn't prove the model
is bad. It means a person should look.

For a sense of how often it happens: I ran this same check over 95 different templates from
popular models. It flagged 3. All three turned out to be ordinary, visible features, such as
typing a special word to switch the model's "thinking" mode on or off. So expect this message to be
rare, and expect most cases to be harmless once someone reads them.

**Fix:** if you didn't expect it, remove the model (`ollama rm <name>`) and get it from the
maker's official source.

### "… secret-looking files in …"

Files such as `.env`, `id_rsa` or `*.pem` usually hold passwords and keys. An AI helper working in
that folder can read them.

**Fix:** move them out of the folders you let an AI helper work in, or give the helper its own
folder with only what it needs.

### "Ollama is set to save a copy of every request"

A debugging setting called `OLLAMA_DEBUG_LOG_REQUESTS` is switched on. While it's on, Ollama
writes the full text of every chat request to a folder in your temp folder.

**Fix:** delete the setting the same way as `OLLAMA_HOST` above, quit and reopen Ollama, then
delete the folders whose names start with `ollama-request-logs-` in your temp folder.

### "Your conversations are kept in … place(s)"

This one is marked `[--]`, because it's information, not a fault. It lists where your chats are
saved and how big those files are. Anyone who uses your account, and any backup or sync tool,
can read them.

**What you can do:** delete old chats you don't need from inside the app. To stop Ollama keeping
a history of what you type in a terminal, add a setting called `OLLAMA_NOHISTORY` with the value
`1`, the same way as `OLLAMA_HOST` above.

---

## Want to go deeper?

The check-up is the quick version. The same project also measures something harder to see:
whether the prompt Ollama gives a model is the prompt its maker designed. That part needs a few
more tools and is described in [How it works](how-it-works.html).
