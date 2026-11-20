## v1.3.5-rc2：替换代码之前先保留 NASA 审计文件

你本机已有真实的 `.horizons-audit`，里面含 NASA HTTP 响应及比较结果。**不要删除此目录，不要上传包含私人联系信息的命令历史。** 把此文件夹单独备份后再覆盖安装新版 `symbolic-reflection-support` 文件夹。ZIP 不含第三方 Swiss 星历数据，因此也不需要重新下载已经就绪的 `sat/sepm9999.se1`。

PowerShell 5.1 的 UTF-8 输出建议设定：

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

然后进入技能目录，执行：

```powershell
py -3 scripts/check_horizons_hashes.py --archive .horizons-audit
py -3 -m unittest discover -s tests -v
```

**预计旧版 `v1.3.5-rc1` 产生的归档会显示 `PASS_RAW_ONLY_LEGACY`**，而不是 `FAIL`：清单 `raw_sha256` 是原始 HTTP 响应哈希，并不是整个 `horizons_*_public.json` 文件哈希。旧清单没有承诺完整文件的哈希，新版以后产生的记录会增加 `archived_json_sha256`，同时检验两个对象。`PASS_RAW_ONLY_LEGACY` 只是内部一致性检查，并不是重新认证 NASA TLS 来源。

# Windows / Codex 安装与验收说明（v1.3.5-rc2）

## 一、安装前检查

1. Windows 10/11，Python 3.10 或更新版本。可使用 `py --version` 检查。
2. 将完整安装 ZIP 解压到 `%USERPROFILE%\.codex\skills\` 下，确保：

```text
%USERPROFILE%\.codex\skills\symbolic-reflection-support\SKILL.md
```

**不要**产生多余的 `symbolic-reflection-support\symbolic-reflection-support\SKILL.md` 双层目录。

3. 先备份旧技能目录，确认新解压版本正常后再清理旧版本。

## 二、在 PowerShell 中检查

```powershell
cd "$env:USERPROFILE\.codex\skills\symbolic-reflection-support"
py -3 -m pip install --only-binary=:all: -r requirements-astronomy.txt
py -3 scripts/validate_skill.py
py -m unittest discover -s tests -q
py -3 scripts/install_diagnostics.py --require-astronomy
```

高级（执行会创建虚拟环境、并由 pip 安装依赖）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows-smoke-test.ps1 -CheckCodexInstalled
```

该命令**必须由你在真实 Windows 电脑执行**；Linux 模拟或 GitHub Windows runner 测试不能代替 Codex 宿主安装确认。

## 三、验证 JPL 和 Swiss 本体中心（非必选）

这里使用**公开中性日期**，不涉及私人出生资料。

```powershell
py -3 scripts/fetch_horizons.py --fetch --strict --contact "YOUR_CONTACT@example.com" --targets Moon PlutoBarycenter PlutoCenter --output-dir horizons-audit-output
py -3 scripts/fetch_horizons.py --from-archive horizons-audit-output --strict --targets Moon PlutoBarycenter PlutoCenter
```

上述命令会访问 NASA/JPL 官方服务。根据官方公平使用规则，需要设置自己的真实联系邮箱或已经公开的项目 HTTPS 地址；如果官方服务无法访问，程序应提示失败，绝不产生“已验证”的假记录。

Swiss 冥王星本体中心请从 [Swiss 官方上游 GitHub](https://github.com/aloistr/swisseph/blob/master/ephe/sat/sepm9999.se1) 或 Astrodienst 另行获取许可允许的 `sepm9999.se1`，放入 `EPHE_ROOT\sat\sepm9999.se1`。随后：

```powershell
py -3 scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path "C:\PATH\TO\EPHE_ROOT"
```

若要进一步与 JPL 999 比较，在 `--fetch` 命令中添加 `--compare-swiss-center --swiss-ephe-path "C:\PATH\TO\EPHE_ROOT"`。

## 四、结果界限

- 本次发布版本：**v1.3.5-rc2 候选版**。用户已有官方 JPL 在线比较成功日志，但发行包不含真实原始响应，仍需在本人电脑执行哈希与全量测试。
- 仅 `--check-center-ephe` 成功不代表已经获得 JPL 数据；只证明本地 Swiss 9999 计算能够正常运行。
- `--from-archive` 不能重新证明文件来源于 NASA。
- 星盘、八字、塔罗等象征性解读不能作为科学的命运、健康或财务预测。

更多详见 [`references/official-closure-checklist.md`](references/official-closure-checklist.md)。

## 五、Windows Python 3.13 与 JPL 最终验收

如果以前 `pip install pyswisseph` 报缺少 Visual C++，不要为了修复当前问题重新安装编译器。v1.3.5 的 `requirements-astronomy.txt` 会在 Python 3.13 自动选择有 Win64 wheel 的 `pysweph==2.10.3.6`。两包的导入名都是 `swisseph`，请不要同时安装两个。

```powershell
cd "$env:USERPROFILE\.codex\skills\symbolic-reflection-support"
py -3 -m pip install --only-binary=:all: -r requirements-astronomy.txt
py -3 scripts/install_diagnostics.py --require-astronomy --installed
py -3 scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path "$env:USERPROFILE\.swisseph\ephe"

# 实际联网 JPL，需要输入真实联系邮箱或项目 HTTPS URL：
powershell -ExecutionPolicy Bypass -File .\scripts\windows-jpl-audit.ps1
```

最后一条会查询**公开测试时刻**的月球 `301`、冥王星质心 `9` 和本体中心 `999`。强制使用 Swiss 文件引擎 `swieph`，并对照 Swiss `9999`。记录原始 JPL JSON、URL 和 SHA-256；如果 DNS/HTTP/时间或数值核对失败，保留 `fetch_failure.json`，不得将结果称作 PASS。

**已确认：**你反馈 Windows 上三个本地 Swiss 测试 PASS。**未确认：**新 v1.3.5 全套 Windows 测试、NASA 官方原始响应、同一时刻 9↔999 角距离及 Swiss 9999↔JPL 999 的正式差异。
