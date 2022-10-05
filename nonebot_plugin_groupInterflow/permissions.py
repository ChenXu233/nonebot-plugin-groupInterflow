from typing import List, Dict
from pathlib import Path
try:
    import ujson as json # type: ignore
except ModuleNotFoundError:
    import json
    
from .config import plugin_config


class Handler:
    
    def __init__(self, config=plugin_config):
        
        self.path: Path = Path(config.groupInterflow_path) / "pending.json"
        if not self.path.exists():
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(json.dumps(dict()))
                f.close()   
    
    def get_group_request(self,thisGid: str)-> List[str]:
        '''
            查看该群有多少请求
        '''
        file = self.load_json(self.path)
        return file[thisGid]

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

p_handler = Handler()