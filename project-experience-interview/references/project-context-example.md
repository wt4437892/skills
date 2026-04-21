# 示例：Mall4Cloud 项目快照

> 本文件仅作示例，展示如何填写 `project-context.md`。
> 初始化流程不会读取此文件，不要把示例内容直接带入其他仓库。

## 1. 项目定位

- 项目名称：mall4cloud
- 一句话定位：企业级多租户 SaaS 电商平台，支持平台-商户-供应商三方协同。
- 业务覆盖范围：商品、订单、支付、营销、拼团、秒杀、搜索、流量分析。

## 2. 技术与架构事实

- 语言与运行时：Java 17
- 基础框架：Spring Boot 3.4.3、Spring Cloud 2024.0.0
- 注册与配置：Nacos 2.5.0
- RPC：Dubbo 3.3.3
- 分布式事务：Seata 2.2.0
- 消息队列：RocketMQ 2.3.1
- 缓存：Redis、Redisson 3.44.0
- 搜索：Elasticsearch 7.17.27
- 认证授权：Sa-Token 1.39.0
- 数据访问：MyBatis-Plus 3.5.12

## 3. 模块分布

基础设施层：mall4cloud-gateway、mall4cloud-auth、mall4cloud-common、mall4cloud-api
业务域层：mall4cloud-product、mall4cloud-order、mall4cloud-payment、mall4cloud-marketing、mall4cloud-group、mall4cloud-seckill、mall4cloud-search、mall4cloud-user
数据与分析层：mall4cloud-flow、mall4cloud-bi、mall4cloud-admin、mall4cloud-biz

## 4. 面试高价值主题

- 为什么同时使用 Spring Cloud 和 Dubbo
- 订单、支付、库存、营销联动时如何处理一致性
- 秒杀、拼团等高并发营销场景如何限流、削峰、扣库存
- 多租户、多角色场景下的权限与数据隔离如何设计
- 一个完整订单链路会经过哪些服务、关键表与状态流转

## 5. 使用提醒

- README 中的微服务数量与 pom.xml 模块数存在口径差异，输出时需解释是否把 common/api 计入微服务。
- README 里的性能描述是宣传材料，转成候选人答案时优先落到机制与设计理由。
- 用户未说明职责范围时，默认聚焦 order、product、payment、seckill，并提示可按真实经历替换。
