# Journey scan

Walk the product as the people who use it. After each stop, ask: if I were this user, what would I wish existed next?

Each stop below is a place in the product, not a place in a browser. Usually you reach it by opening the route, screen, command, or endpoint that implements it and reading what a user would see there; if a running instance happens to be available, click it instead. The questions are the same either way.

## Contents

1. [Pick the product's shape first](#pick-the-products-shape-first)
2. [Web / SaaS app](#web--saas-app)
3. [CLI or developer tool](#cli-or-developer-tool)
4. [Mobile app](#mobile-app)
5. [API, SDK, or library](#api-sdk-or-library)
6. [Internal or ops tool](#internal-or-ops-tool)
7. [Every shape](#every-shape)
8. [How to record a stall or wish](#how-to-record-a-stall-or-wish)

## Pick the product's shape first

Read only the sections that match. A CLI has no empty state and no OAuth return; a library has no CTA. Scanning a product against the wrong checklist produces ideas nobody asked for.

- Runs in a browser, has accounts and pages → [Web / SaaS app](#web--saas-app)
- Installed and invoked in a terminal → [CLI or developer tool](#cli-or-developer-tool)
- Installed from a store, runs on a phone → [Mobile app](#mobile-app)
- Consumed by other people's code → [API, SDK, or library](#api-sdk-or-library)
- Used by colleagues, not customers → [Internal or ops tool](#internal-or-ops-tool)

A product can be two shapes at once (a SaaS with a CLI). Scan both, and keep their users separate — they are different people.

Then read [Every shape](#every-shape), which applies regardless.

## Web / SaaS app

**Guests**

- Marketing or official home: what a signed-out person understands, and what the primary CTA actually opens
- Sign-in / register / OAuth return: whether they land in the product loop or back on marketing
- Public surfaces: whether a stranger can understand the work without an account
- Wish: would I bookmark, follow, copy, or come back later?

**First success**

- Empty home: which action is primary (assistant vs blank form vs upgrade)
- First create/save: required vs hidden optional fields; whether assistant fill persists before save
- After first save: where they land, and whether the next CTA matches what they just did
- Wish: would I want a draft, a template, or to speak instead of typing?

**Depth**

- Detail/overview: empty-state copy vs what the product actually does next
- Secondary artifacts (docs, exports, generated drafts): empty banner vs per-type empty state; preview vs persist
- Uploads and attachments: whether they become something I can use
- Wish: would I want a plan, a checklist, a shareable pack, or a next-week prompt from this work?

**Sharing and other people**

- Public vs private vs link vs request-to-view: whether I understand the difference
- Comments, likes, follows: which exist, and whether the author hears about them
- Inbox / badges: which events I will never see
- After access is granted: can I only look, or can I help write?
- Wish: would I send this to a teammate, an advisor, or a group chat, and what would I expect them to do?

**Returning owner**

- Home with existing work: besides "create another," what do I come back to do?
- Settings / subscription / AI / tokens: whether a stuck state blocks the work I came for
- Export and download: whether leaving the page drops the file; whether formats mean what I think
- Wish: would I want search across my work, a weekly recap, or to resume the last unfinished item?

## CLI or developer tool

- Install and first run: how many steps before the first useful output; what breaks on a clean machine
- Discovery: `--help`, subcommand naming, whether I can guess the command I need without docs
- The happy path: the one command people actually run all day, and how much typing it costs
- Errors: whether a failure tells me what to do next, or only what went wrong
- Config: where state lives, what happens on a second machine, whether secrets are handled sanely
- Scripting: exit codes, machine-readable output, whether the tool composes in a pipeline or CI
- Upgrade: how I learn a new version exists, and whether upgrading breaks my scripts
- Wish: what do I currently wrap in my own shell alias or script because the tool does not do it?

## Mobile app

- Store listing and first launch: what I expected versus what opens
- Permissions: what is asked for, when, and whether refusing leaves the app usable
- One-handed reality: reachability, typing burden, whether the core action survives a moving train
- Offline and flaky network: what happens mid-action, whether work is lost
- Notifications: which ones exist, which ones I would turn off within a day
- Continuity: whether the phone and any web version know about each other
- Wish: what would I want on the lock screen, in the share sheet, or in a widget?

## API, SDK, or library

- Time to first successful call: from docs page to a real response
- Auth: how a key is issued, scoped, rotated, and revoked
- The core object model: whether names match how integrators think, or only how the backend is built
- Errors: status codes, machine-parseable reasons, whether retrying is safe
- Limits: quota, rate limits, pagination — discoverable before I hit them, or only after
- Versioning: how a breaking change reaches me, and how long the old shape survives
- Local development: sandbox, test keys, fixtures, mocks
- Wish: what wrapper is every integrator writing themselves that should ship in the box?

## Internal or ops tool

- Who is forced to use this, and what they were doing before it existed
- The recurring task: how many clicks or tabs a routine run costs
- Trust: whether people verify the output somewhere else before acting on it
- Blast radius: how a destructive action is confirmed, audited, and undone
- Handover: whether a new teammate can operate it without asking the author
- Escape hatch: which parts people bypass with a manual script, and why
- Wish: what would let this run on a schedule, or stop needing a human at all?

## Every shape

Run these regardless of form factor:

- **Second use**: the product on day two, not day one — what is different, what is now annoying
- **Failure**: the worst realistic thing that happens to a user, and what the product says when it does
- **Money and limits**: what is gated, whether the gate is legible before someone hits it
- **Leaving**: whether a user can get their data out, and what they would take with them
- **Adjacent**: nothing is broken and I still want more of what this already does — what is it?

## How to record a stall or wish

One sentence in the user's voice, plus where it happened, plus how you know. Name the source file or screen when it pins the claim down.

- "I just saved the minimum. I want the rest filled in before anyone generates a longer document for me." — after first save — fact that the detail page renders empty for a minimal record; inference that it feels like an unfinished job
- "I ran it twice and could not tell whether the second run did anything." — CLI happy path — fact that the command prints nothing on a no-op; inference that this is what erodes trust
