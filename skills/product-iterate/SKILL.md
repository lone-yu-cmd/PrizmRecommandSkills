---
name: product-iterate
description: "Facilitate a read-only product iteration discussion by studying an existing product's source code and usage evidence through its users' eyes, surfacing a complete backlog of user-voiced iteration ideas without editing files. Use whenever an owner wants to explore what to build next, plan a roadmap, mine unmet user needs, walk the app as customers, or says 「继续迭代」「还能做什么」「产品规划」「需求挖掘」「帮我发现方向」「从用户角度看看」, even with no feature named. Do not use to implement a specified feature (use feature-planner or prizmkit-plan), run autonomous coding iteration loops (use iterate-pipeline-launcher), or scope a single ambiguous request (use prompt-scope)."
compatibility: "Needs an agent that can read the bundled Markdown references and read the product's source code — source reading is the main working method. A browser tool plus a reachable running app is an optional bonus that upgrades some evidence from inference to fact; the skill works fully without one."
---

# Product Iterate

A conversation about what this product could become, seen through the people who use it.

## Responsibility

This is the single authoritative statement of scope. It is not repeated elsewhere in this skill.

This skill **does**:

- Fix which product is under discussion
- **Read the product's source freely and deeply** — that is how it learns what the product does
- Read whatever real usage the owner points to — analytics, logs, support threads, an issue tracker
- Inhabit each kind of user and walk their paths
- Discuss those users and the product's future with the owner
- List every iteration idea that honestly follows from that view — no cap on count, no filtering down to "the next thin slice"

This skill **does not**:

- **Write or edit** product source, tests, or planning files — reading is unlimited, writing is zero
- Implement, scaffold, or fix anything, even a one-line change
- Route to, name, or invoke another skill, or hand the session off at the end

The line is read versus write, not touch versus avoid. Reading the code is the primary way this skill sees the product; without it there is nothing to discuss.

One exception to the write rule: if the owner explicitly asks to save or archive the ideas, write **only** the idea list, to a path the owner names or approves. Never write to product code.

If the owner later asks to build something, that is a new request in a new turn — not a step this skill owns.

## When to use

- Continue iterating with no named feature
- Talk about the product's future, roadmap, or backlog
- List ideas a real user of this product would want
- The owner wants a partner who thinks from the user's side

## Conventions

**Asking questions.** Use the host's structured question capability when one is exposed. If it is not, ask the same question directly in chat and wait for an explicit answer. A missing tool is not permission to pick a default. Only a truly headless run with no conversational user may proceed on stated assumptions, and it must state them.

**Language.** Reply in the language the owner is writing in. The user-voice sentences ("I want … so that …") must be in the owner's language too, because they are meant to be read aloud and argued with.

**Never re-ask.** If the owner already answered something in this thread, use that answer.

## Phase 1 — Fix the target

Before reading anything, know what "the product" is. Confirm three things, asking only for what is not already obvious from the session:

1. **Which product** — a name. In a monorepo or a multi-app workspace, which app.
2. **Where the code is** — the directory that holds it. This is the one thing the skill cannot work without.
3. **Whether a running instance exists** — a deployed URL, or a dev command the owner is happy to run. Ask once. "No" is a completely normal answer; do not push for it and do not block on it.

If the current workspace is not a product (a tooling repo, a skills collection, a docs repo), say so and ask which product to discuss instead of guessing.

## Phase 2 — Read the product

**Source reading is the main method.** Most sessions will never have a running app, and that is fine — a codebase states, precisely and without a login, what the product offers, what it says to users, and where it stops them. Read it as a user-facing artifact, not as an architecture review.

What to read, roughly in this order:

- **Routes and navigation** — the complete list of places a user can be. This is the map the journey scan walks.
- **Page and screen components, especially empty states** — the literal copy shown before anything exists is where most hollow-success ideas come from.
- **CTAs and their handlers** — what the primary button on each screen actually does next, versus what its label promises.
- **Forms and validation** — which fields are required, which are hidden, what a save rejects. Required fields are friction the user feels every time.
- **API surface, error codes, and messages** — the sentence a user reads when something fails.
- **Gates** — auth checks, plan and quota limits, feature flags, permission branches. Every gate is a place someone gets stopped.
- **Data model nouns** — what the product thinks the world contains. Missing nouns are often missing features.
- **Analytics events**, if present — what the team already believes matters.

Also read the project map and the brief if they exist, treating the brief as claims rather than facts. Shipped code wins over stale docs; name any mismatch so the discussion does not replay finished work. Do not load the whole documentation tree. Do not audit dependencies or build tooling — nobody using the product feels those. The exception is a product whose install *is* its first screen, such as a CLI, an SDK, or a library: there, the install path, the entry point, and what a clean machine needs are all user experience, so read them.

**Optional bonus: a live walkthrough.** If, and only if, step 3 of Phase 1 turned up a reachable URL or an owner-approved dev command, walk the real thing with a browser tool: click the real CTAs, submit the real forms, land on the real empty states. Never start a server, install dependencies, or migrate a database unattended. This is an upgrade, not a prerequisite — it mostly confirms or corrects what the source already told you.

**Best evidence, when it exists: real usage.** If the owner can point to analytics, logs, support threads, an issue tracker, reviews, or an existing idea backlog, read it. A stall visible in real usage outranks every stall you reasoned to. Ask once; do not hunt.

**Evidence labels used throughout:**

- `fact` — what the product demonstrably does. Source is enough to establish this: a route exists, a field is required, the empty state says exactly this, the free plan stops here. Real usage data and a live walkthrough are also facts.
- `inference` — how a user reacts to that fact. "This empty state will leave them stranded" is inference even when the copy is quoted verbatim, unless real usage or a walkthrough backs it.
- `taste` — a product judgment the owner may simply reject.

Source reading therefore yields plenty of facts about the product and almost only inferences about feelings. Label accordingly, and if no live walkthrough happened, say so once in the output.

## Phase 3 — Walk it as a user

Read `references/journey-scan.md` for the scan list; it starts by classifying the product's shape, because a CLI, a mobile app, and an API are not scanned like a web app.

The walk happens on whatever Phase 2 gave you. With no running app, walk it on paper: every stop in the scan list corresponds to something concrete in the source — a route, a screen component, a command, an endpoint. Open that thing, read what a user would see there, and ask the scan's question about it. Read the stop's copy back in that user's voice before judging it. This is slower than clicking, and it finds most of the same stalls.

Follow the paths real people take. At each stop notice two things:

1. Where the product stops them
2. What they would wish existed next, even if nothing in the UI hints at it yet

Do not stop at broken loops. Adjacent wishes count. Engineering debt, refactors, and CI gaps belong in this conversation only when a user would feel them; otherwise leave them out. Unchecked items in an old brief are not automatic ideas — they count only if a user of the *current* product would still want them.

**Close the walk by naming the cast.** List every kind of user this product has, one line each: who they are and what they come to do. Derive it from what you just walked, not from a generic template. This list is the denominator for everything after it — Phase 5 works through it a few at a time, and Coverage reports against it. Without it there is no honest way to say what remains, and a round can quietly pass for the whole list.

## Phase 4 — Discuss users and future

This is a discussion, not a dump.

Talk about who those users are, what they come to do, and what kind of product this could become for them. Ask about people and outcomes only when the answer would change which ideas matter. Do not ask the owner to invent feature tickets.

If the owner says "just list ideas," skip to Phase 5.

## Phase 5 — List ideas, in batches

Read `references/idea-thinking.md` before listing. It defines how to inhabit a user, the lenses to run, and the exact fields each idea carries. Do not restate those fields here — that file is the spec.

Completeness is the goal, but one giant unreadable reply is not completeness. So batch:

- Work through the cast named at the end of Phase 3, **2–3 kinds of user per round**, running every lens for each.
- End every round with a **Coverage** note against that cast: which kinds are done, which are still queued.
- Ask whether to continue with the remaining kinds.

Batching never removes an idea. Grouping, ranking, and marking something as stretch are reading aids, not filters. An idea that is large, early, overlapping, or clearly not next still goes on the list — say so and keep it.

## Phase 6 — Keep going

Invite the owner to go deeper on any idea, argue with the user-voice, or run another round with a different user in mind.

On a later round in the same thread, do not reprint the whole list. Show only what is new, mark it `new this round`, and note when a new thought collapses into an idea already listed. Close the round with the updated Coverage note — never with a handoff to another skill.

## Output shape

Lead with how the product feels to a user. Then the discussion. Then the ideas.

```text
## How it feels to use today
[Users, what they come to do, where it helps, where it stops.]
[Say here whether this came from source alone or from a live walkthrough.]

## What we should talk about
[User and future questions, or the outcome already chosen.]

## Ideas — round N: [users covered]
### [group]
1. …

## Coverage
Cast: [every kind of user this product has]
Done: [kinds covered so far, every lens run for each]
Remaining: [kinds not yet run]
```

One idea, filled in:

```text
1. Resume last unfinished draft
   As a user: 我想一打开就回到昨晚没写完的那份，而不是再从空白页开始。
   Who: returning owner
   Why now: home shows only "create new" — coming back costs a search every time
   Evidence: fact (source: home route renders one CTA, no recent-items query) + inference (that this is what makes returning cost a search)
```

Keep each idea that short. Link a file or screen when it helps; never paste a whole journey.

A stretch idea carries exactly the same fields, with `[stretch]` after its name — `1. Multiplayer editing [stretch]`. The tag marks it; it never removes it.
