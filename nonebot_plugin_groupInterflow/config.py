from nonebot import get_driver
from pydantic import BaseModel, Extra
from pathlib import Path
from typing import List

import os


class Config(BaseModel, extra=Extra.ignore):
    groupInterflow_format:str = "<{userName}>在群<{groupId}>说了\n>>>"
    groupInterflow_group_map = {}
    groupInterflow_on:bool = True
    groupInterflow_path:Path = Path(os.path.dirname(__file__))
    groupInterflow_except_peoples:List[int] = [1497250139,]
    

plugin_config = Config.parse_obj(get_driver().config)