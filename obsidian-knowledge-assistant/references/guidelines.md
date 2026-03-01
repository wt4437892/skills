# Note Structure Guidelines

## Template Structure

All notes should follow this structure:

1. **YAML Frontmatter**: Metadata for Obsidian
   - `title`: The knowledge point title
   - `created`: Creation date (YYYY-MM-DD format)
   - `tags`: Domain and category tags
   - `aliases`: Alternative names for this concept

2. **概念 (Concept)**: Clear, concise definition
   - What is this knowledge point?
   - Keep it brief (2-3 sentences)

3. **原理 (Principles)**: How it works
   - Underlying mechanisms
   - Theoretical foundation
   - Why it works this way

4. **实践 (Practice)**: Practical application
   - Basic usage with code examples
   - Common scenarios and best practices
   - Important considerations and pitfalls

5. **参考资料 (References)**: Source citations
   - All information must be evidence-based
   - Include URLs to authoritative sources
   - Prefer official documentation, reputable tutorials, academic papers

6. **相关笔记 (Related Notes)**: Obsidian double links
   - Link to related concepts using [[note-name]] syntax
   - **TWO conditions required**: The note must (1) actually exist in the knowledge base AND (2) have strong relevance to the current topic
   - **Strong relevance means**: direct technical dependency, same core concept family, essential prerequisite, or tightly coupled in practice
   - **When in doubt, do NOT link** — default to an empty section rather than adding uncertain links
   - **Performance**: Scan only the current category directory (max 20 files) to prevent system overload
   - If no strongly related notes exist, leave this section empty

## Directory Organization

Notes are organized directly in the project root (the project name indicates the domain):

**For third-party libraries**:
```
{library-name}/
└── {note-title}.md
```
Example: `pandas/基本运算.md`, `requests/HTTP请求.md`

**For other categories**:
```
├── 基础语法/        (Basic Syntax)
├── 标准库/          (Standard Library)
├── 框架/            (Frameworks)
├── 工具/            (Tools)
├── 最佳实践/        (Best Practices)
└── 进阶主题/        (Advanced Topics)
```
Example: `基础语法/装饰器.md`, `标准库/os模块.md`

The assistant should automatically determine the appropriate category and directory structure based on the knowledge point.

## Evidence-Based Research

When creating notes:

1. **Always search for information** using web search tools
2. **Verify information** from multiple authoritative sources
3. **Never fabricate** information or examples
4. **Cite sources** in the References section
5. **Use official documentation** as primary source when available

## Related Notes Workflow (Strict Two-Condition Check)

When creating the "相关笔记" section:

1. **Limit scope**: Use Glob tool to find `.md` files only in the current category directory (e.g., `基础语法/*.md`)
2. **Set maximum**: Scan at most 20 files to prevent performance issues
3. **Strong relevance check**: For each found note, evaluate whether it meets one of these strict criteria:
   - Direct technical dependency (topic A is implemented using/built on topic B)
   - Same core concept family (both are variants of the exact same concept)
   - Essential prerequisite (must understand B before A makes sense)
   - Tightly coupled in practice (consistently used together as a unit)
4. **Default to no link**: If the relationship is loose, indirect, or uncertain — do not add the link
5. **Create links**: Only add `[[note-title]]` for notes that pass BOTH conditions (exists + strongly relevant)
6. **Empty section handling**: If no strongly related notes are found, leave the section empty

**Performance Note**: Never scan the entire project directory. Always limit to current category and max 20 files to prevent system overload.

## Example Note

See `example_python_decorator.md` for a complete example.
