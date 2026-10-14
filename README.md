# wisp-drug

> 基于 wisp-science 的下一代药物研发平台 —— agent-native，开源优先。

`wisp-drug` 构建在 [wisp-science](https://github.com/Yu-Qiao-sjtu/wisp-science) 引擎之上：wisp-science 提供项目 / 会话 / 子代理委派 / 技能执行的技术底座，`wisp-drug` 承载药物研发的垂直能力层——靶点评估、变异解读、分子设计、成药性、证据综合。

**我们的起点是 wisp-science 的 coding-agent-first 架构，不是任何闭源工作台。** 对 OriBench 等竞品的拆解只作为工程情报输入（对比计划见 [wisp-science-depmap](https://github.com/Yu-Qiao-sjtu/wisp-science-depmap)）；凡属 vendor lock-in 的部分（docker 私有镜像、llm-only 中继计费、云强制执行、身份改写营销层）一概不采用。

## 平台分层

```
wisp-science        引擎层：项目 / 会话 / 子代理委派 / 技能执行循环
   └─ wisp-drug     垂直层：药物研发技能体系 + 技能契约三约定
        └─ skills/  target-evaluation · variant-interpretation · 分子设计 · 成药性 · 证据综合
```

## 技能契约三约定（v0 基石）

| 约定 | 解决什么 | Issue |
|---|---|---|
| `dependsOn:` 依赖声明 | 技能横向组合，复杂技能模块化；组合发生在提示词层而非代码层 | #1 |
| `references/` 渐进式披露 | SKILL.md 薄入口 + 深文档按需加载，控制上下文成本 | #2 |
| `samples/` 示例输入即 schema | 测试夹具 + schema 文档 + 新手样例，一份三用 | #3 |

三约定在 wisp-science 的 skill-creator 模板中已有字段位（`dependsOn` / `references` / `samples`）；本仓负责把它们升级为全库强约定 + CI 校验。

## 设计原则

1. **说明书而非集成代码** —— 工具接入 = 一份 SKILL.md + 可选脚本，不写 per-tool 适配器
2. **Agent 即运行时** —— 复用 Claude Code / Codex 原生执行循环，不自研 agent 引擎
3. **文件即接口** —— 跨工具数据交换用 SDF/PDB/CSV 落盘，Agent 负责格式翻译
4. **开源优先** —— 不依赖私有镜像或计费中继；重计算工具用开源版 + 公开权重自建

## 姊妹仓库

- [wisp-science](https://github.com/Yu-Qiao-sjtu/wisp-science) —— 上游引擎（技能 / 会话 / 子代理执行底座）
- [wisp-science-depmap](https://github.com/Yu-Qiao-sjtu/wisp-science-depmap) —— 科学侧项目：依赖组图谱驱动；`docs/oribench-skill-comparison-plan.md` 保存竞品拆解与技能格式对比计划

## Roadmap

- [ ] #1 `dependsOn` 依赖声明 + validate 脚本
- [ ] #2 `references/` 渐进式披露 + 行数上限校验
- [ ] #3 `samples/` 示例输入规范 + CI smoke
- [ ] #4 平台定位锚定（上游 wisp-science，竞品仅作情报）
- [ ] 首批领域技能：target-evaluation / variant-interpretation（自主设计，按 wisp-science 科研路线生长）

## License

TBD
