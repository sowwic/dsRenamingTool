import os
import json
from string import Formatter

import pymel.core as pm
from dsRenamingTool import const


class Template(object):

    INDEX_PADDING = "index_padding"
    INDEX_START = "index_start"
    UPPER_SUFFIX = "upper_case_suffix"

    def __repr__(self):
        return "Template {0}: {1}".format(self.name, self.mapping)

    def __init__(self, file_path):
        # type: (str) -> None
        self.file_path = file_path
        self.name = os.path.basename(file_path).split(".")[0]
        with open(file_path, "r") as json_file:
            self.data = json.load(json_file)  # type: dict

    @property
    def is_default(self):
        # type: () -> bool
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
        # type: () -> bool
        return self.data.get(self.UPPER_SUFFIX, False)

    @mapping.setter
    def mapping(self, fmt_string):
        self.data["mapping"] = fmt_string

    @property
    def is_indexed(self):
        return "index" in self.get_tokens()

    @property
    def on_disk(self):
        return os.path.isfile(self.get_file_path_from_name())

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
        # type: (pm.PyNode) -> str
        node_type = pm.objectType(node)
        if node_type == "transform":
            dependNodes = pm.listRelatives(node, c=1)
            if dependNodes:
                node_type = pm.objectType(dependNodes[0])
        suffix = self.suffix_aliases.get(node_type, "obj")
        if self.upper_case_suffix:
            suffix = suffix.upper()
        return suffix

    def get_file_path_from_name(self):
        return os.path.join(Template.get_templates_dir(), "{}.json".format(self.name))

    def export_to_json(self, file_path=None):
        # type: (str) -> None
        if not file_path:
            file_path = self.get_file_path_from_name()
        with open(file_path, "w") as json_file:
            json.dump(self.data, json_file, indent=4)

    @ staticmethod
    def get_templates_dir():
        module_path = pm.moduleInfo(moduleName=const.MAYA_MODULE_NAME, path=True)  # type: str
        return os.path.join(module_path, "templates")

    @ staticmethod
    def list_template_files():
        # type: () -> list[str]
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
