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
   - Build knowledge graph connections

## Directory Organization

Notes should be organized by tech stack:

```
domain-name/
├── 基础语法/        (Basic Syntax)
├── 标准库/          (Standard Library)
├── 第三方库/        (Third-party Libraries)
├── 框架/            (Frameworks)
├── 工具/            (Tools)
├── 最佳实践/        (Best Practices)
└── 进阶主题/        (Advanced Topics)
```

The assistant should automatically determine the appropriate category based on the knowledge point.

## Evidence-Based Research

When creating notes:

1. **Always search for information** using web search tools
2. **Verify information** from multiple authoritative sources
3. **Never fabricate** information or examples
4. **Cite sources** in the References section
5. **Use official documentation** as primary source when available

## Example Note

See `example_python_decorator.md` for a complete example.
