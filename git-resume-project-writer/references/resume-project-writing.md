# 项目经历写法参考

## 核心结论

把项目经历写成“职责列表”是不够的，面试和简历更看重“你做了什么、怎么做的、带来了什么结果”。

适合技术简历的稳定公式：

```text
动作 + 场景/模块 + 技术手段 + 结果
```

可改写成这些变体：

- 动词 + 任务 + 结果
- What + How + Why
- Action + Project/Problem + Result
- Accomplished X as measured by Y by doing Z

这些公式本质一致，都是要求把“做事过程”翻译成“可评估的贡献”。

## 从 Git 历史到简历表述的转换规则

Git 里常见的是这些信号：

- `feat`/`implement`/`support`
- `fix`/`hotfix`
- `optimize`/`perf`
- `refactor`
- `test`/`ci`/`deploy`

简历里不要直接写成：

- 提交了 XX 次代码
- 修了很多 bug
- 参与了后端开发
- 负责日常维护

优先改写为：

- 负责/主导某个业务模块或技术模块
- 通过某种技术方案完成能力建设、性能优化或稳定性治理
- 形成明确结果：性能、稳定性、交付效率、成本、用户体验、业务支持能力

## 结果应该怎么写

能量化就量化，量化优先级如下：

1. 性能指标：响应时间、吞吐、CPU/内存占用、SQL 耗时、页面加载时间
2. 稳定性指标：故障率、超时率、错误率、线上事故次数、回归缺陷数
3. 交付指标：发布耗时、研发周期、自动化覆盖率、人工操作减少比例
4. 业务指标：用户数、订单量、转化率、GMV、留存、活跃度
5. 范围指标：覆盖模块数、接口数、页面数、服务数、项目规模

没有业务数据时，不要瞎编。先写技术效果，再补“待确认指标”：

- 将复杂查询链路重构为缓存 + 异步刷新方案，显著降低高峰期接口抖动
- 搭建自动化发布流程，减少手工发布步骤；待确认发布耗时下降比例

## 好的项目经历长什么样

### 单条版

适合用户只要“一条项目经历”时使用：

```text
主导订单查询链路优化，基于 Redis 缓存和异步预热机制重构热点接口访问路径，降低高并发场景下的查询延迟并提升系统稳定性。
```

### 标准项目版

```markdown
项目名称：订单中台系统
角色定位：Java 后端开发
技术栈：Spring Boot、MySQL、Redis、Kafka
项目经历：
- 负责订单查询与履约流程核心接口开发，基于 Spring Boot + MySQL 完成多模块服务拆分与接口治理，支撑业务快速迭代。
- 针对高频查询场景引入 Redis 缓存与异步刷新机制，优化热点接口访问链路，降低高峰期响应延迟；待确认 P95 优化幅度。
- 推动异常处理与告警链路补齐，完善测试与发布流程，提升核心交易链路稳定性与问题定位效率。
待确认指标：
- 日均订单量 / 峰值 QPS
- 查询接口 P95 降幅
- 线上故障率或超时率变化
```

## 差例改写

差例：

```text
参与后端开发，修复 bug，写接口。
```

问题：

- 没有模块边界
- 没有技术手段
- 没有结果
- 看不出你的个人贡献

改写：

```text
负责用户中心认证与权限接口开发，基于 Spring Security 和 Redis 完成登录态校验与权限缓存优化，提升认证链路稳定性并降低重复鉴权开销。
```

差例：

```text
提交了很多代码，做了优化。
```

改写：

```text
围绕报表导出链路完成性能优化与异步化改造，结合批处理和任务分片机制降低大批量导出场景下的接口阻塞风险。
```

## 面向目标岗位做二次改写

### 投后端

优先强调：

- 核心链路和关键模块
- 架构设计、服务治理、缓存、消息队列、数据库优化
- 稳定性、性能、可维护性、工程效率

### 投前端

优先强调：

- 页面体验、首屏性能、组件化、状态管理、可维护性
- 埋点、可视化、交互复杂度、端到端联调

### 投测试/测开

优先强调：

- 自动化测试、回归效率、质量门禁、缺陷治理、CI 集成

## 从搜索资料提炼出的稳定原则

以下要点来自职业发展中心和简历写作资料的共识：

- 用强动词起句，不要用弱描述
- 强调成就，不要只列职责
- 说明 what、how、why / result
- 尽量加入数字、范围或结果指标
- 每条 bullet 只讲一个中心贡献
- 用目标岗位会使用的关键词改写

## 来源

- Coursera, "How to Write a Resume (Project-Centered Course)": https://www.coursera.org/learn/how-to-write-a-resume
- Coursera, "How to Make a Resume: 2026 Resume Writing Guide": https://www.coursera.org/articles/how-to-make-a-resume
- Emory University, "Creating Impressive Resume Bullets": https://cpd.emory.edu/resources/creating-impressive-resume-bullets/
- Yale University, "Writing Impactful Resume Bullets": https://ocs.yale.edu/resources/writing-impactful-resume-bullets/
- University of Florida, "Resume Guide": https://careerhub.ufl.edu/resources/resume-guide/
- MCPHS Career Development Center, "Bullets: Turning Responsibilities into Actions & Results": https://www.mcphs.edu/academics/career-development-center/job-internship-search/resumes/bullets
