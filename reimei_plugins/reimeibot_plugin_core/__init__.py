import nonebot
from nonebot import get_driver
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from .config import Config

from reimei_api.rule import globalWhitelisted
from reimei_api.permission import isMaintainer
from reimei_api.help import getHelp
from nonebot.plugin import PluginMetadata

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

# 注册插件
__plugin_meta__ = PluginMetadata(
    name="Reimei核心",
    description="ReimeiBot调试与插件管理系统",
    usage=config.docs,
    config=Config,
    extra={
        "Enabled": True
    },
)

# 事件合集
debug = on_command("/debug", rule=globalWhitelisted,
                   permission=SUPERUSER, aliases={"/调试"}, priority=10, block=True)
plugin_list = on_command(("/plugin", "list"), rule=globalWhitelisted,
                         aliases={"/插件列表"}, priority=10, block=True)
plugin_help = on_command(("/plugin", "help"), rule=globalWhitelisted,
                         aliases={"/帮助", "/help"}, priority=10, block=True)
plugin_turn = on_command(("/plugin", "turn"), rule=globalWhitelisted,
                            permission=isMaintainer, aliases={"/开关插件"}, priority=10, block=True)


@debug.handle()
async def debugHandle(args: Message = CommandArg()):
    if message := args.extract_plain_text():
        await debug.finish(Message(message))
    else:
        await debug.finish("一切正常！")


@plugin_list.handle()
async def pluginList():
    plugin: nonebot.plugin.Plugin
    plugins: set[nonebot.plugin.Plugin] = nonebot.get_loaded_plugins()
    string_list = "====ReimeiBot插件列表====\n"
    for index, plugin in enumerate(plugins):
        if plugin.metadata:
            string_list += (f"{index}. {plugin.metadata.name}（{plugin.name}）"
                            f"[{'启用' if plugin.metadata.extra['Enabled'] else '禁用'}]\n\n")
        else:
            string_list += f"{index}. {plugin.name} [不支持ReimeiBot协议]"
    await plugin_list.finish(string_list)


@plugin_help.handle()
async def pluginHelp(args: Message = CommandArg()):
    if package := args.extract_plain_text():
        if plugin := nonebot.get_plugin(package):
            if plugin.metadata:
                await plugin_help.finish(await getHelp(package))
            else:
                await plugin_help.finish(f"插件包 {package} 不支持ReimeiBot协议，无法查看帮助哦~")
        else:
            await plugin_help.finish(f"插件包 {package} 不存在哦~")
    else:
        await plugin_help.finish(config.docs)


@plugin_turn.handle()
async def pluginInspect(args: Message = CommandArg()):
    if package := args.extract_plain_text():
        if package in config.system_plugins:
            await plugin_turn.finish(f"插件包 {package} 为黎明系统插件，不可禁用哦！")
        if plugin := nonebot.get_plugin(package):
            if plugin.metadata:
                plugin.metadata.extra["Enabled"] = not plugin.metadata.extra["Enabled"]
                await plugin_turn.finish(f"插件包 {package} 的开关已成功"
                                            f"{'启用' if plugin.metadata.extra['Enabled'] else '禁用'}"
                                            f"了哦！")
            else:
                await plugin_turn.finish(f"插件包 {package} 不支持ReimeiBot协议，无法调动开关哦~")
        else:
            await plugin_turn.finish(f"插件包 {package} 不存在哦~")
    else:
        await plugin_turn.finish("请指定插件包呐~")
