import os
import json
import pymel.core as pm
from dsRenamingTool import const
from string import Formatter


class Template(object):

    INDEX_PADDING = "index_padding"
    INDEX_START = "index_start"
    UPPER_SUFFIX = "upper_case_suffix"

    def __repr__(self):
        return "Template {0}: {1}".format(self.name, self.mapping)

    def __init__(self, data):
        # type: (dict) -> None
        self.data = data

    @property
    def is_default(self):
        return self.name == "default"

    @property
    def suffix_aliases(self):
        # type: () -> dict
        return self.data.get("suffix_aliases", dict())

    @property
    def mapping(self):
        # type: () -> str
        return self.data["mapping"]

    @property
    def upper_case_suffix(self):
        return self.data.get(self.UPPER_SUFFIX, False)

    @mapping.setter
    def mapping(self, fmt_string):
        self.data["mapping"] = fmt_string

    @property
    def is_indexed(self):
        return "index" in self.get_tokens()

    def get_tokens(self):
        return [fname for _, fname, _, _ in Formatter().parse(self.mapping) if fname]

    def generate_name(self, tokens_map, node=None):
        # type: (dict, pm.PyNode) -> str
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
        suffix = self.suffix_aliases.get(node_type, "obj")
        if self.upper_case_suffix:
            suffix = suffix.upper()
        return suffix

    @classmethod
    def import_from_json(cls, file_path):
        # type: (str) -> Template
        with open(file_path, "r") as json_file:
            data = json.load(json_file)  # type: dict
        return cls(data)

    def export_to_json(self, file_path=None):
        # type: (str) -> None
        if not file_path:
            file_path = os.path.join(Template.get_templates_dir(), "{}.json".format(self.name))
        with open(file_path, "w") as json_file:
            json.dump(self.data, json_file, indent=4)

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
        return [cls.import_from_json(file_path) for file_path in cls.list_template_files()]


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
