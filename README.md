# wisp-drug

> Drug-discovery skill suite for coding agents — Claude Code / Codex / Gemini CLI first.

`wisp-drug` 是面向编码 Agent 的药物研发技能套件，起点是对 [OriBench](https://oribench.lglab.ac.cn)（临港实验室 AI 制药工作台）的逆向拆解：它用 108 个 SKILL.md 说明书替代传统集成代码，让通用编码 Agent 充当集成运行时。本项目吸收其中被验证有效的**轻量约定**，在 wisp 系列的 coding-agent-first 架构上重建，不引入 docker 私有镜像、云中继、llm-only 路由等 vendor lock-in。

## 核心约定（v0 基石）

| 约定 | 来源 | 解决什么 |
|---|---|---|
| `dependsOn:` frontmatter 依赖声明 | OriBench skill contract | 技能横向组合，复杂技能模块化 |
| `references/` 渐进式披露 | OriBench skill layout | SKILL.md 薄入口，深文档按需加载，控上下文成本 |
| `samples/` 示例输入即 schema | OriBench 可测性设计 | 测试夹具 + schema 文档 + 新手上手，三合一 |

详细规范见 Issues #1–#3。

## 设计原则

1. **说明书优先于代码** —— 工具接入 = 一份 SKILL.md + 可选脚本，不写 per-tool 适配器
2. **Agent 即运行时** —— 依赖 Claude Code / Codex 原生工具循环，不自建 agent 引擎
3. **文件即接口** —— 工具间数据交换走 SDF/PDB/CSV 落盘，Agent 负责格式翻译
4. **零锁定** —— 无强制云中继、无私有镜像依赖；重计算走开源工具官方渠道

## 与姊妹仓库的关系

- [wisp-science-depmap](https://github.com/Yu-Qiao-sjtu/wisp-science-depmap) —— 依赖组图谱方向的科学推理项目，`docs/oribench-skill-comparison-plan.md` 记录了两边技能格式的对比计划
- 本仓库聚焦药物设计技能本体（分子生成/对接/成药性/靶点评估）

## Roadmap

- [ ] #1 `dependsOn` 依赖声明
- [ ] #2 `references/` 渐进式披露
- [ ] #3 `samples/` 示例输入规范
- [ ] 首批技能迁移（target-evaluation / variant-interpretation 方向，对位 OriBench 靶点评估与变异解读三件套）

## License

TBD
