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

### skill-optimizer

Audit and optimize SKILL.md files against [skill-creator](https://github.com/anthropics/claude-code) writing standards.

**What it does:**
- **Phase 1 — Diagnose**: Read-only audit across 8 dimensions (body size, progressive disclosure, redundancy, instruction style, description triggering, reference health, etc.)
- **Phase 2 — Optimize**: Extract reference-manual content, deduplicate, compress, update pointers (requires user confirmation)
- **Phase 3 — Review**: Verify completeness, pointer integrity, and standalone readability

**Usage:**
```
/skill-optimizer <path-to-skill-directory> [--diagnose-only]
```

## License

MIT
