import pymel.core as pm
import json
import logging

LOGGER = logging.getLogger(__name__)


class RenameUtils:

    @classmethod
    def rename(cls, obj, newName, aliasesDict, prefix=None, suffix=None, autoSuffix=False, indexing=True, indexPadding=1, startIndex=0):
        if not newName:
            LOGGER.warning("No name was specified")
            return

        if prefix:
            baseName = "{0}_{1}".format(prefix, newName)
        else:
            baseName = newName

        if autoSuffix:
            suffix = cls.getSuffix(obj, aliasesDict)

        fullName = cls.genName(obj, baseName, suffix, padding=indexPadding + 1, start=startIndex, indexing=indexing)
        pm.rename(obj, fullName)

        return fullName

    @classmethod
    def genName(cls, obj, name, suffix=None, indexing=True, padding=2, start=0):
        if suffix:
            suffix = "_" + suffix
        else:
            suffix = ""

        if indexing:
            index = start
            version = str(index).zfill(padding)
            testName = name + version + suffix

            if pm.objExists(testName):
                while pm.objExists(testName):
                    if testName == obj:
                        return testName
                    index += 1
                    version = str(index).zfill(padding)
                    testName = name + version + suffix

            else:
                "Name is unique: ", testName

        else:
            testName = name + suffix

        return testName

    @classmethod
    def getSuffix(cls, obj, aliasesDict):
        objType = pm.objectType(obj)
        aliasesDict = json.loads(pm.optionVar["dsRenamingToolSuffixAliases"])
        if objType == "transform":
            dependNodes = pm.listRelatives(obj, c=1)
            if dependNodes:
                objType = pm.objectType(dependNodes[0])

        try:
            suffix = aliasesDict[objType]
        except KeyError:
            LOGGER.warning("No suffix recorded for type: {0}.\nUpdate aliases using suffix alias editor.".format(objType))
            suffix = "OBJ"

        return suffix
