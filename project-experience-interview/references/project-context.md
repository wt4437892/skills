# Mall4Cloud 项目快照

## 目录

1. 项目定位
2. 技术与架构事实
3. 模块分布
4. 面试高价值主题
5. 使用提醒

## 1. 项目定位

- 仓库名为 `mall4cloud`，定位是企业级多租户 SaaS 电商平台。
- README 明确强调 `DDD`、`微服务架构`、`平台-商户-供应商` 三方协同。
- 业务覆盖商品、订单、支付、营销、拼团、秒杀、搜索、流量分析等多个域。

## 2. 技术与架构事实

基于当前仓库可直接确认的事实：

- 语言与运行时：`Java 17`
- 基础框架：`Spring Boot 3.4.3`、`Spring Cloud 2024.0.0`
- 注册与配置：`Nacos 2.5.0`
- RPC：`Dubbo 3.3.3`
- 分布式事务：`Seata 2.2.0`
- 消息队列：`RocketMQ 2.3.1`
- 缓存：`Redis`、`Redisson 3.44.0`
- 搜索：`Elasticsearch 7.17.27`
- 认证授权：`Sa-Token 1.39.0`
- 数据访问：`MyBatis-Plus 3.5.12`
- API 文档：`Knife4j 4.5.0`

这些信息主要来自 `pom.xml` 与 `README.md`，回答细节题时应继续下钻到具体模块和实现类。

## 3. 模块分布

根 `pom.xml` 当前声明的顶层模块包括：

- `mall4cloud-gateway`
- `mall4cloud-auth`
- `mall4cloud-common`
- `mall4cloud-api`
- `mall4cloud-admin`
- `mall4cloud-biz`
- `mall4cloud-product`
- `mall4cloud-search`
- `mall4cloud-user`
- `mall4cloud-order`
- `mall4cloud-marketing`
- `mall4cloud-payment`
- `mall4cloud-group`
- `mall4cloud-seckill`
- `mall4cloud-flow`
- `mall4cloud-bi`

回答项目拆分题时，可以按“基础设施层 / 公共能力层 / 业务域层”重新归类，而不是机械背模块名。

## 4. 面试高价值主题

这个仓库最容易延伸出以下项目经历题：

- 为什么采用微服务与领域拆分，而不是单体
- 网关、认证、业务服务之间的调用链如何组织
- 为什么同时使用 Spring Cloud 和 Dubbo
- 订单、支付、库存、营销联动时如何处理一致性
- 秒杀、拼团等高并发营销场景如何限流、削峰、扣库存
- Redis、消息队列、搜索引擎分别解决什么问题
- 多租户、多角色场景下的权限与数据隔离如何设计
- 一个完整订单链路会经过哪些服务、关键表与状态流转
- 如果线上出现超时、重复下单、库存不一致、搜索延迟，该怎么排查

## 5. 使用提醒

- README 中的“微服务数量”“业务域数量”可能与 `pom.xml` 的模块数存在口径差异。输出时优先解释统计口径，例如是否把 `common/api` 计入微服务。
- README 里的性能或规模描述更像项目宣传材料。把它们转成候选人答案时，应优先落到“机制”与“设计理由”，不要直接复述成个人实战指标。
- 用户未说明职责范围时，优先假设其聚焦某几个核心域，例如 `order`、`product`、`payment`、`seckill`，并明确提示可按真实经历替换。
