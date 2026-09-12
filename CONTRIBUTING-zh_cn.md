[中文] | [[English]](./CONTRIBUTING.md)

# 为 ColorMe 贡献代码

感谢你愿意改进 ColorMe。请保持改动小而可预测，并聚焦于原版队伍行为。

## 项目结构

```
color_me/
  __init__.py        命令注册与命令处理
  colors.py          颜色与队伍名的唯一来源
  team_commands.py   按版本生成的原版队伍命令
  i18n.py            英文与中文插件消息
tests/
  helpers.py         伪造的 MCDR 服务端与命令来源
  test_*.py          单元测试与 MCDR API 测试
  e2e/               针对真实 Minecraft 服务端的端到端测试
```

## 开发环境

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## 运行测试

单元测试与 MCDR API 测试（快速，无需网络和服务端）：

```bash
pytest -m "not e2e"
```

## 端到端测试

E2E 测试会下载原版服务端 jar，使用 `mcdreforged pack` 打包插件，在真实的
MCDReforged 实例中运行，通过 MCDR 控制台执行命令、用 RCON 校验队伍状态，
并使用两个 [mineflayer](https://github.com/PrismarineJS/mineflayer) 机器人
验证渲染出的名字颜色在两个客户端上一致。

前置条件：

- 与测试版本匹配的 Java 运行时（1.12.2 需要 Java 8，1.20.4 需要 Java 17+）。
  可通过 `JAVA_BIN` 指定 `java` 可执行文件。
- Node.js 与 npm（机器人测试需要）。
- 首次运行需要网络下载服务端 jar（缓存于 `tests/e2e/.cache/`）。

```bash
cd tests/e2e/js && npm install && cd ../../..
MCDR_E2E=1 MC_VERSION=1.20.4 pytest tests/e2e
MCDR_E2E=1 MC_VERSION=1.12.2 MCDR_E2E_LANGUAGE=zh_cn pytest tests/e2e
```

常用环境变量：

- `MCDR_E2E=1`：启用 E2E 测试。
- `MC_VERSION`：原版服务端版本（默认 `1.12.2`）。
- `MCDR_E2E_LANGUAGE`：测试实例使用的 MCDR 语言（默认 `en_us`）；控制台断言会随之变化，
  因此修改用户可见消息时请两种语言都跑一遍。
- `JAVA_BIN`：覆盖 `java` 可执行文件路径。
- `MCDR_E2E_KEEP=1`：保留 `tests/e2e/.run/` 下的 MCDR 工作目录，便于排查问题。

## 设计规则

- 颜色和队伍名只在 `color_me/colors.py` 中定义一次。
- ColorMe 只是原版队伍的薄封装。不要添加客户端渲染或第二份队伍/状态存储。
- 1.12.x 与 1.13+ 的队伍命令语法差异放在 `color_me/team_commands.py`。
- `install`/`uninstall` 必须可以安全地重复执行，且绝不能修改不以 `__` 为前缀的队伍。
- 玩家专属命令必须拒绝控制台来源。
- 错误消息要有用，并始终以原版服务端作为队伍状态的唯一事实来源。
  广播一条聊天消息并不代表队伍状态已经改变。

## 国际化（i18n）

- 所有用户可见文本都放在 `color_me/i18n.py`，通过 `tr(source, key, **kwargs)` 渲染。
  语言取自命令来源的 MCDReforged 偏好（`source.get_preference().language`）。
- `en_us` 与 `zh_cn` 必须始终包含相同的键和相同的占位符；`tests/test_i18n.py` 会强制检查。
- 不要在命令处理函数里硬编码用户可见字符串，而是为两种语言各添加一个键。
- 未知语言回退到 `en_us`，`zh_*` 语言回退到 `zh_cn`。

## 提交 Pull Request

- 提 PR 前先运行 `pytest -m "not e2e"`；CI 也会运行。
- 如果改动影响队伍同步，请用两个客户端运行 E2E 测试。
- 如果改动涉及用户可见消息，请运行两种语言的 E2E 测试。
- 说明兼容性影响，尤其是 1.12.x 与 1.13+ 的差异，以及其他使用原版队伍的插件。
- 避免无关重构。

## CI

- `ci.yml`：每次 push 和 PR 在 Python 3.10 与 3.13 上运行单元/API 测试，并构建 `.mcdr` 产物。
- `e2e.yml`：在 push 到 `master`、每周定时和手动触发时，运行 1.12.2（中文 MCDR）
  与 1.20.4（英文 MCDR）的端到端测试。
- `release.yml`：校验 tag、运行测试并发布 Release。

## 发布流程

1. 按[语义化版本](https://semver.org/)更新 `mcdreforged.plugin.json` 中的 `version`。
2. 若用户可见行为有变化，更新 readme/introduction。
3. 运行 `pytest -m "not e2e"`，最好再跑一遍 E2E。
4. 提交改动。
5. 创建并推送与元数据版本完全一致的 tag `vX.Y.Z`：

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

6. Release workflow 会校验版本、运行单元测试、打包 `ColorMe-vX.Y.Z.mcdr`，
   并创建带有自动生成说明和打包插件的 GitHub Release。

## 依赖

运行时依赖必须保持最小：仅 MCDReforged 本身。`requirements.txt` 会被打包进插件并由
MCDReforged 安装。仅测试用的依赖（pytest、Node.js/mineflayer）绝不能成为运行时依赖。
