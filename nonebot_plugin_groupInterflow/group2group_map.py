from nonebot.log import logger
from typing import List, Dict
from pathlib import Path
try:
    import ujson as json # type: ignore
except ModuleNotFoundError:
    import json
    
from .config import plugin_config


class Handler:
    
    def __init__(self, config=plugin_config):
        self.on: bool = config.groupInterflow_on
        self.path: Path = Path(config.groupInterflow_path) / "config.json"
        self.group_map: Dict = config.groupInterflow_group_map
        
        if not self.on:
            logger.warning(f"已全局禁用群聊互通")
        else:
            if not self.path.exists():
                with open(self.path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(dict()))
                    f.close()
        self.load_default_settings()

    def load_default_settings(self):
        file = self.load_json(self.path)
        file.update(self.group_map)
        
        
    def get_dict(self) -> Dict[str,List[str]]:
        '''
            获取group2groupMap
        '''
        file = self.load_json(self.path)
        return file

    def add_group(self, gid: str, gid2: str) -> None:
        '''
            Update覆盖
        '''
        file:Dict[str,list] = self.load_json(self.path)
        try:
            values = file[gid]
        except KeyError:
            values = []
        if gid2 not in values:
            values.append(gid2)
            file.update({gid: values})
        self.save_json(self.path, file)
    
    def remove_group(self, gid: str, gid2: str) -> None:
        '''
            尝试Pop
        '''
        file = self.load_json(self.path)
        try:
            values = file[gid]
            values.remove(gid2)
            if values == []:
                file.pop(gid)
        except KeyError:
            pass
        finally:
            self.save_json(self.path, file)
        
    def save_json(self, file: Path, data: Dict[str, List]) -> None:
        if file.exists():
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def load_json(self, file: Path) -> Dict[str, List]:
        if file.exists():
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}

g_handler = Handler()