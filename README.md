# PrizmRecommandSkills

A collection of recommended AI agent skills, compatible with Claude Code, Cursor, Gemini CLI, and 40+ other agents via [skills.sh](https://skills.sh).

## Installation

```bash
npx skills add lone-yu-cmd/PrizmRecommandSkills
```

This will prompt you to select which agent platforms to install to. All skills are automatically available for universal agents (Amp, Cursor, Gemini CLI, etc.), and you can optionally enable Claude Code, CodeBuddy, and others.

### Install globally (skip prompts)

```bash
npx skills add lone-yu-cmd/PrizmRecommandSkills -y -g
```

## Available Skills

### prompt-scope

Scope a brief, ambiguous, or underspecified request into a complete one before acting. It reconstructs intent, tests premises, classifies the scenario, expands the request across scenario-specific dimensions and blind spots, then either runs a read-only preflight or compiles the request into one clearly sectioned, execution-ready prompt.

**What it does:**
- **Preflight mode**: explicit scope contract → evidence → work; pauses before risky writes and states what was not checked
- **Scope contract**: names the decision, in/out of scope, minimum evidence, and stop condition; no fixed Quick/Standard/Deep levels
- **Keeps the AI's own retrieval path**: the protocol is a scaffold, not a cage; a material finding outside the original scope is surfaced under "其他观察 / 新发现", not dropped
- **Compile mode**: produces one clearly sectioned, copy-ready prompt with criteria, evidence requirements, acceptance, and guardrails; no multiple variants and no table/pipe formatting inside the prompt
- Covers layered docs, design review, logic closure, requirements, implementation, debugging, test adequacy, contract changes, migration/release, decisions, writing, and AI asset review
- Skips trivial single-step tasks; supports "直接做" without dropping the evidence or safety gate

**Usage:**
```
/prompt-scope 检查一下 L1 层的内容，设计是否合理、逻辑是否闭环、上下层是否呼应。
帮我优化这个 prompt：修复登录 bug。
```

### skill-optimizer

Audit and refactor SKILL.md files against [skill-creator](https://github.com/anthropics/claude-code) writing standards.

**What it does:**
- **Phase 1 — Diagnose**: Read-only audit across 11 dimensions (body size, progressive disclosure, redundancy, instruction style, description triggering, reference health, frontmatter, script health, safety patterns, etc.)
- **Phase 2 — Refactor**: Architecture refactoring, instruction rewriting, description optimization, health fixes (requires user confirmation)
- **Phase 3 — Review**: Verify completeness, pointer integrity, and standalone readability

**Usage:**
```
/skill-optimizer <path-to-skill-directory> [--diagnose-only] [--dimensions N,N,...]
```

### skill-reviewer

Static audit of SKILL.md files against skill-creator writing standards.

**What it does:**
- Read-only 11-dimension audit: body size, progressive disclosure, redundancy, instruction style, description triggering, reference health, frontmatter, script health, safety patterns, and more
- Produces a diagnostic report with severity levels (error / warning / info / style)
- Does NOT modify any files — purely diagnostic

**Usage:**
```
/skill-reviewer <path-to-skill-directory> [--dimensions N,N,...]
```

### skill-auditor

Evaluate skill effectiveness through test runs, grading, benchmarking, and A/B comparison.

**What it does:**
- **Eval mode**: Write test cases, run with-skill vs baseline, grade outputs, benchmark performance, collect user feedback, iterate
- **Compare mode**: Blind A/B comparison between two skill versions with post-hoc analysis
- **Trigger mode**: Optimize skill description for better triggering accuracy
- **Grade-only mode**: Grade existing outputs without re-running

**Usage:**
```
/skill-auditor <path-to-skill> [--eval | --compare | --trigger | --grade-only]
```

### prizm-video-analyzer

Extract and summarize what a video actually says from a Bilibili, Douyin, YouTube, Xiaohongshu, or TikTok URL.

**What it does:**
- Prefer existing captions when the platform has them
- If the site blocks anonymous download (Bilibili HTTP 412), retry with browser cookies
- If there is no caption track (danmaku does not count), download audio and transcribe with Whisper
- Extract keyframes so on-screen terms can correct ASR errors
- Produce a grounded summary; do not guess from the title

**Usage:**
```
帮我总结这个视频讲了什么：https://www.bilibili.com/video/BVxxxx
```

Requires `yt-dlp`, `ffmpeg`, and (when there are no captions) `faster-whisper`.

## License

MIT
