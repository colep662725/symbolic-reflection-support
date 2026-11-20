
> **当前稳定版本：v1.3.5（2026年11月20日）**
>
> Symbolic Reflection Support 是一个支持六种语言的
> 开源 Agent Skill，涵盖塔罗、易经、八字四柱、
> 西方占星以及情感与自我探索。
>
> **验证情况**
>
> - Windows 本地 117 项自动测试通过。
> - GitHub Actions 9 项 CI 任务全部通过。
> - 支持 Python 3.10–3.13。
> - 兼容 pyswisseph 与 pysweph。
> - 支持 Swiss Ephemeris 天文历算。
> - 提供 NASA/JPL Horizons 数值审计工具。
>
> **科学边界**
>
> 天文和历法计算可以通过数值方法验证。
> 塔罗、易经与命理解读属于文化象征和自我反思，
> 不构成经过科学验证的命运预测。
>
> 历史版本更新详见 CHANGELOG.md。


# Symbolic Reflection Support · 象征性自我探索 Skill

> **历史版本 v1.3.4-rc1（2026-11-20）：** 修正 Swiss 冥王星本体中心为单独对象 `9999`（而非默认 `PLUTO` + `FLG_CENTER_BODY`），增加官方数据联系信息校验、联网失败审计日志、离线卫星星历自检与新增自动测试。**NASA 官方 JPL 直接取数、实际 `9/999` 数值比较与 Swiss `9999` 实机验收仍未完成**；不要把测试模拟值或第三方归档称作正式通过。见 [完整关闭清单](references/official-closure-checklist.md) 和 [验收报告](QA_REPORT.md)。


[English](README.md) · [离线网页演示（塔罗与易经）](docs/index.html) · [Agent Skills 规范](https://agentskills.io/specification) · [AGPL 许可证](LICENSE) · [Windows 安装指南](INSTALL.zh-CN.md) · [许可说明](LICENSING.md)

**v1.3.0 已新增真正可执行的节气、四柱八字、十年大运规则计算及西方热带黄道本命星盘模块。**

**v1.3.2 重点升级“真实独立几何核验与 JPL 数据审计”：** 在先前66项低精度模型比较基础上，另写不调用 Swiss 的 Placidus 半日弧数值求根及独立天文角度近似，完成12个中性公开案例×12宫头=**144项独立比较**，最大差异约**0.43角秒**。新增 NASA/JPL Horizons 官方 API 的显式联网获取程序，限定公开日期的月球、冥王星地心视黄经，保存请求 URL、原始返回及 SHA-256 并独立比较。**本次环境无法访问 JPL 官方 API，因此月球/冥王星的真实 JPL 高精度核验仍未完成，不得以模拟数据替代。**详见[独立验证说明](references/independent-qa.md)和[真实安装验收指引](references/install-testing.md)。 这次重点是把**天文与历法计算**和**命理解读**严格分开：前者可以数值复算与参考资料核对；后者没有得到科学的命运预测验证。

原有 v1.2 功能全部保留：78张塔罗牌正逆位、64卦、六语言主题、离线抽牌、原始JSON结果、浏览器交互演示与历史命令兼容。

## 最快开始

基础功能无需安装第三方库：

```bash
python scripts/reflect.py tarot --count 1 --lang zh
python scripts/reflect.py iching --lang zh
python scripts/reflect.py iching --lines 7 8 7 9 7 8 --lang zh
# 第49卦革，第四爻动，变第63卦既济；给定输入不会冒充真实随机起卦。
```

**新增天文计算需先安装可选依赖**（在本机离线运算，安装本身一般需联网；本仓库不提供第三方星历文件）：

```bash
python -m pip install -r requirements-astronomy.txt

# 24节气：太阳视黄经、北京时间、另一套数值求根交叉复核
python scripts/solar_terms.py --year 2024 --tz Asia/Shanghai --verify-bisection

# 四柱八字：立春换年、节气换月，明确午夜／子初／晚子三种日界规则
python scripts/bazi.py --datetime 2024-02-10T12:00:00 --tz Asia/Shanghai --lat 39.9042 --lon 116.4074 --compare-boundaries

# 大运需明确顺逆，或由使用者显式提供传统男命／女命参数
python scripts/bazi.py --datetime 2024-02-10T12:00:00 --tz Asia/Shanghai --lat 39.9042 --lon 116.4074 --direction forward --cycles 8

# 西方热带黄道本命盘：太阳至冥王星、ASC、MC、Placidus宫位
python scripts/natal.py --datetime 2000-01-01T12:00:00 --tz Europe/London --lat 51.4779 --lon 0 --houses placidus --cross-check --uncertainty-minutes 15
```

上面**全部是公开中性测试案例，不包含使用者的私人出生资料**。默认塔罗、易经、八字与星盘计算在本机运行、JSON 输出至标准输出，不保存个人出生资料；只有明确执行 `fetch_horizons.py --fetch` 时才会访问 JPL 官方 API，且该脚本仅查询公开中性日期。共享终端与公开日志仍需自行保护隐私。

## 能力、规则与边界

| 子系统 | 已完成 | 严格限制 |
| --- | --- | --- |
| 塔罗与易经 | 六语言内容、真随机与示例结果区分 | 不宣称科学预测 |
| 四柱八字 | 立春年界、12节月界、日干支、时干支 | 子初／午夜／晚子流派不强行混合 |
| 时间规则 | IANA时区、DST缺失／重复时间检测、可选均时差／地方平太阳时 | 真太阳时不是唯一公认命理规范 |
| 十年大运 | 由前后节与顺逆按三日一岁计算，输出近似起运时间 | 不自动假定性别或吉凶，不保证不同流派换算一致 |
| 24节气 | 太阳视黄经求根；另写二分法复算 | 同一星历模型的数值交叉检查不是第三方独立验证 |
| 西方星盘 | 十星体、上升、天顶、Placidus/整宫、宫位与时间敏感性 | 已增加9星体及ASC/MC低精度独立模型校验，已完成12宫头×12公开案例独立几何近似核查；仍无真实JPL DE高精度月球/冥王星核验或行星相位 |
| 六语言网页 | 78牌、64卦、离线网页体验 | **网页尚不运行八字和星盘计算** |

**非常关键的历算诚实性：** 本地缺少 Swiss Ephemeris 外部星历文件时，`pyswisseph` 即使请求 `swieph`，也可能实际回退为 `moseph`。新版检测并公开真实使用的引擎；可用 `--strict-ephemeris` 禁止静默回退。`--cross-check` 若最终两次都采用 Moshier，则明确标为**不构成独立验证**。

2024年的22个节气**公历日期**已经与香港天文台当年官方历表比较一致。这个核验不证明所有节气精确到分秒，更不意味着有科学的个人命运预测能力。[查看完整计算规则及资料来源](references/astronomy-computation.md)。

## 重要的开源许可证变化

**从 v1.3 起，完整整合包从 MIT 改为 AGPL-3.0-or-later**，因为新模块需要 `pyswisseph` / Swiss Ephemeris。此前的 v1.2 MIT 授权不受影响，已保留原许可证文档。第三方库/商用部署可能还有单独义务，发布前请阅读 [`LICENSING.md`](LICENSING.md)。不要把 v1.3 当作无条件 MIT 包传播。

## v1.3.2：独立几何与 JPL 官方数据核对

```bash
# 6个公开时刻 ×（9星体+上升+天顶）=66个模型级检查
python scripts/verify_ephemeris.py --strict

# 运行本机环境诊断（不发送任何网络遥测）
python scripts/install_diagnostics.py --require-astronomy

# 全部12宫头的独立几何与独立天文近似验证（12例共144项）
python scripts/verify_placidus.py --strict

# 显式联网，从JPL Horizons官方域名获取月球、冥王星在公开日期的视黄经
# 当前受限环境未能取回任何结果；在可联网的 Windows 上才可继续
python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --output-dir horizons-audit-output

# 使用已保存的官方原始返回复核；本地存档并非官方数字签名
python scripts/fetch_horizons.py --from-archive horizons-audit-output --strict

# 另外提供手工输入外部数据的数值比较（不能认证真实JPL来源）
python scripts/compare_horizons_fixture.py --file LOCAL_REFERENCE.json --strict
```

Windows 用户可在已经解压的目录中审阅并执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows-smoke-test.ps1 -CheckCodexInstalled
```

它创建独立虚拟环境并通过 pip 安装额外星历依赖。**本轮已获得你在 Windows 上三项 Swiss 基础计算 PASS 的反馈，但 v1.3.5 全套 Windows 实机回归及 JPL 正式比较仍需运行。** 运行后会在本机生成不含姓名、出生资料和完整本地路径的检查报告。

## 在 Codex 中安装和测试

将整个 `symbolic-reflection-support` 文件夹复制到 `%USERPROFILE%\.codex\skills\`，确保存在 `SKILL.md`；执行 `$symbolic-reflection-support`。有些宿主客户端只加载技能指令、不提供执行本地 Python 的权限，不能保证所有客户端都能真实运行排盘脚本。

```bash
python scripts/validate_skill.py
python scripts/build_demo.py --check
python -m unittest discover -s tests -v
# 若要验证完整星历测试，先安装 requirements-astronomy.txt
```

GitHub 仓库上传、Description、Topics、Actions 和 Pages 的真实发布步骤见 [`PUBLISHING.md`](PUBLISHING.md)。**本地 ZIP 制作完成，不等于远程 GitHub 仓库已经部署。**


## v1.3.3-rc1：冥王星目标编号纠正（验收候选）

**重要勘误：** v1.3.2 使用 Swiss 默认 `PLUTO` 直接对照 JPL `999`，不是严格同一目标。Swiss 默认行星位置是冥王星**系统质心**，应对照 JPL `9`；JPL `999` 是冥王星本体中心。新版官方取数程序分别请求月球 `301`、冥王星系统质心 `9` 和本体中心 `999`。只有同时取得两份真实的 JPL 冥王星原始响应，才能核对它们的角距离；若还要直接用 Swiss 本体中心复核，需要独立安装 `sepm9999.se1`，不可用默认质心替代。

```bash
python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --targets Moon PlutoBarycenter PlutoCenter --output-dir horizons-audit-output
python scripts/fetch_horizons.py --from-archive horizons-audit-output --strict --targets Moon PlutoBarycenter PlutoCenter
```

详见 [JPL目标身份验收规则](references/jpl-target-verification.md)。**当前环境无法访问 JPL API：直接官方验收仍未完成。** 历史36项公开二手基准数值一致性不等于本轮获得NASA原始数据。

## v1.3.4-rc1：独立星历文件与官方验收流程

```bash
# 先检查自行获取的 Swiss 冥王星本体中心数据：
python scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path EPHE_ROOT

# 在允许访问官方 API 的环境中，提供真实的联系邮箱或项目地址：
python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --targets Moon PlutoBarycenter PlutoCenter --output-dir horizons-audit-output

# 另加 --compare-swiss-center --swiss-ephe-path EPHE_ROOT 才会测试 Swiss 9999 与 JPL 999。
```

ZIP 不含 Swiss 授权二进制星历、不含 NASA 原始响应，也不含个人出生资料。


## v1.3.5-rc1：Windows Python 3.13 修复与最终 JPL 审计

前版在新 `pysweph` 下可能因 `calc_ut()` 多一个返回值、宫头多一个空占位而报错。新版已在星盘、八字、节气、宫位校验和 JPL 审计调用链统一处理；请不要反复重装 Python。

```powershell
py -3 -m pip install --only-binary=:all: -r requirements-astronomy.txt
py -3 scripts/install_diagnostics.py --require-astronomy
py -3 scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path "$env:USERPROFILE\.swisseph\ephe"
powershell -ExecutionPolicy Bypass -File .\scripts\windows-jpl-audit.ps1
```

最后一条为显式联网操作，需要你的真实联系地址，只查询公开测试日期。官方数据仍待在可联网的 Windows 环境取得；不能把用户反馈的三项本地 Swiss PASS 误写成 NASA/JPL 高精度验收。
