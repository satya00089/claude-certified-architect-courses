# Claude Certified Architect – Foundations

![Claude Certified Architect - Foundations](public/claude-certified-architect-foundations.png)

> Independent study guide and practice repository for **Claude Certified Architect – Foundations**.

This repository contains structured study materials, practical notes, and hands-on examples for developers, architects, and AI engineers preparing for the **Claude Certified Architect – Foundations** certification.

It is designed to help learners understand the core concepts, workflows, and implementation patterns commonly associated with Claude-based production systems.

> This is an independent educational resource and is **not** an official Anthropic repository.

---

## Why this repository exists

People looking for **Claude Certified Architect – Foundations** resources often have to piece information together from scattered documentation, examples, and tutorials.

This repository aims to make that easier by organizing useful learning material in one place.

---

## What's included

- Study notes
- Hands-on exercises
- Code examples
- Certification-aligned domain coverage
- Prompting and context management examples
- Practical Claude API workflows

---

## Exam Overview

| Detail | Info |
|--------|------|
| Format | Multiple choice (1 correct, 3 distractors) |
| Scoring | Scaled score of 100–1,000 |
| Passing Score | 720 |
| Scenarios | 4 out of 6 selected at random |
| Penalty for Guessing | None |

---

## Content Domains & Weightings

| Domain | Weight |
|--------|--------|
| Agentic Architecture & Orchestration | 27% |
| Tool Design & MCP Integration | 18% |
| Claude Code Configuration & Workflows | 20% |
| Prompt Engineering & Structured Output | 20% |
| Context Management & Reliability | 15% |

---

## Start Here

If you're new, follow this order:

1. Claude API basics
2. Multi-turn conversations
3. System prompts
4. Prompt engineering
5. Structured output
6. Streaming
7. Evaluation and practice
8. Architecture concepts

Recommended first folder:

```text
accessing-claude-with-the-api/001_requests
```

---

## Repository Structure

```text
claude-certified-architect-foundations/
├── accessing-claude-with-the-api/
│   ├── 001_requests/
│   ├── 002_multi_turn_conversations/
│   ├── 003_chat_exercise/
│   ├── 004_system_prompts/
│   ├── 005_system_prompts_exercise/
│   ├── 006_temperature/
│   ├── 007_streaming/
│   └── 008_structured_data/
├── prompt-evaluation/
├── public/
├── LICENSE
└── README.md
```

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/satya00089/claude-certified-architect-foundations.git
cd claude-certified-architect-foundations
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the environment

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

Install dependencies inside the module you want to run.

Example:

```bash
cd accessing-claude-with-the-api/001_requests
pip install -r requirements.txt
```

> Note: Each folder has its own `requirements.txt`. Install per module as needed.

---

## Suggested Study Approach

1. Read the topic folder
2. Run the example code
3. Modify prompts and parameters
4. Observe the outputs
5. Compare behaviors
6. Keep your own notes

This repository is most useful when treated as a **practice lab**, not just reading material.

---

## Useful Official References

Helpful areas to review alongside this repository:

- Anthropic documentation
- Claude API docs
- Claude Code docs
- Model Context Protocol (MCP) docs
- Anthropic certification / learning resources

---

## What's not included

- Official exam questions
- Brain dumps
- Leaked proprietary content
- Guaranteed exam answers
- Official Anthropic certification materials

---

## Disclaimer

This repository is an **independent educational resource** created for learning and practice.

It is **not affiliated with, endorsed by, or officially maintained by Anthropic**.

All trademarks, product names, and platform names belong to their respective owners.

If you are preparing for any certification, always verify the latest requirements and domain coverage using official sources.

---

## Support

If this repository helps you:

- Star the repo
- Fork it for your own notes
- Share it with others who may find it useful
