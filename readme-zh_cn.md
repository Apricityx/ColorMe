[中文] | [[English]](./readme.md)

# ColorMe

一个简单的 [MCDReforged](https://github.com/MCDReforged/MCDReforged) 插件，让玩家自行选择
名字颜色。它只是 Minecraft 原版计分板队伍系统的一层薄封装：ColorMe 创建 16 个队伍
（每种聊天颜色一个），玩家通过加入队伍来改变颜色。

## 功能

- 玩家通过 `!!color <color>` 更改自己的名字颜色
- 支持全部 16 种原版 Minecraft 聊天颜色
- 同时支持 Minecraft **1.12.x**（`/scoreboard teams`）和 **1.13+**（`/team`）
- 队伍状态完全由 Minecraft 服务端管理；ColorMe 不实现自定义渲染，也不维护第二份状态
- 插件消息内置英文和中文，跟随命令来源的 MCDReforged 语言偏好
- ColorMe 只创建、修改和删除自己的 `__` 前缀队伍

## 环境要求

- MCDReforged 2.x
- Python 3.10+
- Minecraft Java Edition 1.12.x 或 1.13+（命令语法根据服务端上报的版本自动选择）

## 安装

1. 将 `ColorMe-vX.Y.Z.mcdr` 放入 MCDReforged 的 `plugins/` 目录。
2. 重启或重载 MCDReforged。
3. 执行一次初始化：

```
!!color install
```

## 命令

| 命令 | 可用者 | 权限 | 说明 |
| --- | --- | --- | --- |
| `!!color <color>` | 玩家 | 所有人 | 加入指定颜色的队伍 |
| `!!color list` | 玩家和控制台 | 所有人 | 列出可用颜色 |
| `!!color install` | 玩家和控制台 | helper（等级 2） | 创建 ColorMe 队伍并设置颜色 |
| `!!color uninstall` | 玩家和控制台 | helper（等级 2） | 删除 ColorMe 队伍 |

可用颜色：

```
red, blue, green, yellow, light_purple, aqua, white, black, gray, gold,
dark_red, dark_blue, dark_green, dark_aqua, dark_purple, dark_gray
```

## 工作原理

1. `!!color install` 创建 `__red`、`__blue` 等队伍，并用原版队伍颜色选项设置颜色。
2. `!!color red` 让执行命令的玩家加入 `__red` 队伍。
3. 原版服务端会把队伍关系同步给客户端，客户端按队伍颜色渲染玩家名字。
   整个过程不涉及客户端修改。

在 Minecraft 1.12.x 上插件使用 `/scoreboard teams add|remove|join|option`；
在 1.13+ 上使用 `/team add|remove|join|modify`。

## 语言（i18n）

插件消息提供英文（`en_us`）和中文（`zh_cn`）。每条回复的语言取自命令来源的
MCDReforged 语言偏好：控制台输出跟随 MCDR 语言设置，每位玩家看到自己偏好的语言。
其他语言回退到英文，`zh_*` 语言回退到中文。公开的换色广播使用执行换色玩家所用的语言。

## 注意事项与限制

- 一名玩家同一时间只能属于一个队伍（原版行为）。如果你的服务器用队伍实现其他功能
  （前后缀、权限等），玩家加入 ColorMe 队伍时会自动退出原队伍，请确认不会破坏现有系统。
- ColorMe 不会修改或删除不以 `__` 为前缀的队伍。为避免冲突，请不要创建名为
  `__<颜色>` 的自有队伍。
- `!!color install` 可以重复执行。若队伍已存在，原版服务端可能输出 "already exists"
  日志，但颜色仍会被正确设置。
- `!!color uninstall` 只删除 ColorMe 的队伍，可以重复执行。
- 彩色名字需要客户端支持队伍颜色；ViaVersion/ViaFabric 等协议转换层不会改变队伍数据本身。

## 开发

开发环境、测试与发布流程见 [CONTRIBUTING.md](./CONTRIBUTING.md)（英文）或
[CONTRIBUTING-zh_cn.md](./CONTRIBUTING-zh_cn.md)（中文）。

## 许可证

ColorMe 使用 GNU General Public License v3.0 许可，详见 [LICENSE](./LICENSE)。
