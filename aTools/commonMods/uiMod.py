'''
========================================================================================================================
Author: Alan Camilo
www.alancamilo.com

Requirements: aTools Package

------------------------------------------------------------------------------------------------------------------------
To install aTools, please follow the instructions in the file how_to_install.txt

------------------------------------------------------------------------------------------------------------------------
To unistall aTools, go to menu (the last button on the right), Uninstall

========================================================================================================================
''' 

from maya import cmds
import os
FILE_PATH       = __file__

class BaseSubUI(object):
    def __init__(self, parent, buttonSizeDict):
        self.btnSizeDict    = buttonSizeDict
        self.parentLayout   = parent
        
        #get values
        self.ws     = self.btnSizeDict["small"][0]
        self.hs     = self.btnSizeDict["small"][1]
        self.wb     = self.btnSizeDict["big"][0]
        self.hb     = self.btnSizeDict["big"][1]
        
        


def getImagePath(imageName, ext="png", imageFolder="img"):
    
    imageFile       = "%s.%s"%(imageName, ext)
    relativePath    = os.path.abspath(os.path.join(FILE_PATH, os.pardir, os.pardir))
    imgPath         = os.path.abspath(os.path.join(relativePath, imageFolder, imageFile))
    
    return imgPath

def getModulePath(filePath, moduleName):
    relativePath   = os.sep.join(filePath.split(os.sep)[:-1])
    return           relativePath + os.sep + moduleName


def getModKeyPressed():
    mods = cmds.getModifiers()
    if mods == 1:
        return "shift"
    if mods == 4:
        return "ctrl"
    if mods == 8:
        return "alt"
    if mods == 5:
        return "ctrlShift"
    if mods == 9:
        return "altShift"
    if mods == 12:
        return "altCtrl"
    if mods == 13:
        return "altCtrlShift"


def clearMenuItems(menu):
    
    menuItens = cmds.popupMenu(menu, query=True, itemArray=True)

    if menuItens:
        for loopMenu in menuItens:
            if cmds.menuItem(loopMenu, query=True, exists=True): cmds.deleteUI(loopMenu)
  






