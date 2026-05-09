---
name: vibe-training-planning
description: Route and plan a broad model-training task by clarifying the problem family, inputs/outputs, constraints, success metrics, phase order, risks, and deliverables. Use for the first phase of any ML/CV/NLP/speech/OCR/diffusion/generative modeling/recommender/time-series/RL/LLM/VLM or emerging training/evaluation project.
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: AskUserQuestion
---

# Planning

## Goal

Convert the user's training idea into a clear task route, task definition, and execution sequence.

## Inputs

- User goal
- Product or research scenario
- Budget
- Timeline
- Target metrics
- Deployment constraints
- Input/output examples
- Existing data or dataset preference
- Framework preference
- Whether implementation/execution is wanted now

## Outputs

Write or update project-local `plan.md` and `state.md` under `.claude/vibe-training/runs/<run_id>/` with:

- task definition
- task family and route
- assumptions and open questions
- target user or benchmark
- success criteria
- constraints
- risks
- phase order
- next skill to use

`state.md` must also include the visible gate: current phase, next action, files that may be edited, commands that may be run, user approvals needed, and stop conditions.

## What To Do

1. Route the task by problem family before choosing models. Consider classic ML, CV, OCR/handwriting, speech, NLP, diffusion/generative modeling, recommendation/search, time series, RL/control, graph/scientific ML, LLM/VLM, data-only, evaluation-only, or other/unknown/emerging.
2. Clarify the input/output contract: what goes in, what should come out, label space, examples, and acceptable errors.
3. Ask only user-owned questions when ambiguity blocks routing. Examples: data availability, framework preference, deployment target, metric priority, compute budget, and whether to implement now.
4. Define the desired behavior change and the failure modes the user wants to reduce.
5. List hard constraints: license, privacy, budget, GPU/CPU type, time, latency, memory, deployment target.
6. Define measurable success criteria and stop conditions.
7. Choose or create the project-local workflow directory.
8. Identify the next phase and what evidence it needs.

## Question Policy

Use `AskUserQuestion` early when routing depends on user intent. Batch related questions together and avoid asking what can be discovered from files or search. Good planning questions include task type, data availability, metric priority, framework preference, compute budget, deployment target, and whether the user wants implementation now.

## Routing Heuristics

- Treat the route list as open-ended. If the request does not fit known buckets, create an `other/<short-label>` route and define what evidence modeling must gather.
- Handwritten digit recognition usually routes to CV/OCR baselines first, such as MNIST with a CNN or lightweight ViT, not an LLM.
- Diffusion or generative media tasks route to generative modeling first, then modeling should discover the best maintained reference repositories for the exact modality and objective.
- Document understanding with layout, images, and language may route to OCR plus NLP or VLM.
- Small structured business datasets usually route to tabular ML baselines before neural networks.
- User-facing natural language generation or instruction following may route to LLM fine-tuning or RAG.
- If a pre-trained model or API solves the task without training, say so and offer training only if the user needs customization.

## Do Not Do

- Do not choose the final architecture before routing is clear.
- Do not design detailed dataset schema.
- Do not write training scripts.
- Do not run final evaluation.
- Do not use native plan mode unless the user explicitly requested it.
- Do not write plans to `~/.claude/plans`.
