---
name: vibe-training-modeling
description: Research current strong baselines, SOTA/open-source approaches, and practical GitHub reference repositories for the routed training task, then select a model family, architecture, algorithm, library, or fine-tuning route with tradeoffs, cost, memory, license, and risk. Use after vibe-training-planning.
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: AskUserQuestion, WebSearch, WebFetch, Read, Write, Edit, Bash, PowerShell, Glob, Grep
---

# Modeling

## Goal

Research the current practical frontier for the routed task and choose an implementation route that fits the user's constraints.

## Artifact Location

Read and write phase artifacts under `.claude/vibe-training/runs/<run_id>/`. If no run directory is known, find the latest project-local vibe-training run or create one. Do not write to `~/.claude/plans`.

## Inputs

- `plan.md`
- Task type
- Resource budget
- Input/output shape
- Metric target
- Dataset size and label quality
- Inference constraints
- License constraints

## Outputs

Write or update `model-choice.md` with:

- research notes with sources when current claims are made
- recommended GitHub/reference repositories with rationale
- candidate comparison across simple baselines, strong open-source implementations, and SOTA-style approaches
- primary route
- backup route
- training or adaptation route
- expected memory and serving implications
- large-task framework comparison, when orchestration or post-training complexity matters
- risks and unknowns

## What To Do

1. Research the task family before naming a model or library. Look for current SOTA papers, strong open-source repos, widely used libraries, benchmark leaderboards, and practical baselines.
2. Discover reference repositories dynamically. Search for official implementations, maintained framework examples, model cards that link to training code, benchmark-winning repos, and mature community libraries.
3. When live browsing/search is available, verify current claims from primary or near-primary sources: papers, official docs, model cards, benchmark pages, and maintained repositories. Include links or citations in `model-choice.md`.
4. Score candidate repositories by fit to the task, maintenance recency, stars/downloads only as weak signals, issue activity, license, reproducible examples, training scripts, evaluation scripts, dataset tooling, hardware assumptions, and compatibility with the user's stack.
5. Compare at least three levels when possible: simplest viable baseline, strong practical open-source approach, and frontier/SOTA-style approach.
6. Check capability, dataset fit, license, memory, throughput, training complexity, inference complexity, ecosystem maturity, and deployment fit.
7. Choose a primary route and at least one fallback route.
8. Recommend the adaptation method appropriate to the family: from-scratch training, transfer learning, feature extraction, classical ML, diffusion fine-tuning, LoRA/QLoRA, full fine-tune, prompt/RAG, distillation, RL, or evaluation-only.
9. For large post-training, RL, agent training, distributed fine-tuning, simulation-heavy, or data-generation-heavy tasks, compare SOTA practical frameworks instead of only comparing models. Examples to search and compare by evidence include verl, SMILE, OpenRLHF, TRL, Ray RLlib, DeepSpeed-Chat, and task-specific maintained repos.
10. State the assumptions that should be validated before training.

## Reference Repository Discovery

Do not hardcode one library as the answer for a family. Use prior knowledge only to seed the search.

Use search as part of the modeling phase when the user asks for current SOTA, open-source references, model/library recommendations, or repository selection. Prefer:

- code references: GitHub repositories, official examples, framework examples
- model references: Hugging Face model cards, dataset cards, spaces, official model docs
- paper references: arXiv, OpenReview, conference pages, Papers with Code, official project pages
- framework references: official docs for PyTorch, TensorFlow, JAX, Hugging Face, scikit-learn, Lightning, Ray, and task-specific ecosystems

Search query pattern:

1. `<task> sota open source training GitHub`
2. `<task> benchmark leaderboard`
3. `<task> paper code official implementation`
4. `<task> huggingface model card training`
5. `<candidate library> official examples train fine tune`
6. `<task> framework comparison distributed training RL post-training`
7. `<agent RL> verl slime OpenRLHF TRL benchmark GitHub`

For each promising reference repo, record:

- repository URL
- why it fits this task
- whether it is official, paper-linked, framework-maintained, or community-maintained
- license
- last meaningful maintenance signal
- training entrypoint and config style
- evaluation support
- hardware assumptions
- distributed orchestration support, if relevant
- inference or serving path
- clone/adaptation burden: install difficulty, required CUDA extensions, config system, expected local patches, and upstream divergence risk
- risks

For complex training frameworks, do not treat "GitHub repo exists" as enough. Prefer repos with clear clone/install instructions, pinned examples, active issue resolution, reproducible configs, and a path for local customization without rewriting the framework.

If a known library seems obvious for a route, still verify it against alternatives. For example, a diffusion task may lead to a library such as a maintained diffusion framework, but the selected repo should depend on modality, objective, dataset shape, and current maintenance evidence.

If search tools are unavailable, do not pretend the research is current. Mark SOTA and repository choices as provisional, use stable baseline knowledge, and ask the user to enable web search or provide candidate links when currentness matters.

## Question Policy

Use `AskUserQuestion` when the best route depends on a user-owned tradeoff: accuracy vs speed, research novelty vs maintainability, preferred ecosystem, license constraints, cloud/local deployment, model size limit, or whether to favor GitHub code, Hugging Face models, papers, or managed APIs. Do not ask the user to choose between candidates before you have done enough research to explain the tradeoff.

## Avoid Route Collapse

- Do not turn every vision/audio/OCR/tabular task into an LLM or VLM task.
- Do not use QLoRA/SFT language unless the routed task actually involves LLM/VLM adaptation.
- Do not treat family examples as fixed prescriptions. Families are discovery prompts, not answers.
- For simple educational tasks, prefer concise runnable baselines over heavyweight SOTA.
- For production tasks, separate "best paper result" from "best maintainable implementation."

## Do Not Do

- Do not redesign the data workflow.
- Do not modify training framework internals.
- Do not execute on GPU servers.
