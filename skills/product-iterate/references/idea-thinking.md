# Idea thinking

Read this before listing ideas. The journey scan finds where a user is. This file is how to think from that place, and it is the spec for what a listed idea looks like.

The job is not "name three features." The job is: inhabit each user, run every lens, and write down every wish that still belongs to *this* product.

## Contents

1. [Become the user](#become-the-user)
2. [Lenses — run all of them](#lenses--run-all-of-them)
3. [Turn a thought into an idea](#turn-a-thought-into-an-idea)
4. [Round completeness check](#round-completeness-check)
5. [Do not](#do-not)

## Become the user

Pick one kind of user from the cast named at the end of the walk. Stay in their body for a whole pass. Speak in "I", in the owner's language.

Answer, in their voice:

- I opened this because I wanted ______.
- If it works, I leave with ______.
- I would tell a friend this product is for ______.
- I would abandon it when ______.
- I would come back tomorrow if ______.

Then switch to the next kind in the cast and do it again. A guest, a first-timer, a returning owner, a visitor of someone else's work, and a collaborator are different products wearing the same UI — those are illustrations, not the cast itself, which comes from the product you actually walked. Ideas from one kind do not cover the others.

Do not think as the maintainer ("we should refactor"). Think as the person who will feel the change.

## Lenses — run all of them

For each user, run every lens. A lens that yields nothing is fine; skipping a lens is not.

### 1. Stall

The product asked me to do something, then left me stuck, confused, or doing the wrong next step.

Ask: what did I think the button would do? What did it do? What do I need instead?

### 2. Hollow success

I "succeeded" (saved, sent, published) but I do not have what I came for. The empty state after first save is often this.

Ask: if I showed this result to the person I care about, would I be embarrassed? What is still missing?

### 3. Next ten minutes

I am still here. What do I naturally want to do in the next ten minutes that the product does not offer?

Ask: after this screen, where does my attention go in real life (notes, chat, calendar, another tool)?

### 4. Come back later

Days have passed. I do not remember where I left off.

Ask: what would make returning obvious? Search, recap, unfinished, reminders, last-opened.

### 5. Other people

I want a human involved: cofounder, advisor, audience, teammate, future me on another device.

Ask: what do I send them? What can they do when they arrive? How do I hear that they did something?

### 6. Trust and control

I do not trust what the product just did (assistant, generate, paywall, visibility).

Ask: can I undo, preview, see why, keep a draft, or say no without losing work?

### 7. Expressing myself

The blank form is heavier than my thought. I would rather talk, paste, upload, or point at an example.

Ask: how is this idea already sitting in my world (voice, files, chat, a competitor's page)?

### 8. Seeing others

I learn by looking at how other people used this product.

Ask: what would I copy, follow, or learn from a stranger's public work?

### 9. Crossing tools

I will not live only here. I will paste into chat, slides, a repo, a notebook.

Ask: what do I need to take out, bring in, or keep in sync?

### 10. Power and limits

Something blocked me: quota, plan, login, missing field, silent error.

Ask: what did I think I had paid for or earned? What should the product say, and what should it let me do next?

### 11. Time and ritual

Morning capture, weekly review, before a meeting, late-night dump.

Ask: is there a rhythm this product could belong to, that it currently ignores?

### 12. Adjacent wish

Nothing is broken. I still want more of what this product already is.

Ask: if this already helps me do X, the obvious next human wish is _______. Do not stop at the current feature set.

## Turn a thought into an idea

Each surviving thought becomes one list item with exactly these fields:

- **Name** — what I would see or get, in user-visible terms
- **As a user** — "I want … so that …", in the owner's language
- **Who** — which person from the become-the-user pass
- **Why now** — the stall, hollow success, adjacent wish, or other lens it answers
- **Evidence** — `fact` / `inference` / `taste`, plus the one thing that justifies each label. Labels combine, and usually must: a source-only idea normally reads `fact` about the product **+** `inference` about the person, with both halves written out

On evidence, the split is between behaviour and reaction. What the product **does** is `fact`, and reading the source is enough to establish it — a route exists, a field is required, a plan stops here, the empty state says exactly this. How a user **feels** about that is `inference` until real usage or a live walkthrough shows otherwise. A stall visible in analytics, logs, support threads, or an issue tracker is `fact` and outranks one you reasoned to. Most source-only ideas will therefore read as: fact about the product, inference about the person. Write both halves rather than rounding up to `fact`.

If two thoughts are the same wish, keep one and say they collapsed. If they help different users, keep both.

Stretch is allowed. Mark it stretch. Still list it.

## Round completeness check

A round covers 2–3 kinds of user from the cast. It is done when all of these are true for **those** users:

- Each of them has been inhabited, in their own voice
- Every lens has been run for each of them
- No idea was dropped for being large, obvious, overlapping, or "not the next slice"
- Nothing was padded in — no maintainer work a user would never notice

Then report coverage against the full cast: which kinds are done, with every lens run for each, and which are still queued. Because a finished kind always has all lenses run, coverage is counted by kind, not by lens. Queued kinds are not lost — the next round picks them up. Ending a round is not the same as finishing the list, and the output must not imply it is.

On a later round, only new ideas are printed. When a new thought collapses into one already listed, say which, rather than reprinting it.

## Do not

- Start from the codebase's modules and invent a feature per folder
- Start from a competitor feature list and paste it
- Start from an old brief and treat unchecked boxes as ideas
- Offer only "add more AI" when the user wanted a clearer next step
- Confuse a bug with a future (a wrong button can still be listed if a user feels it; say that it is a break, not a new bet)
- Silently upgrade an inference to a fact because it sounds more convincing
