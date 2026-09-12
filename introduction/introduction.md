[[中文]](./introduction-zh_cn.md) | [English]

### ColorMe

A simple plugin that lets players choose their own name color:

```
!!color <color>
```

It works by making players join one of 16 vanilla scoreboard teams, one per chat color.
Both Minecraft 1.12.x and 1.13+ are supported.

After enabling the plugin, initialize the teams once:

```
!!color install
```

When you no longer need the plugin, remove the teams:

```
!!color uninstall
```

Other commands: `!!color list` lists the colors. `install` and `uninstall` require
MCDReforged permission level 2 (helper) or higher.

Note: a player can only be in one team, so this plugin may conflict with other systems
that use vanilla teams for prefix/suffix/permissions.
