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
   - **IMPORTANT**: Only link to notes that actually exist in the knowledge base
   - **Performance**: Scan only the current category directory (max 20 files) to prevent system overload
   - Use filename-based matching to identify related notes quickly
   - If no related notes exist, leave this section empty or add a placeholder comment
   - Build knowledge graph connections based on real, existing content

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

## Related Notes Workflow (Optimized)

When creating the "相关笔记" section:

1. **Limit scope**: Use Glob tool to find `.md` files only in the current category directory (e.g., `基础语法/*.md`)
2. **Set maximum**: Scan at most 20 files to prevent performance issues
3. **Quick matching**: Use filename-based matching to identify potentially related notes
4. **Create links**: Only add `[[note-title]]` links for verified existing files
5. **Empty section handling**: If no related notes exist, either:
   - Leave the section empty with a comment like `<!-- 暂无相关笔记 -->`
   - Or omit specific links and add a note: "相关笔记将在创建后添加"

**Performance Note**: Never scan the entire project directory. Always limit to current category and max 20 files to prevent system overload.

## Example Note

See `example_python_decorator.md` for a complete example.
