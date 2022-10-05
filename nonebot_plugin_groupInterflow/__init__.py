from nonebot import on_message, on_command
from nonebot.log import logger
from nonebot.rule import Rule
from nonebot.params import Arg, CommandArg
from nonebot.matcher import Matcher
from nonebot.adapters import Bot
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN,GROUP_OWNER
PERM_EDIT = GROUP_ADMIN | GROUP_OWNER | SUPERUSER

from .config import plugin_config
from .group2group_map import g_handler
from .permissions import p_handler

import unicodedata

def remove_control_characters(string:str) -> str:
    """将字符串中的控制符去除

    Arg:
        string (str): 需要去除的字符串

    Return:
        (str): 经过处理的字符串
    """
    return "".join(ch for ch in string if unicodedata.category(ch)[0]!="C")


async def _chcker(event:GroupMessageEvent)->bool:  # type: ignore
    group2group = g_handler.get_dict()
    if int(event.user_id) in plugin_config.groupInterflow_except_peoples:
        return False
    return True if str(event.group_id) in group2group else False


GroupInterflow = on_message(rule=Rule(_chcker),priority=10,block=False)
GroupInterflow_adGroupMap = on_command(cmd = "添加群聊互通", permission=PERM_EDIT, priority=1, block=True)
GroupInterflow_rmGroupMap = on_command(cmd = "删除群聊互通", permission=PERM_EDIT, priority=1, block=True)
GroupInterflow_lookRequest = on_command(cmd = "查看群互通请求", permission=PERM_EDIT, priority=1, block=True)
GroupInterflow_agreeRequest = on_command(cmd = "同意群互通请求", permission=PERM_EDIT, priority=1, block=True)
GroupInterflow_addrule = on_command(cmd="添加互通规则", permission=PERM_EDIT, priority=1, block=True)# TODO
GroupInterflow_rmrule = on_command(cmd="删除互通规则", permission=PERM_EDIT, priority=1, block=True)# TODO



@GroupInterflow.handle()
async def _sender(event: GroupMessageEvent, bot: Bot):
    
    group2group = g_handler.get_dict()
    userInfo = await bot.call_api(
        "get_group_member_info", 
        group_id=event.group_id,
        user_id=event.user_id,
        no_cache=True
        )
    username:str = userInfo['card'] if userInfo["card"] else userInfo['nickname']
    username:str = remove_control_characters(username)
    eventMsg:Message = event.get_message()
    msg = Message(
        plugin_config.groupInterflow_format.format(
            userName=username,
            groupId=event.group_id
            )
        )
    msg += eventMsg
    
    for i in group2group[str(event.group_id)]:
        try:
            await bot.call_api(
                "send_group_msg", 
                group_id=i,
                message=msg
                )
        except ActionFailed:
            g_handler.remove_group(str(event.group_id),i)
            
    await GroupInterflow.finish()
    

@GroupInterflow_adGroupMap.handle()
async def _ad(matcher: Matcher, event: GroupMessageEvent, bot: Bot, args: Message = CommandArg()):
    
    groups:str = args.extract_plain_text()
    if groups:
        matcher.set_arg("gid2s", groups)  # type: ignore


@GroupInterflow_adGroupMap.got(key='gid2s',prompt="想在本群互通的群?")
async def _adh(event: GroupMessageEvent, bot: Bot, ad =  Arg("gid2s")):
    
    groups = [str(i["group_id"]) for i in await bot.call_api('get_group_list')]
    ad = ad.split(',')
    for i in ad:
        if i in groups:
            p_handler.add_group(i,str(event.group_id))
        else:
            await GroupInterflow_adGroupMap.send("机器人不在群{}".format(i))
            await bot.call_api("send_group_msg",group_id=int(i),message="来自群{}的互通申请等待同意".format(event.group_id))
    await GroupInterflow.send('添加成功,等待对方群聊同意')



@GroupInterflow_rmGroupMap.handle()
async def _rm(matcher: Matcher, event: GroupMessageEvent, bot: Bot, args: Message = CommandArg()):
    
    groups:str = args.extract_plain_text()
    if groups:
        matcher.set_arg("gid2s", groups)  # type: ignore


@GroupInterflow_rmGroupMap.got(key='gid2s',prompt="不想在本群互通的群?")
async def _rmh(event: GroupMessageEvent, bot: Bot, ad =  Arg("gid2s")):
    
    ad = ad.split(',')
    for i in ad:
        g_handler.remove_group(str(event.group_id),i)
    await GroupInterflow.send("删除成功")



@GroupInterflow_lookRequest.handle()
async def _lq(event: GroupMessageEvent, bot: Bot):
    
    gids = p_handler.get_group_request(thisGid=str(event.group_id))
    msg = Message("有以下群聊请求中!:")+Message(str(gids)[1:-1])
    print(msg)
    await GroupInterflow_lookRequest.finish(msg)
    
    

@GroupInterflow_agreeRequest.handle()
async def _aq(matcher: Matcher,event: GroupMessageEvent,bot: Bot, args: Message = CommandArg()):
    
    groups:str = args.extract_plain_text()
    if groups:
        matcher.set_arg("gid2s", groups)  # type: ignore


@GroupInterflow_agreeRequest.got(key='gid2s',prompt="想同意把本群互通的群?")
async def _aqh(event: GroupMessageEvent, bot: Bot, ad = Arg("gid2s")):
    
        ad = ad.split(',')
        gids = p_handler.get_group_request(thisGid=str(event.group_id))
        for i in ad:
            if i not in gids:
                await GroupInterflow_agreeRequest.send("群{}不在请求列表".format(i))
            else:
                g_handler.add_group(str(event.group_id), i)
                p_handler.remove_group(i, str(event.group_id))
                print(event.group_id,i)
                await bot.call_api("send_group_msg",group_id=int(i),message="发向群{}的互通申请已同意".format(event.group_id))
                await GroupInterflow_agreeRequest.send("群{}的互通申请已同意".format(i))
                
        await GroupInterflow_agreeRequest.finish()
            
