---
layout: post
title: "Why is my favorite LLM getting better?"
date: 2026-04-15
tags: [transformers]
description: "I evaluate language models for a living. I built a transformer small enough to see through (three-digit addition, 17,000 parameters) to sharpen my intuitions about what my evaluation methods are actually measuring. Three observations from the build."
---

I evaluate language models for a living. Most of that work comes down to one question: *did the model learn to do the thing we asked, or did it just learn to look like it did?* That question gets harder the bigger the model gets, because you're making claims about systems whose insides you can't see.

So I built a transformer small enough to see through. 17,000 parameters, three-digit addition, every component inspectable. There's no shortage of writing on how transformers work, and I'm not trying to add to it. I wanted something different: a setting where I know what algorithm the model should have learned, so I can tell whether it actually found it. Same question I'm asking of production LLMs, stripped of the natural-language fog.

During training, accuracy sat near zero for a long time. Loss dropped steadily the whole time. Then accuracy jumped to 95%+ over a few epochs. I had just watched **grokking**, a phase transition from memorizing training examples to discovering the generalizable algorithm.

This is the first of three posts about what that did to how I think about the question *why is my favorite LLM getting better?* The toy model can't answer the whole thing. It doesn't speak to RLHF, data curation, or any of the post-training work that makes production LLMs good. But it can answer a surprisingly large slice of it, and the slice generalizes.

Three observations.

## Capability is a cliff, not a ramp

During training, loss and accuracy decoupled. Loss dropped steadily. Accuracy sat near zero for many epochs, then jumped. The model first memorized the training data, then discovered the algorithm. That's grokking.

The implication to sit with: more training can be the path from memorization to understanding, but only if the architecture and regularization support it. Without weight decay, the model stays in the memorization regime indefinitely. Evaluate it mid-plateau and you'd conclude it failed. Evaluate it twenty epochs later and it's at 95%.

[AdderBoard](https://github.com/anadim/AdderBoard), a community competition for the smallest transformer that can add two 10-digit numbers, makes the same point along a different axis. Accuracy hovers near zero below some parameter threshold, then jumps to near 100% above. Same phase-transition shape, parameter count instead of training step.

Zoom out and scaling looks smooth: log-log curves, tidy power laws. Zoom in and it's made of cliffs. A model that "can't do X" today may be one training step, one parameter, or one representation change away from being able to. A model that "can do X" may be solving the task through memorization rather than computation. Training loss on its own tells you neither.

## Representation is a modeling choice, not a detail

The most important single line in the whole build is the one that reverses the output digits.

The natural way to encode `123 + 456 = 579` is thousands-first: `0579`. That's how you'd write it on paper. I tried it. The model got stuck at 1% accuracy.

One change fixed it: encode the sum as `9750`, ones digit first. Same model. Same data. Same optimizer. Same number of parameters. 1% → 95%+.

Why? The model generates the answer left to right, one token at a time. Carries propagate right to left. Thousands-first forces the model to predict the leading digit (which depends on whether a carry cascades all the way from the ones column) as its first output token. It has to solve the entire problem before emitting anything. Ones-first lets the model predict the ones digit from the ones columns alone, then the tens digit knowing whether there was a carry, and so on. The generation order lines up with the computation order.

This isn't a "trick." It's a parameterization that aligns with the causal structure of the problem. Every top solution on AdderBoard uses reversed output.

When people ask why LLMs are getting better, most of the answer they have in mind is training infrastructure: more compute, more data, better optimizers. That's real and it matters. But a meaningful share of the improvement (maybe half, hard to know) is representation: tokenization strategy, prompt format, chain-of-thought, the structure of the context you hand the model. Same architecture, same weights, different wrapping, different capability. My instinct calibrator for how big the representation lever is: 1% vs. 95%+ with one line of preprocessing.

## Scale is the only thing separating this from GPT-4

The components I built:

- Token embedding + positional embedding
- `[LayerNorm → Self-Attention → Residual]` then `[LayerNorm → FFN → Residual]`, stacked
- A final LayerNorm
- A linear head

Every one of these appears, unchanged, in GPT-4. Llama. Claude.

| | This model | GPT-2 Small | Llama 3 8B |
|---|---|---|---|
| Parameters | 17,760 | 124M | 8B |
| Layers | 2 | 12 | 32 |
| `d_model` | 32 | 768 | 4,096 |
| Attention heads | 1 | 12 | 32 |
| `d_ff` | 64 | 3,072 | 14,336 |
| Vocabulary | 14 | 50,257 | 128,256 |
| Context length | 13 | 1,024 | 128,000 |

Different dimensions, same stack. The scaling is dramatic; the components are identical.

My model is deliberately oversized for its task. I picked `d_model=32` and two layers so every component would be big enough to inspect. AdderBoard's current trained record for 10-digit addition is 67 parameters at 100% accuracy. The architecture isn't the bottleneck. Representation and scale are.

So part of "my favorite LLM is getting better" really is the same stack, more of everything. Wider embedding tables, wider MLPs, more heads, more layers, more tokens of training data. Not a fundamentally new architecture every six months.

## What this post is not saying

The addition task speaks to representation, architecture floor, and scale. It doesn't speak to:

- **RLHF and preference tuning.** The reason chatbots stopped saying blatantly offensive things in 2023 isn't in this transformer. It's in instruction-tuning and preference-optimization pipelines that sit on top of the base model.
- **Data curation and pretraining mixtures.** What you train on matters as much as how long you train. 50,000 addition problems doesn't approximate the internet.
- **Tool use, retrieval, agentic scaffolding.** Much of what makes a deployed LLM useful at a given task is the wrapping (tools, memory, retrieval augmentation), not the weights.

So when your favorite LLM gets better at following instructions or writing code, some of the improvement is architecture-plus-scale (this post) and some is post-training and systems engineering (not this post).

---

The code lives in a Quarto book: [How a Transformer Learns Addition]({{ '/notes/transformers-from-scratch/' | relative_url }}). The community version of the same exercise is [AdderBoard](https://github.com/anadim/AdderBoard), which tracks the smallest transformer that can add two 10-digit numbers. The smallest hand-coded entry uses six parameters.

*Next in this series: why context changes what the model effectively is.*
