import os
import json
import pymel.core as pm
from dsRenamingTool import const
from string import Formatter


class Template(object):

    INDEX_PADDING = "index_padding"
    INDEX_START = "index_start"

    def __repr__(self) -> str:
        return "Template {0}: {1}".format(self.name, self.mapping)

    def __init__(self, file_path):
        # type: (str) -> None
        self.__name = os.path.basename(file_path).split(".")[0]
        with open(file_path, "r") as json_file:
            self.data = json.load(json_file)

    @property
    def name(self):
        return self.__name

    @property
    def suffix_aliases(self):
        # type: () -> dict
        return self.data.get("suffix_aliases", dict())

    @property
    def mapping(self):
        # type: () -> str
        return self.data["mapping"]

    @property
    def is_indexed(self):
        return "index" in self.get_tokens()

    def get_tokens(self):
        return [fname for _, fname, _, _ in Formatter().parse(self.mapping) if fname]

    def generate_name(self, tokens_map, node=None):
        suffix_req_but_not_provided = "suffix" in self.mapping and "suffix" not in tokens_map
        if node and suffix_req_but_not_provided:
            tokens_map["suffix"] = self.get_suffix(node)

        if not self.is_indexed:
            return self.mapping.format_map(tokens_map)

        index = self.data.get(self.INDEX_START, 0)
        padding = self.data.get(self.INDEX_PADDING, 1) + 1
        obj_name = self._generate_indexed_name(tokens_map, index, padding)
        while pm.objExists(obj_name):
            index += 1
            obj_name = self._generate_indexed_name(tokens_map, index, padding)
        return obj_name

    def _generate_indexed_name(self, tokens_map, index, padding):
        index = str(index).zfill(padding)
        tokens_map["index"] = index
        return self.mapping.format_map(tokens_map)

    def get_suffix(self, node):
        node_type = pm.objectType(node)
        if node_type == "transform":
            dependNodes = pm.listRelatives(node, c=1)
            if dependNodes:
                node_type = pm.objectType(dependNodes[0])
        return self.suffix_aliases.get(node_type, "obj")

    @ staticmethod
    def get_templates_dir():
        module_path = pm.moduleInfo(moduleName=const.MAYA_MODULE_NAME, path=True)  # type: str
        return os.path.join(module_path, "templates")

    @ staticmethod
    def list_template_files():
        templates_dir = Template.get_templates_dir()
        template_paths = []
        for file_name in os.listdir(templates_dir):
            if not file_name.endswith(".json"):
                continue
            template_paths.append(os.path.join(templates_dir, file_name))
        return template_paths

    @ classmethod
    def get_templates(cls):
        return [cls(file_path) for file_path in cls.list_template_files()]


if __name__ == "__main__":
    sel = pm.selected()
    # Temp renaming
    for node in sel:
        for temp in Template.get_templates():
            tk_map = {"side": "temp",
                      "name": "temp",
                      "suffix": "temp"}
            new_name = (temp.generate_name(tk_map, node=node))
        node.rename(new_name)

    # Actual naming
    for node in sel:
        tk_map = {"side": "c",
                  "name": "test"}
        new_name = (temp.generate_name(tk_map, node=node))
        node.rename(new_name)
