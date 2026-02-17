---
name: obsidian-knowledge-assistant
description: Domain-specific Obsidian knowledge note assistant that researches, extracts, and organizes evidence-based notes. Use when users request to (1) create notes about a knowledge point or concept, (2) organize or document technical knowledge, (3) ask questions expecting structured note output, or (4) mention keywords like "整理笔记", "记录", "帮我学习". The domain is determined by the project/directory name (e.g., "python" project creates Python notes). Creates structured markdown notes with YAML frontmatter, double links, tags, and organizes them by tech stack categories.
---

# Obsidian Knowledge Assistant

Domain-specific note assistant that researches knowledge points and creates structured Obsidian notes with evidence-based content.

## Workflow

### 1. Identify Domain and Knowledge Point

- **Domain**: Determined by the current project/directory name
  - Example: Project named "python" → Python domain notes
  - Example: Project named "javascript" → JavaScript domain notes
  - **IMPORTANT**: All user-requested knowledge points are within this domain context

- **Knowledge Point**: Extract from user's request
  - User's knowledge points are always within the current domain
  - Example in "python" project:
    - "帮我整理装饰器的笔记" → Knowledge point: "Python装饰器" (Python domain)
    - "pandas基本运算" → Knowledge point: "pandas基本运算" (Python third-party library)
    - "什么是列表推导式？" → Knowledge point: "列表推导式" (Python basic syntax)
  - Example in "javascript" project:
    - "什么是Promise？" → Knowledge point: "Promise" (JavaScript domain)
    - "React Hooks" → Knowledge point: "React Hooks" (JavaScript framework)

### 2. Research the Knowledge Point

**CRITICAL**: All information must be evidence-based. Never fabricate content.

1. Use web search tools to find authoritative sources:
   - Official documentation (highest priority)
   - Reputable tutorials and guides
   - Academic papers or technical blogs

2. Gather information covering:
   - Concept definition
   - Working principles
   - Practical examples
   - Common use cases
   - Best practices and pitfalls

3. Collect source URLs for the References section

### 3. Determine Category

Automatically categorize the knowledge point into one of these tech stack categories based on its nature:

- `基础语法` (Basic Syntax): Language fundamentals, syntax features
  - Example: Python装饰器, 列表推导式, async/await
- `标准库` (Standard Library): Built-in modules and functions
  - Example: os模块, datetime, json
- `第三方库` (Third-party Libraries): External packages installed via package managers
  - Example: pandas, numpy, requests, axios
- `框架` (Frameworks): Web frameworks, testing frameworks, etc.
  - Example: Django, Flask, React, Vue
- `工具` (Tools): Development tools, CLI tools
  - Example: pip, npm, webpack, pytest
- `最佳实践` (Best Practices): Design patterns, coding standards
  - Example: 设计模式, 代码规范, 错误处理
- `进阶主题` (Advanced Topics): Advanced concepts, performance optimization
  - Example: 性能优化, 内存管理, 并发编程

**Category Selection Logic**:
1. Research the knowledge point to understand its nature
2. Identify whether it's a language feature, library, framework, or concept
3. Select the most appropriate category from the list above
4. Example: "pandas基本运算" → pandas is a third-party library → Category: `第三方库`

### 4. Scan Existing Notes

Before creating the note, scan the domain directory to identify existing notes:

1. Use Glob tool to find all `.md` files in the domain directory
2. Read each note to verify it has actual content (not empty)
3. Build a list of available notes that can be referenced
4. This list will be used in the "相关笔记" section to only link existing notes

### 5. Create the Note

Use the template from `assets/note_template.md` with these replacements:

- `{{TITLE}}`: Knowledge point name
- `{{DATE}}`: Current date (YYYY-MM-DD)
- `{{DOMAIN}}`: Project domain (e.g., "python")
- `{{CATEGORY}}`: Determined category (e.g., "基础语法")
- `{{LANGUAGE}}`: Programming language for code blocks

Fill in each section:

1. **概念 (Concept)**: 2-3 sentence clear definition
2. **原理 (Principles)**: Explain how it works and why
3. **实践 (Practice)**:
   - Basic usage with code examples
   - Common scenarios
   - Important considerations
4. **参考资料 (References)**: List all source URLs
5. **相关笔记 (Related Notes)**: Link to existing related notes
   - **CRITICAL**: Only link to notes that actually exist in the knowledge base
   - Before creating links, scan the domain directory to find existing notes
   - Check that linked notes have actual content (not empty files)
   - Use `[[note-title]]` syntax only for verified existing notes
   - If no related notes exist yet, leave this section empty or add a comment

### 6. Save to Appropriate Directory

Create the directory structure directly in the project root (no need to create a domain directory since the project name already indicates the domain):

**For third-party libraries** (第三方库):
```
{library-name}/
└── {note-title}.md
```
Example: `pandas/基本运算.md`, `numpy/数组操作.md`

**For other categories**:
```
{category}/
└── {note-title}.md
```
Example: `基础语法/装饰器.md`, `标准库/os模块.md`, `框架/Django路由.md`

## Note Structure

See `references/guidelines.md` for detailed structure guidelines and `references/example_python_decorator.md` for a complete example.

## Key Principles

1. **Evidence-Based Only**: Never invent information. All content must come from research.
2. **Cite Sources**: Always include URLs in the References section.
3. **Structured Format**: Follow the template structure consistently.
4. **Obsidian Features**: Use YAML frontmatter, tags, and double links `[[]]`.
5. **Automatic Organization**: Determine category and create directory structure automatically.
6. **Link Only Existing Notes**: In the "相关笔记" section, only create links to notes that actually exist and have content. Never link to empty or non-existent notes.

## Example Usage

**Example 1**: In "python" project, user says "帮我整理装饰器的笔记"

**Process**:
1. Domain: "python" (from project name)
2. Knowledge point: "装饰器" (within Python domain)
3. Research using web search
4. Category: "基础语法" (language feature)
5. Create note at: `基础语法/装饰器.md`

**Example 2**: In "python" project, user says "pandas基本运算"

**Process**:
1. Domain: "python" (from project name)
2. Knowledge point: "pandas基本运算" (pandas is a third-party library)
3. Research using web search
4. Category: "第三方库" (external package)
5. Create note at: `pandas/基本运算.md` (use library name as directory)

**Example 3**: In "javascript" project, user says "什么是Promise？"

**Process**:
1. Domain: "javascript" (from project name)
2. Knowledge point: "Promise" (within JavaScript domain)
3. Research using web search
4. Category: "基础语法" (language feature)
5. Create note at: `基础语法/Promise.md`
