# Getting Started

This guide walks through the local AI security labs and the separate web bot protection demo. You do not need to install Python packages. The first two AI labs use a model running on your computer. The third and fourth AI labs are deterministic simulations and do not use a model.

## What you need

- A computer running macOS, Windows, or Linux
- Git, if you need to download the repository
- Python 3.9 or newer
- Ollama for the prompt injection labs
- An internet connection for the initial model download

The bot protection demo also needs internet access while it is running. It loads the Cloudflare Turnstile widget and verifies its test tokens with Cloudflare.

## 1. Open a terminal

On macOS, open **Terminal** from Applications or Spotlight. On Windows, open **PowerShell**. On Linux, open your usual terminal.

## 2. Download or open the repository

If you have not downloaded the repository yet, run:

```bash
git clone https://github.com/razi-rais/Anatomy-of-Cyberattack.git
cd Anatomy-of-Cyberattack
```

If you already cloned it, open a terminal in the `Anatomy-of-Cyberattack` folder instead.

Confirm Python is available:

```bash
python3 --version
```

Use Python 3.9 or newer. On Windows, if `python3` is not recognized, try `python --version` and use `python` in place of `python3` in the commands below.

No `pip install` step is needed for these exercises.

## 3. Install and start Ollama

The direct and indirect prompt injection labs send requests to a model running locally through Ollama. The supplied exercises do not send prompts to a hosted model service.

1. Download Ollama from [ollama.com/download](https://ollama.com/download) and install it for your operating system.
2. Open the Ollama application and leave it running.
3. In a new terminal window, confirm the command is available:

```bash
ollama --version
```

If the command is not found, finish opening the Ollama application and open a new terminal window.

## 4. Download the model once

From any terminal directory, run:

```bash
ollama pull qwen2.5:1.5b
```

This requires internet access and downloads the model to your computer. Confirm it appears in the local model list:

```bash
ollama list
```

The examples use this model. Model responses can vary, so your output may not exactly match the examples in the exercise READMEs.

## 5. Start the AI lab browser app

In the terminal where you opened the repository, start the shared lab app:

```bash
cd exercises/LLM
python3 serve.py
```

Keep this terminal window open while you use the app. If a browser does not open automatically, visit <http://localhost:8000>.

Choose an exercise from the **Exercise** menu:

1. **Direct Prompt Injection** shows how crafted user input can try to override a chatbot’s instructions.
2. **Indirect Prompt Injection** shows how instructions hidden in a document can affect a summarizer.
3. **Excessive Agency** shows how overly broad tool permissions can enable unsafe actions.
4. **Unbounded Consumption** simulates how request bursts and oversized inputs or outputs can use up AI resources.

Use the **Defense layer** control to compare the exercise with defenses turned off and on. The first two exercises use the local Ollama model. The third uses a deterministic mock agent. Its delete, email, and refund actions are simulated. They do not modify real records, send email, or move money. The fourth simulates resource use without calling a model or incurring a charge. At the bottom of the app, open the collapsible visual sequence to see each attack path and the control that stops it.

To stop the browser app, return to its terminal window and press **Ctrl+C**.

## 6. Run an AI lab from the command line

You can run an exercise without the shared browser app. Open a new terminal window, start from the repository folder, and choose one lab.

### Direct Prompt Injection

```bash
cd exercises/LLM/01-prompt-injection
python3 run_lab.py
```

Compare the defended run:

```bash
python3 run_lab.py --defended
```

### Indirect Prompt Injection

```bash
cd exercises/LLM/02-indirect-prompt-injection
python3 run_lab.py
```

Compare the defended run:

```bash
python3 run_lab.py --defended
```

### Excessive Agency

```bash
cd exercises/LLM/03-excessive-agency
python3 run_lab.py
```

Compare the defended run:

```bash
python3 run_lab.py --defended
```

This exercise does not require Ollama. Its actions are simulated.

### Unbounded Consumption

Select **4. Unbounded Consumption** in the shared browser app. Try each preset with the Defense layer turned off, then turn it on and compare the simulated usage. No model is called and no cost is incurred.

## 7. Run the tests

Run each command from the directory shown.

The direct prompt injection tests can include live requests to your local model when Ollama is available:

```bash
cd exercises/LLM/01-prompt-injection
python3 -m unittest -v
```

The indirect prompt injection tests can also include live requests to your local model:

```bash
cd exercises/LLM/02-indirect-prompt-injection
python3 -m unittest -v
```

The excessive agency tests are deterministic and do not contact a model:

```bash
cd exercises/LLM/03-excessive-agency
python3 -m unittest -v
```

The shared browser app tests, including the unbounded consumption usage limits, are deterministic and do not contact a model:

```bash
cd exercises/LLM
python3 -m unittest test_labkit -v
```

## 8. Try the bot protection demo

This is a separate exercise. It needs internet access because the browser loads the Cloudflare Turnstile widget and the local server sends test tokens to Cloudflare for verification. The supplied public test keys are sufficient. You do not need to create an account or add a secret.

From the repository folder, run:

```bash
cd exercises/bots
python3 server.py
```

If the browser does not open automatically, visit <http://localhost:8001>. Follow the **Human**, **Bot**, and forged token examples in the page. The server listens on your local computer. Keep it local and stop it with **Ctrl+C**.

The optional bot test suite includes live Cloudflare checks when the network is available. Running those tests sends test data to Cloudflare:

```bash
python3 -m unittest -v
```

## About the other materials

The `exercises/deepfakes` folder contains reference material and media. It is not a runnable software lab. The PDF reports in the repository are optional reading.

## If something does not work

- **`python3` is not found:** Install Python 3.9 or newer. On Windows, try `python` instead.
- **`ollama` is not found:** Open or install Ollama, then open a new terminal window.
- **The model cannot be reached:** Make sure the Ollama application is running. Check `ollama list` and repeat `ollama pull qwen2.5:1.5b` if the model is missing.
- **The browser app does not open:** Enter `http://localhost:8000` for the AI labs or `http://localhost:8001` for the bot demo in your browser.
- **A port is already in use:** Stop the other local app using that port, then try again.
- **An attack does not produce the exact expected model response:** Results depend on the local model. Compare the behavior and evidence rather than relying on identical wording.

Use these exercises only on your own computer. Do not apply the techniques to systems without authorization.

---

Created by [**Razi Rais**](https://razibinrais.com) · Licensed under the [MIT License](LICENSE).
