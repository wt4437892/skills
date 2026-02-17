---
title: Python装饰器
created: 2024-01-15
tags: [python, 基础语法]
aliases: [decorator, 装饰器模式]
---

# Python装饰器

## 概念 (Concept)

装饰器是Python中的一种设计模式，允许在不修改原函数代码的情况下，为函数添加额外的功能。装饰器本质上是一个接受函数作为参数并返回新函数的高阶函数。

## 原理 (Principles)

装饰器基于Python的几个核心特性：

1. **函数是一等公民**：函数可以作为参数传递，也可以作为返回值
2. **闭包机制**：内部函数可以访问外部函数的变量
3. **语法糖**：`@decorator` 语法是 `func = decorator(func)` 的简写

工作流程：
1. 装饰器函数接收被装饰的函数作为参数
2. 在装饰器内部定义一个包装函数（wrapper）
3. 包装函数在调用原函数前后添加额外逻辑
4. 返回包装函数替代原函数

## 实践 (Practice)

### 基本用法

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("函数执行前")
        result = func(*args, **kwargs)
        print("函数执行后")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}!")

say_hello("World")
# 输出:
# 函数执行前
# Hello, World!
# 函数执行后
```

### 常见场景

1. **日志记录**：记录函数调用信息
2. **性能测试**：测量函数执行时间
3. **权限验证**：检查用户权限
4. **缓存**：缓存函数返回值
5. **重试机制**：失败时自动重试

### 注意事项

1. **保留元数据**：使用 `functools.wraps` 保留原函数的元数据
2. **参数传递**：使用 `*args, **kwargs` 确保参数正确传递
3. **装饰器顺序**：多个装饰器的执行顺序是从下到上
4. **性能开销**：装饰器会增加函数调用开销，避免过度使用

## 参考资料 (References)

- [Python官方文档 - 装饰器](https://docs.python.org/zh-cn/3/glossary.html#term-decorator)
- [PEP 318 - Decorators for Functions and Methods](https://www.python.org/dev/peps/pep-0318/)
- [Real Python - Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)

## 相关笔记

- [[Python闭包]]
- [[Python高阶函数]]
- [[functools模块]]
