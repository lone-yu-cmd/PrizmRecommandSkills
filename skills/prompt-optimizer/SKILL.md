---
name: prompt-optimizer
description: "Optimize and improve prompts before sending them to Claude Code. Use this skill whenever the user says 'optimize prompt', 'improve this prompt', 'help me rewrite this instruction', 'how to write this prompt better', or any variation of wanting to refine, polish, or enhance a prompt/instruction they plan to give Claude. Also trigger when the user provides a draft prompt and asks for feedback or improvements, even if they don't use the word 'prompt' explicitly."
---

# Prompt Optimizer

A skill for optimizing prompts given to Claude Code. It takes a user's draft prompt, analyzes it in the context of the current conversation, and produces multiple optimized versions with clear explanations of what was improved and why.

## When to Use

- User wants to optimize a prompt before sending it to Claude
- User asks "how should I phrase this", "help me write a better prompt", "optimize this instruction"
- User has a draft prompt and wants it refined for clarity, precision, or structure

## How It Works

You receive the user's original prompt as input. Your job is to:

1. Understand what the user actually wants to accomplish (from the prompt itself and the conversation context)
2. Identify problems in the original prompt
3. Produce three optimized versions, each with a different optimization strategy

## Step 1: Analyze the Original Prompt

Before optimizing, figure out what's going on. Look at:

**From the conversation context:**
- What topic has the user been working on?
- What technologies, frameworks, or tools are involved?
- What's the broader goal behind this prompt?

**From the prompt itself:**
- What is the user asking Claude to do?
- What information is missing that Claude would need?
- Where is the language ambiguous or open to multiple interpretations?
- Is the task too broad or too vague to produce a focused response?

## Step 2: Apply Optimization Rules

Focus on two core dimensions:

### Dimension 1: Eliminate Ambiguity, Increase Precision

Ambiguity is the #1 killer of prompt quality. A prompt that can be interpreted two ways will be interpreted the wrong way half the time. Look for these common problems:

- **Vague scope**: "improve the code" — which code? improve how? performance? readability? both?
- **Missing constraints**: "write a function" — in what language? what are the edge cases? what should it return on error?
- **Implicit assumptions**: the user knows what they mean, but Claude doesn't have that context. Make the implicit explicit.
- **Undefined terms**: "make it better", "clean this up", "fix the issues" — these mean nothing without specifics.
- **Missing output expectations**: the user has a mental picture of what "done" looks like, but hasn't described it.

For each problem found, add the missing information. Pull from conversation context when possible — if the user has been working on a React app, and they say "write a component", you can infer they want a React component, but it's still better to state it explicitly in the optimized prompt.

### Dimension 2: Task Decomposition and Structure

Complex prompts fail when they dump everything into one paragraph. Structure helps Claude process the request systematically:

- **Break multi-step tasks into numbered steps**: if the prompt asks for 3 things, make that explicit rather than burying them in prose.
- **Separate concerns**: input description, processing logic, output format — each should be its own section when the task is complex enough.
- **Add constraints as a list**: rather than weaving constraints into sentences, pull them out as bullet points.
- **Specify output format**: if the user wants code, specify the language. If they want analysis, specify the structure (bullet points? sections? a table?).
- **Order matters**: put the most important instruction first. Claude pays more attention to the beginning and end of a prompt.

Not every prompt needs heavy structure. A simple "rename variable X to Y in file Z" doesn't need decomposition. Match the structure to the complexity of the task.

## Step 3: Generate Three Versions

Each version takes a different approach to optimization. This gives the user options that fit their style and the complexity of the task.

### Version 1: Precise Version (Recommended)

Minimal changes to the original. Focus on:
- Adding missing context from the conversation
- Replacing vague words with specific ones
- Adding the one or two most important constraints the user forgot

This version is best when the original prompt is mostly fine but needs sharpening. The user should be able to look at it and think "yes, that's what I meant."

### Version 2: Structured Version

Restructure the prompt for maximum clarity:
- Break it into clearly labeled sections (Goal / Context / Requirements / Output Format)
- Decompose multi-part tasks into numbered steps
- Pull out constraints and edge cases as explicit bullet points

This version is best for complex tasks where Claude needs to juggle multiple requirements. The structure helps Claude not miss anything.

### Version 3: Minimal Version

Strip everything down to the essential instruction:
- Remove pleasantries, hedging, and filler
- Keep only the core action and the most critical constraint
- One to three sentences maximum

This version is best for simple, focused tasks where brevity is a virtue. Some prompts are verbose not because the task is complex, but because the user is thinking out loud.

## Output Format

Present results using this structure:

```
## Original Prompt Analysis

**Identified intent**: [What the user is actually trying to accomplish, inferred from prompt + conversation context]

**Issues found**:
- [Issue 1: specific problem and why it matters]
- [Issue 2: specific problem and why it matters]
- ...

---

## Optimized Versions

### Version 1: Precise Version (Recommended)

> [The optimized prompt, in a blockquote so it's easy to copy]

**What changed**: [Brief explanation of each change and why it improves the prompt]

---

### Version 2: Structured Version

> [The optimized prompt, in a blockquote]

**What changed**: [Brief explanation]

---

### Version 3: Minimal Version

> [The optimized prompt, in a blockquote]

**What changed**: [Brief explanation]

---

**Recommendation**: [Which version to use and why, based on the task complexity]
```

## Important Principles

- **Don't invent requirements.** Only add information that can be inferred from the conversation context or that is obviously missing. If you're not sure what the user wants, flag it as a question rather than guessing.
- **Preserve the user's voice.** The optimized prompt should feel like a better version of what the user wrote, not a completely different prompt written by someone else.
- **Optimization is not expansion.** A prompt that's twice as long is not twice as good. Every word should earn its place.
- **Context is king.** The same prompt can be excellent or terrible depending on context. "Write tests" is a great prompt if the conversation has been about a specific function for the last 10 minutes. Always consider what Claude already knows from the conversation.
- **Be honest about diminishing returns.** If the original prompt is already clear and well-structured, say so. Don't optimize for the sake of optimizing.
