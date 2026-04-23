# My Custom Skills

This repository contains custom skills for Claude Code.

## Overview

These skills are organized as standalone folders. Each skill contains a `SKILL.md` file and optional bundled resources such as `references/`, `scripts/`, or `assets/`.

Current focus areas:
- Git history to resume/project summary conversion
- Java senior interview new-question training
- Java senior interview spaced review from historical notes
- LeetCode note generation
- Project-experience interviewer / interviewee split workflow

## Skills

| Skill | Description | Typical Use |
|-------|-------------|-------------|
| [git-resume-project-writer](./git-resume-project-writer/SKILL.md) | 从 Git 提交历史提炼适合面试简历的项目经历与项目亮点 | 根据仓库提交记录生成项目经历、亮点和面试表达 |
| [java-senior-interviewer](./java-senior-interviewer/SKILL.md) | Java 资深面试新题训练：出新题、评分、讲解与笔记沉淀 | 针对 MySQL、Redis、JVM、Spring、并发、消息队列、分布式等领域做新题训练 |
| [java-senior-reviewer](./java-senior-reviewer/SKILL.md) | Java 历史题间隔复习：只抽今天到期题，复用笔记中的答案与讲解 | 基于历史笔记做今日到期间隔复习，并回写复习日期 |
| [leetcode-note-taker](./leetcode-note-taker/SKILL.md) | 帮助创建和记录 LeetCode 算法题笔记，生成结构化题解 | 根据题目和思路生成结构化算法题笔记 |
| [project-experience-interviewer](./project-experience-interviewer/SKILL.md) | 基于当前项目生成真实项目经历面试题，并把题目写入统一输出目录中的 Markdown 文件 | 面试官模式，只负责出题和落盘 |
| [project-experience-interviewee](./project-experience-interviewee/SKILL.md) | 读取统一输出目录中的项目面试题 Markdown，并基于当前项目给出参考回答 | 候选人模式，只负责读取题目并作答，必要时回写回答 |

## Java Skills Split

The Java interview workflow is intentionally split into two skills:

- `java-senior-interviewer`
  Responsible for new questions only: asking a fresh question, scoring the answer, giving explanations, and writing notes.
- `java-senior-reviewer`
  Responsible for review only: reading historical notes, selecting questions due today, showing existing answers/explanations, and updating review metadata.

This split keeps the trigger conditions clear and avoids mixing new-question training with review flow.

## Repository Structure

```text
skills/
├── git-resume-project-writer/
├── java-senior-interviewer/
├── java-senior-reviewer/
├── leetcode-note-taker/
├── project-experience-shared/
├── project-experience-interviewer/
├── project-experience-interviewee/
└── README.md
```

Conventions:
- Each skill lives in its own directory
- Each skill must contain a `SKILL.md`
- Optional resources should stay inside the same skill directory

## Usage

1. Add or update a skill under this repository.
2. Keep the skill description in frontmatter accurate enough to trigger correctly.
3. Validate the skill structure if needed.
4. Commit and push the repository.

## Getting Started

To create a new skill, use the `skill-creator` workflow:

```text
/skill-creator
```

When adding a new skill:
- Keep `SKILL.md` concise
- Put reusable detailed content in `references/` when needed
- Avoid extra docs like `CHANGELOG.md` or `QUICK_REFERENCE.md`

