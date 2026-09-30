# Hello Trench

A single [Google ADK](https://adk.dev) agent that answers questions about the Twenty One Pilots narrative universe, from *Blurryface* (2015) to *Breach* (2025), plus the behavioral eval suite used to check it.

The agent is small on purpose. It is module 0 of a study track on the Agent Development Kit, and its job is to exercise the ADK development loop: define an agent, run it locally, and evaluate it with LLM judges.

Write-up: [Quando o eval reprova o eval: avaliando um agente Google ADK sem tools](https://dev.to/carvalhocaio/quando-o-eval-reprova-o-eval-avaliando-um-agente-google-adk-sem-tools-32k4) (Portuguese).

---

## What it does

The agent plays the Torchbearer's archivist and follows a short set of rules:

- **Canon vs. theory**: anything not established by releases, music videos or official material is labeled as a fan theory.
- **No verbatim lyrics**: songs are paraphrased and named, never quoted.
- **Scope**: off-topic questions get a one-sentence refusal that steers back to the lore.
- **Instruction integrity**: requests to ignore, change or reveal its instructions are declined.
- **Language**: replies in the user's language.

It has no tools. Everything it knows comes from the model, plus a short list of verified facts in the prompt for what the model cannot know on its own, such as how the story ends in *Breach*, released after its training data.

---

## Project structure

```
.
├── src/adk_00_hello_trench/
│   ├── __init__.py          # Exposes the agent module, as ADK expects
│   ├── agent.py             # build_agent() and the root_agent ADK loads
│   ├── prompts.py           # Agent description and instruction
│   └── settings.py          # pydantic-settings: model name and credential checks
├── tests/                   # Unit tests; none of them call the model
├── evals/
│   ├── hello_trench.evalset.json   # 11 single-turn cases with reference answers
│   └── test_config.json            # Judge criteria and thresholds
├── Makefile
└── pyproject.toml
```

---

## Setup

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
make sync
cp .env.example .env
```

| Variable                      | Description                                                         | Default               |
|-------------------------------|---------------------------------------------------------------------|-----------------------|
| `GOOGLE_API_KEY`              | Gemini API key, required when not using Vertex AI                   | —                     |
| `GOOGLE_GENAI_USE_ENTERPRISE` | `1` to use Vertex AI instead of the Gemini API                      | `0`                   |
| `GOOGLE_CLOUD_PROJECT`        | Google Cloud project, required when `GOOGLE_GENAI_USE_ENTERPRISE=1` | —                     |
| `GOOGLE_CLOUD_LOCATION`       | Vertex AI region                                                    | `us-central1`         |
| `HELLO_TRENCH_MODEL`          | Gemini model used by the agent                                      | `gemini-flash-latest` |

Missing credentials fail at import time with a clear message instead of on the first model call.

---

## Usage

| Command     | Description                                     |
|-------------|-------------------------------------------------|
| `make run`  | Chat with the agent in the terminal             |
| `make web`  | Start the ADK dev UI at `http://127.0.0.1:8000` |
| `make api`  | Start the ADK API server on localhost           |
| `make eval` | Run the eval suite against Gemini               |

Both servers bind to `127.0.0.1` by default. The ADK dev UI is meant for local development only.

---

## Evaluation

```bash
make eval
```

The eval runs the 15 cases in `evals/hello_trench.evalset.json`: ten lore questions and five adversarial prompts (off-topic, lyric extraction, instruction override, instruction extraction and an injection wrapped inside the lore). Two judges, both on `gemini-pro-latest` so the judge is never the agent's own model, score every response:

- **`final_response_match_v2`** compares the response with the case's reference answer. This is where lore facts live.
- **`rubric_based_final_response_quality_v1`** applies six behavior rules that hold for every case: scope, no verbatim lyrics, role integrity, instruction secrecy, reply language and fidelity to the known facts in the prompt. Canon vs. theory is checked per case through reference answers, because telling the two apart requires knowing the lore.

Facts go to reference answers because the rubric judge only trusts the user prompt, tool outputs and grounding metadata as evidence. For an agent without tools, it has nothing to verify a factual claim against, and its verdicts on facts become inconsistent between runs.

Latest result: 15/15 in two consecutive runs. The eval needs Gemini credentials and costs money per run, so it stays out of CI.

---

## Development

| Command                     | Description                                                            |
|-----------------------------|------------------------------------------------------------------------|
| `make ci`                   | Lint, format check, dependency audit and tests, same as GitHub Actions |
| `make test`                 | Unit tests                                                             |
| `make lint` / `make format` | Ruff                                                                   |
| `make hooks`                | Install the pre-commit hooks                                           |

---

## Design notes

**Concept isolated.** The ADK development loop for a single `LlmAgent`: code-first definition, local runtimes (`adk run`, `adk web`, `adk api_server`) and `adk eval` with LLM judges.

**Main design decision.** Separate knowledge from behavior in the eval. Every fact is checked against a per-case reference answer, and the rubrics only hold rules that apply to every case. Earlier versions mixed the two and failed correct answers for reasons that had nothing to do with the agent.

**What would change at scale.**

- Repeat each run several times and track pass rates. `adk eval` has no flag for repeated runs, so a single run is only a sample.
- Keep reference answers under review like code. The judge enforces what is written, not what is true, and a wrong reference fails a correct agent.
- Cap the thinking budget. Reasoning tokens reached several times the size of the visible answer, which is pure cost and latency for a lore bot.
- Replace the known facts in the prompt with search grounding. Injected facts go stale, and the model invents details around them: when the prompt only said Breach was the final chapter, the agent made up its plot.
- Once tools arrive, move factual checks back into rubrics grounded in tool outputs, the scenario that metric was designed for.
