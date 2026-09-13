[中文] | [[英文]](./introduction.md)

### ColorMe

一个让玩家自行选择名字颜色的简单插件：

```
!!color <color>
```

原理是让玩家加入 16 个原版计分板队伍（每种聊天颜色一个队伍），
同时支持 Minecraft 1.12.x 和 1.13+。

启用插件后，先初始化一次队伍：

```
!!color install
```

不再需要此插件时，删除队伍：

```
!!color uninstall
```

其他命令：`!!color list` 列出所有颜色；`install` 和 `uninstall` 需要
MCDReforged 权限等级 2（helper）或更高。

注意：一名玩家同一时间只能属于一个队伍，因此本插件可能与其他使用原版队伍
实现前后缀/权限的系统冲突。
