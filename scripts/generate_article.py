#!/usr/bin/env python3
"""Generate blog articles from repo analysis and optional aimiddleground evidence.

Intermediate artifacts are stored in ~/article-workspace/{slug}/ for resumability.
"""

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
BLOG_DIR = PROJECT_DIR / "src" / "content" / "blog" / "en"
WRITING_GUIDE = PROJECT_DIR / "ARTICLE-WRITING-GUIDE.md"
WORKSPACE_ROOT = Path.home() / "article-workspace"

AIMIDDLEGROUND_DB_CANDIDATES = [
    Path.home() / "aimiddleground" / "data" / "aimiddleground.db",
    Path.home() / "claude" / "aimiddleground" / "data" / "aimiddleground.db",
]

ANALYSIS_PROMPT = """Analyze this open-source project repository thoroughly. Output a structured markdown report covering:

## Project Overview
- What the project does (1-2 sentences)
- Target users
- GitHub stars, contributors, latest release info (from README or repo metadata)
- License

## Technical Architecture
- Tech stack (languages, frameworks, key dependencies)
- Project structure (main packages/modules)
- Core design patterns

## Key Features
- List 5-10 main features with brief descriptions
- What makes this project unique vs alternatives

## Installation & Setup
- How to install (all methods: npm, pip, docker, etc.)
- Prerequisites and dependencies
- Complexity assessment (1-5 scale)

## Strengths
- 3-5 concrete strengths with evidence from the code

## Weaknesses & Limitations
- 3-5 honest weaknesses or limitations found in code/docs/issues

## Competitive Landscape
- Name 2-3 direct alternatives/competitors
- How this project differentiates

## Pricing
- Is it free/open-source? Any paid tiers?
- Cost of required dependencies (API keys, etc.)

## Community & Maintenance
- Activity level (recent commits, open issues, PR velocity)
- Documentation quality assessment

Be specific. Include exact numbers, version strings, file counts, and code references.
Output in markdown format."""


# ────────────────────────────────────────────
# Metadata (resume support)
# ────────────────────────────────────────────

def load_metadata(work_dir: Path) -> dict:
    meta_path = work_dir / "metadata.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {"phases": {}, "created_at": datetime.now().isoformat()}


def save_metadata(work_dir: Path, meta: dict):
    meta["updated_at"] = datetime.now().isoformat()
    (work_dir / "metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def phase_done(meta: dict, phase: str) -> bool:
    return meta.get("phases", {}).get(phase, {}).get("status") == "done"


def mark_phase(meta: dict, phase: str, **extra):
    meta.setdefault("phases", {})[phase] = {
        "status": "done",
        "finished_at": datetime.now().isoformat(),
        **extra,
    }


# ────────────────────────────────────────────
# Main
# ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate blog articles from repo analysis")
    parser.add_argument("article_type", choices=["review", "comparison"], help="Article type")
    parser.add_argument("--repo-url", help="GitHub repo URL (standalone mode)")
    parser.add_argument("--task-id", help="aimiddleground task ID (linked mode)")
    parser.add_argument("--slug", help="Output filename slug (e.g. oh-my-pi-review-2026)")
    parser.add_argument("--skip-research", action="store_true", help="Skip NotebookLM research phase")
    parser.add_argument("--resume", action="store_true", help="Resume from last completed phase")
    parser.add_argument("--db-path", type=Path, help="Override aimiddleground DB path")
    parser.add_argument("--dry-run", action="store_true", help="Print article to stdout, don't write file")
    parser.add_argument("--model", default="sonnet", help="Claude model for generation (default: sonnet)")
    args = parser.parse_args()

    if not args.repo_url and not args.task_id:
        parser.error("Either --repo-url or --task-id is required")

    slug = args.slug or _derive_slug_from_url(args.repo_url or "", args.article_type)
    work_dir = WORKSPACE_ROOT / slug
    work_dir.mkdir(parents=True, exist_ok=True)

    meta = load_metadata(work_dir)
    meta["slug"] = slug
    meta["article_type"] = args.article_type
    meta["repo_url"] = args.repo_url or ""
    meta["task_id"] = args.task_id or ""

    context_path = work_dir / "context.md"
    research_path = work_dir / "research.md"
    draft_path = work_dir / "article-draft.md"

    print(f"  Workspace: {work_dir}")
    print()

    # ── Phase 1: Collect ──
    print("=" * 60)
    print("Phase 1: COLLECT — Gathering evidence")
    print("=" * 60)

    if args.resume and phase_done(meta, "collect") and context_path.exists():
        context = context_path.read_text(encoding="utf-8")
        print(f"  [RESUME] Using existing context.md ({len(context)} chars)")
    else:
        if args.task_id:
            context = collect_from_aimiddleground(args.task_id, args.db_path)
        else:
            context = collect_from_repo(args.repo_url)

        context_path.write_text(context, encoding="utf-8")
        mark_phase(meta, "collect", chars=len(context))
        save_metadata(work_dir, meta)
        print(f"  Context written: {context_path} ({len(context)} chars)")

    # ── Phase 2: Research ──
    research = ""
    if not args.skip_research:
        print()
        print("=" * 60)
        print("Phase 2: RESEARCH — NotebookLM enrichment")
        print("=" * 60)

        if args.resume and phase_done(meta, "research") and research_path.exists():
            research = research_path.read_text(encoding="utf-8")
            print(f"  [RESUME] Using existing research.md ({len(research)} chars)")
        else:
            repo_url = args.repo_url or _extract_url_from_context(context)
            project_name = _extract_name_from_context(context) or "project"
            research = run_notebooklm_research(work_dir, meta, context, repo_url, project_name)
            if research:
                research_path.write_text(research, encoding="utf-8")
                mark_phase(meta, "research", chars=len(research))
                save_metadata(work_dir, meta)
                print(f"  Research written: {research_path} ({len(research)} chars)")
            else:
                print("  Research phase skipped or failed, continuing without it")
    else:
        if research_path.exists():
            research = research_path.read_text(encoding="utf-8")
            print(f"\n  [Skipping research, but loading existing research.md ({len(research)} chars)]")
        else:
            print("\n  [Skipping research phase]")

    # ── Phase 3: Generate ──
    print()
    print("=" * 60)
    print("Phase 3: GENERATE — Writing article with Claude")
    print("=" * 60)

    if args.resume and phase_done(meta, "generate") and draft_path.exists():
        article = draft_path.read_text(encoding="utf-8")
        print(f"  [RESUME] Using existing article-draft.md ({len(article)} chars)")
    else:
        writing_guide = ""
        if WRITING_GUIDE.exists():
            writing_guide = WRITING_GUIDE.read_text(encoding="utf-8")

        prompt = build_article_prompt(args.article_type, context, research, writing_guide)
        article = generate_with_claude(prompt, args.model)

        draft_path.write_text(article, encoding="utf-8")
        mark_phase(meta, "generate", chars=len(article), model=args.model)
        save_metadata(work_dir, meta)
        print(f"  Draft written: {draft_path} ({len(article)} chars)")

    # ── Phase 4: Output ──
    print()
    print("=" * 60)
    print("Phase 4: OUTPUT — Validation and file write")
    print("=" * 60)

    article = ensure_draft_true(article)
    warnings = validate_article(article)
    for w in warnings:
        level = "ERROR" if w.startswith("[E]") else "WARN"
        print(f"  {level}: {w}")

    errors = [w for w in warnings if w.startswith("[E]")]
    if errors:
        print(f"\n  {len(errors)} error(s) found. Article NOT written.")
        print(f"  Draft saved at: {draft_path}")
        print(f"  Fix the draft and re-run with --resume to skip earlier phases.")
        sys.exit(1)

    out_slug = slug if slug.endswith(".md") else slug + ".md"

    if args.dry_run:
        print(f"\n  [DRY RUN] Would write to: {BLOG_DIR / out_slug}")
        print("--- Article Preview (first 500 chars) ---")
        print(article[:500])
    else:
        out_path = BLOG_DIR / out_slug
        out_path.write_text(article, encoding="utf-8")
        mark_phase(meta, "output", path=str(out_path))
        save_metadata(work_dir, meta)
        word_count = len(article.split())
        print(f"\n  Article written: {out_path}")
        print(f"  Words: {word_count}")

    print("\nDone!")


# ────────────────────────────────────────────
# Phase 1: Collect
# ────────────────────────────────────────────

def collect_from_repo(repo_url: str) -> str:
    print(f"  Analyzing repo: {repo_url}")

    clone_dir = None
    cwd = None

    if repo_url.startswith("http"):
        clone_dir = Path(tempfile.mkdtemp(prefix="article-gen-"))
        print(f"  Cloning to {clone_dir}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(clone_dir)],
            capture_output=True, timeout=120,
        )
        cwd = str(clone_dir)
    else:
        cwd = repo_url

    print("  Running Claude Code analysis (this may take 1-2 minutes)...")
    try:
        result = subprocess.run(
            ["claude", "-p", ANALYSIS_PROMPT, "--output-format", "text",
             "--model", "sonnet", "--allowedTools", "Read,Glob,Grep,WebSearch,WebFetch"],
            capture_output=True, text=True, timeout=600, cwd=cwd,
        )
        output = result.stdout.strip()
        if not output:
            output = result.stderr.strip() or "Analysis produced no output"
    except subprocess.TimeoutExpired:
        output = "Analysis timed out after 600 seconds"
    except FileNotFoundError:
        print("  ERROR: 'claude' CLI not found. Install with: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)

    if clone_dir and clone_dir.exists():
        shutil.rmtree(clone_dir, ignore_errors=True)

    header = f"# Project Analysis: {repo_url}\n\n"
    header += f"- **Source**: Direct repo analysis via Claude Code\n"
    header += f"- **Date**: {date.today().isoformat()}\n\n"
    return header + output


def collect_from_aimiddleground(task_id: str, db_path: Path | None) -> str:
    db = _find_db(db_path)
    if not db:
        print(f"  ERROR: Cannot find aimiddleground database")
        sys.exit(1)

    print(f"  Reading aimiddleground task: {task_id}")
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row

    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        print(f"  ERROR: Task {task_id} not found in database")
        sys.exit(1)

    questions = conn.execute(
        "SELECT * FROM questions WHERE task_id = ? ORDER BY priority", (task_id,)
    ).fetchall()

    evidences = conn.execute(
        "SELECT * FROM evidences WHERE task_id = ? AND type != 'log' ORDER BY timestamp",
        (task_id,),
    ).fetchall()

    report = conn.execute(
        "SELECT * FROM reports WHERE task_id = ?", (task_id,)
    ).fetchone()

    conn.close()

    data_dir = db.parent
    task_dir = data_dir / "tasks" / task_id
    report_md = _read_artifact(task_dir, "05-report.md")
    analysis_md = _read_artifact(task_dir, "01-analysis.md")
    agent_test_md = _read_artifact(task_dir, "05-test-agent.md")

    lines = [
        f"# Project Analysis: {task['project_name']}",
        f"\n- **GitHub URL**: {task['github_url']}",
        f"- **Source**: aimiddleground evaluation (task {task_id})",
        f"- **Date**: {task['updated_at'] or task['created_at']}",
        f"- **Project Type**: {task.get('project_type', 'unknown')}",
        f"\n## Summary\n{task.get('summary', 'N/A')}",
    ]

    if report:
        lines.append(f"\n## Ratings")
        lines.append(f"- Deploy Difficulty: {report['deploy_difficulty']}/5")
        lines.append(f"- Feature Completeness: {report['feature_completeness']}/5")
        lines.append(f"- Documentation Quality: {report['doc_quality']}/5")
        lines.append(f"- Recommendation: {report['recommendation']}")

    if questions:
        lines.append("\n## Questions & Answers")
        for q in questions:
            answer = q["answer"] or "Not answered"
            lines.append(f"\n### [{q['category']}] {q['content']}")
            lines.append(f"**Status**: {q['status']}")
            if answer != "Not answered":
                lines.append(f"\n{answer}")

    if report_md:
        lines.append(f"\n## Full Report\n{report_md[:15000]}")
    if analysis_md:
        lines.append(f"\n## Analysis\n{analysis_md[:5000]}")
    if agent_test_md:
        lines.append(f"\n## Agent Test Results\n{agent_test_md[:5000]}")

    if evidences:
        lines.append("\n## Key Evidence")
        for e in evidences[:20]:
            content = e["content"] or ""
            lines.append(f"\n### {e['step_name']}")
            lines.append(content[:1000])

    return "\n".join(lines)


# ────────────────────────────────────────────
# Phase 2: Research (NotebookLM)
# ────────────────────────────────────────────

def run_notebooklm_research(work_dir: Path, meta: dict, context: str, repo_url: str, project_name: str) -> str:
    if not shutil.which("nlm"):
        print("  WARNING: 'nlm' CLI not found. Skipping research.")
        return ""

    try:
        nb_id = meta.get("phases", {}).get("research_notebook", {}).get("notebook_id")

        if not nb_id:
            print(f"  Creating NotebookLM notebook for '{project_name}'...")
            nb_id = _nlm_create_notebook(f"Review: {project_name}")
            if not nb_id:
                print("  WARNING: Failed to create notebook. Skipping research.")
                return ""
            meta.setdefault("phases", {})["research_notebook"] = {"notebook_id": nb_id}
            save_metadata(work_dir, meta)

            print("  Adding evidence as source...")
            context_file = work_dir / "context.md"
            _nlm_add_source(nb_id, file_path=str(context_file), title="Test Evidence")

            if repo_url:
                print(f"  Adding GitHub URL as source: {repo_url}")
                _nlm_add_source(nb_id, url=repo_url)

            print(f"  Running web research for '{project_name}'...")
            _nlm_research(nb_id, f"{project_name} open source review community feedback")
        else:
            print(f"  [RESUME] Reusing notebook {nb_id}")

        print("  Querying notebook for article insights...")
        queries = [
            ("Capabilities Summary",
             f"Summarize the key capabilities, strengths, and limitations of {project_name}. Include specific numbers and facts."),
            ("Competitive Landscape",
             f"What alternatives or competitors exist to {project_name}? How does it compare in features, community size, and maturity?"),
            ("Community Sentiment",
             f"What is the community sentiment about {project_name}? Any notable issues, praise, or concerns from users?"),
        ]

        sections = []
        for title, query in queries:
            answer = _nlm_query(nb_id, query)
            if answer:
                sections.append(f"## {title}\n\n{answer}")

        return "\n\n".join(sections) if sections else ""

    except Exception as e:
        print(f"  WARNING: NotebookLM research failed: {e}")
        return ""


def _nlm_create_notebook(title: str) -> str | None:
    try:
        result = subprocess.run(
            ["nlm", "notebook", "create", title],
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout.strip()
        match = re.search(r"ID:\s*([a-f0-9-]{36})", output)
        if match:
            return match.group(1)
        match = re.search(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", output)
        return match.group(0) if match else None
    except Exception:
        return None


def _nlm_add_source(nb_id: str, url: str = None, file_path: str = None, title: str = None):
    cmd = ["nlm", "source", "add", nb_id]
    if url:
        cmd.extend(["--url", url])
    elif file_path:
        cmd.extend(["--file", file_path])
    if title:
        cmd.extend(["--title", title])
    cmd.extend(["--wait"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return result.returncode == 0
    except Exception:
        return False


def _nlm_research(nb_id: str, query: str):
    try:
        result = subprocess.run(
            ["nlm", "research", "start", query,
             "--notebook-id", nb_id, "--mode", "fast", "--auto-import"],
            capture_output=True, text=True, timeout=300,
        )
        output = result.stdout.strip()
        match = re.search(r"Imported (\d+) sources", output)
        count = match.group(1) if match else "?"
        print(f"    Research complete: {count} sources imported")
    except Exception as e:
        print(f"    Research failed: {e}")


def _nlm_query(nb_id: str, query: str) -> str:
    try:
        result = subprocess.run(
            ["nlm", "notebook", "query", nb_id, query],
            capture_output=True, text=True, timeout=120,
        )
        output = result.stdout.strip()
        if not output:
            return ""
        try:
            data = json.loads(output)
            answer = data.get("value", {}).get("answer", "")
            sources = data.get("value", {}).get("sources_used", [])
            if sources:
                answer += f"\n\n_({len(sources)} sources referenced)_"
            return answer
        except json.JSONDecodeError:
            return output
    except Exception:
        return ""


# ────────────────────────────────────────────
# Phase 3: Generate
# ────────────────────────────────────────────

REVIEW_PROMPT_TEMPLATE = """You are writing a blog article for Pick My AI (pick-my-ai.com), a site that publishes honest, data-driven reviews of AI tools.

## WRITING RULES (mandatory — follow these exactly)

{writing_guide}

## ADDITIONAL RULES FOR THIS ARTICLE

- Output language: English
- Category: review
- Minimum 1200 words, target 1500-1800 words
- At least 14 paragraphs (the site inserts ads every 3 paragraphs, minimum 6 paragraphs needed)
- Start with YAML frontmatter (---), then a blank line, then # h1 title, then intro paragraph
- Use ## for sections, ### for subsections. Never use # in body after the h1.
- Every 150-200 words must include a concrete data point (price, star count, metric, version number, date)
- Answer-first style: lead each section with the conclusion, then expand with evidence
- Use markdown tables for pricing and feature comparisons
- Include 2-3 internal links to existing articles: /blog/best-ai-coding-assistants is the most relevant
- Frontmatter must include: title (50-60 chars), description (150-160 chars), publishDate ({today}), category: review, tags (3-6), author: "Pick My AI Team", image: "/images/placeholder.svg", draft: true
- Tone: informed first-person plural ("we tested", "in our evaluation"), honest about limitations
- Include sections: What It Does, Key Features, Installation & Setup, Hands-On Experience, Pricing, Who Should Use This, Final Verdict
- The Final Verdict must include a clear recommendation

## TEST EVIDENCE (from hands-on analysis)

{context}

## ADDITIONAL RESEARCH

{research}

## YOUR TASK

Write a complete review article. Ground every claim in the evidence above. If the evidence is in Chinese, translate findings into natural English. Include the project's GitHub star count and key metrics. Be honest about both strengths and weaknesses.

Output ONLY the complete markdown file (frontmatter + full article content). No explanations or commentary outside the article."""


COMPARISON_PROMPT_TEMPLATE = """You are writing a comparison article for Pick My AI (pick-my-ai.com).

## WRITING RULES (mandatory)

{writing_guide}

## ADDITIONAL RULES

- Output language: English
- Category: comparison
- Minimum 1500 words, target 1800-2200 words
- At least 14 paragraphs
- Must include a TL;DR comparison table early in the article
- Each comparison dimension gets its own ## section with a clear winner declared
- Frontmatter: title (50-60 chars), description (150-160 chars), publishDate ({today}), category: comparison, tags (4-6), author: "Pick My AI Team", image: "/images/placeholder.svg", draft: true
- Include internal links to /blog/best-ai-coding-assistants
- End with ## Final Verdict with clear recommendation for different use cases

## TEST EVIDENCE

{context}

## ADDITIONAL RESEARCH

{research}

## YOUR TASK

Write a complete comparison article. Output ONLY the markdown file."""


def build_article_prompt(article_type: str, context: str, research: str, writing_guide: str) -> str:
    today = date.today().isoformat()

    if not research:
        research = "No additional research available. Rely on test evidence only."

    if len(writing_guide) > 8000:
        writing_guide = writing_guide[:8000] + "\n\n[... truncated for length ...]"

    if len(context) > 20000:
        context = context[:20000] + "\n\n[... truncated for length ...]"

    template = REVIEW_PROMPT_TEMPLATE if article_type == "review" else COMPARISON_PROMPT_TEMPLATE
    return template.format(
        writing_guide=writing_guide,
        context=context,
        research=research,
        today=today,
    )


def generate_with_claude(prompt: str, model: str) -> str:
    print(f"  Generating article with Claude ({model})...")
    print(f"  Prompt size: {len(prompt)} chars")

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text", "--model", model],
            capture_output=True, text=True, timeout=600,
        )
        output = result.stdout.strip()
        if not output:
            stderr = result.stderr.strip()
            print(f"  ERROR: Claude returned empty output. stderr: {stderr[:500]}")
            sys.exit(1)
        output = _strip_code_fences(output)
        return output
    except subprocess.TimeoutExpired:
        print("  ERROR: Claude timed out after 600 seconds")
        sys.exit(1)
    except FileNotFoundError:
        print("  ERROR: 'claude' CLI not found")
        sys.exit(1)


# ────────────────────────────────────────────
# Phase 4: Output
# ────────────────────────────────────────────

def validate_article(content: str) -> list[str]:
    warnings = []

    if not content.startswith("---"):
        warnings.append("[E] Missing frontmatter (must start with ---)")
        return warnings

    fm_end = content.find("---", 3)
    if fm_end < 0:
        warnings.append("[E] Unclosed frontmatter (missing closing ---)")
        return warnings

    frontmatter = content[3:fm_end]
    body = content[fm_end + 3:].strip()

    for field in ["title:", "description:", "publishDate:", "category:", "tags:"]:
        if field not in frontmatter:
            warnings.append(f"[E] Missing required frontmatter field: {field.rstrip(':')}")

    if "category:" in frontmatter:
        cat_match = re.search(r"category:\s*(\w+)", frontmatter)
        if cat_match and cat_match.group(1) not in ("review", "comparison", "tutorial", "best-of"):
            warnings.append(f"[E] Invalid category: {cat_match.group(1)}")

    word_count = len(body.split())
    if word_count < 800:
        warnings.append(f"[E] Too short: {word_count} words (minimum 800)")
    elif word_count < 1200:
        warnings.append(f"[W] Below target: {word_count} words (target 1200+)")

    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    if len(paragraphs) < 6:
        warnings.append(f"[E] Too few paragraphs: {len(paragraphs)} (minimum 6)")
    elif len(paragraphs) < 12:
        warnings.append(f"[W] Below target paragraphs: {len(paragraphs)} (target 12+)")

    h1_count = len(re.findall(r"^# ", body, re.MULTILINE))
    if h1_count == 0:
        warnings.append("[W] No h1 heading found in body")
    elif h1_count > 1:
        warnings.append(f"[W] Multiple h1 headings found: {h1_count} (should be 1)")

    return warnings


def ensure_draft_true(content: str) -> str:
    if "draft:" not in content:
        content = content.replace("---\n", "---\ndraft: true\n", 1)
    elif "draft: false" in content:
        content = content.replace("draft: false", "draft: true", 1)
    return content


# ────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────

def _find_db(override: Path | None) -> Path | None:
    if override and override.exists():
        return override
    for candidate in AIMIDDLEGROUND_DB_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _read_artifact(task_dir: Path, filename: str) -> str:
    path = task_dir / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _extract_url_from_context(context: str) -> str:
    match = re.search(r"https://github\.com/[\w-]+/[\w.-]+", context)
    return match.group(0) if match else ""


def _extract_name_from_context(context: str) -> str:
    match = re.search(r"# Project Analysis:\s*(?:https://github\.com/[\w-]+/)?([\w.-]+)", context)
    return match.group(1) if match else ""


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        first_nl = stripped.index("\n") if "\n" in stripped else len(stripped)
        stripped = stripped[first_nl + 1:]
    if stripped.endswith("```"):
        stripped = stripped[:-3].rstrip()
    return stripped


def _derive_slug_from_url(url: str, article_type: str) -> str:
    match = re.search(r"github\.com/[\w-]+/([\w.-]+)", url)
    name = match.group(1) if match else "untitled"
    name = re.sub(r"[^a-z0-9-]", "-", name.lower())
    name = re.sub(r"-+", "-", name).strip("-")
    suffix = "review" if article_type == "review" else "comparison"
    return f"{name}-{suffix}-{date.today().year}"


if __name__ == "__main__":
    main()
