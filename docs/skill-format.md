# wisp-drug 技能契约 v0.1

本规范定义 `skills/` 下所有技能的强约定。校验工具：`python tools/validate_skills.py`（CI 强制门禁，违规即 fail）。

## 1. 目录布局

```
skills/<skill-name>/
├── SKILL.md              # 唯一入口（强制，≤ 300 行）
├── references/           # 深文档（可选，按需加载）
│   ├── concepts.md
│   ├── troubleshooting.md
│   └── advanced.md
├── scripts/              # 胶水脚本（可选；有则 samples 强制）
└── samples/              # 示例输入即 schema
    ├── input.json        # 最小可用输入（带脚本时强制）
    └── expected/         # 关键输出字段快照（可选）
```

## 2. frontmatter 规范

```yaml
---
name: target-evaluation            # 必填，必须与目录名一致
description: 一句话能力描述          # 必填，进入 Agent 技能菜单
dependsOn:                          # 可选，前置技能
  - depmap-knowledge-query
env:                                # 可选，环境声明
  runtime: uv                       # uv | ssh
  capability: gpu-compute           # runtime=ssh 时必填
license: TBD                        # 必填
---
```

### 2.1 `dependsOn` 依赖声明（Issue #1）

1. 列出的技能必须存在于同仓库 `skills/` 下
2. Agent 执行主技能前，先加载依赖技能的 SKILL.md 入口（不含其 `references/`）
3. 依赖链允许嵌套（A→B→C），**禁止循环**（A→B→A）；自依赖同样违规
4. 语义：组合发生在提示词层，不发生在代码层

### 2.2 `env` 环境声明（双档）

| runtime | 含义 | 校验 |
|---|---|---|
| `uv` | 本机 `uv sync` 直装（默认） | 无附加字段 |
| `ssh` | 经 wisp-science SSH kernel 路由到远程主机 | `capability` 必填，匹配 delegation_policy 的 capability ID |

不设私有镜像档、不设云执行档（设计决策见 README 设计原则 4）。

## 3. `references/` 渐进式披露（Issue #2）

1. SKILL.md 入口硬上限 **300 行**，超出必须拆 references/
2. SKILL.md 末尾放**索引表**：每篇 reference 一行（文件名 + 一句话说明何时读）
3. 建议类型（按需，不强求全有）：`concepts.md`（领域概念/阈值表）、`troubleshooting.md`、`advanced.md`（进阶参数）
4. references 之间可互引，但 SKILL.md 是唯一入口
5. 索引表列出的文件必须真实存在（防 stale 链接）；references/ 中存在但未被索引的文件给出警告

## 4. `samples/` 示例输入即 schema（Issue #3）

1. **带 `scripts/` 的技能必须有 `samples/input.json`** 且为合法 JSON
2. input.json 必须能直接喂给主脚本跑通（无网络场景；网络型技能允许标记 `"requires_network": true` 跳过冒烟，仅校验 JSON 合法性）
3. `expected/` 存关键输出**字段快照**（非全文），校验做字段级断言而非全文 diff
4. SKILL.md 的用法示例段直接引用 `samples/` 路径，不内联重复 JSON
5. 豁免：纯知识型技能（无 scripts/）可无 samples/，validator 不报错

## 5. 校验规则汇总（validator 行为）

| # | 检查 | 级别 |
|---|---|---|
| V1 | `skills/*/SKILL.md` 存在 | error |
| V2 | frontmatter 可解析、`name` 与目录名一致、`description`/`license` 存在 | error |
| V3 | `dependsOn` 引用的技能存在 | error |
| V4 | 依赖图无环、无自依赖（DFS） | error |
| V5 | SKILL.md ≤ 300 行 | error |
| V6 | references/ 索引表列出的文件存在 | error |
| V7 | references/ 内未索引文件 | warning |
| V8 | 带 scripts/ 的技能存在合法 samples/input.json | error |
| V9 | input.json 含 `"requires_network": true` 时跳过冒烟 | info |
| V10 | `env.runtime` ∈ {uv, ssh}；ssh 时 `capability` 必填 | error |

## 6. 与 wisp-science 的关系

- 字段位（dependsOn/references/samples）在 wisp-science skill-creator 模板中已存在；本仓将其升级为强约定
- `env.capability` 对接 wisp-science delegation_policy 的 capability→主机解析（引擎侧，不在本仓实现）
- 本规范是平台契约，叙事基座是 wisp-science 平台约定；OriBench 拆解仅作工程情报来源

## 7. 变更记录

- v0.1（2026-10-14）：三约定 + env 双档声明 + validator 首版
