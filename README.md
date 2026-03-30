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

Audit and refactor SKILL.md files against [skill-creator](https://github.com/anthropics/claude-code) writing standards.

**What it does:**
- **Phase 1 — Diagnose**: Read-only audit across 11 dimensions (body size, progressive disclosure, redundancy, instruction style, description triggering, reference health, frontmatter, script health, safety patterns, etc.)
- **Phase 2 — Refactor**: Architecture refactoring, instruction rewriting, description optimization, health fixes (requires user confirmation)
- **Phase 3 — Review**: Verify completeness, pointer integrity, and standalone readability

**Usage:**
```
/skill-optimizer <path-to-skill-directory> [--diagnose-only] [--dimensions N,N,...]
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

## License

MIT
