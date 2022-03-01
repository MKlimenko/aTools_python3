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
from maya import mel
import os
import shutil
import time

from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import utilMod
    
G.A_NODE              = "aTools_StoreNode"
G.USER_FOLDER       = G.USER_FOLDER or mel.eval('getenv MAYA_APP_DIR') + os.sep + "aToolsSettings"
G.UM_timerMessage   = ""  

utilMod.makeDir(G.USER_FOLDER)


def getSceneId(forceCreate=False):
    id = loadInfoWithScene("scene", "id") if not forceCreate else False
    
    if not id:
        id = time.time()
        saveInfoWithScene("scene", "id", id)
        
    return str(id)  

def saveInfoWithScene(storeNode, attr, value):
    
    with G.aToolsBar.createAToolsNode:
        cmds.undoInfo(stateWithoutFlush=False)
        currSel     = None
        if not cmds.objExists(G.A_NODE) or not cmds.objExists(storeNode): currSel     = cmds.ls(selection=True)
        if not cmds.objExists(G.A_NODE):      cmds.createNode('mute', name=G.A_NODE)
        if not cmds.objExists(storeNode):   cmds.createNode('mute', name=storeNode)
        if currSel: cmds.select(currSel)
        
        if not cmds.isConnected("%s.output"%G.A_NODE, "%s.mute"%storeNode): cmds.connectAttr("%s.output"%G.A_NODE, "%s.mute"%storeNode)
        if not cmds.objExists("%s.%s"%(storeNode, attr)): cmds.addAttr(storeNode, longName=attr, dataType="string", keyable=False)
        cmds.setAttr("%s.%s"%(storeNode, attr), value, type="string")
        cmds.undoInfo(stateWithoutFlush=True)
    
def loadInfoWithScene(storeNode, attr):    
    obj = "%s.%s"%(storeNode, attr)
    if cmds.objExists(obj): 
        return cmds.getAttr(obj)
    else:
        return None
    
   
    
def saveFileWithUser(folder, file, value, ext=None):
    filePath        = getSaveFilePath("%s%s%s"%(folder, os.sep, file), ext)
    folderPath      = utilMod.getFolderFromFile(filePath)
    
    
    if os.path.isfile(filePath):            os.remove(filePath)    
    if not os.path.isdir(folderPath):       os.makedirs(folderPath)
    
    newFileContents = "%s"%value
    
    utilMod.writeFile(filePath, newFileContents)


def deleteFileWithUser(folder, file, ext="aTools"):
    filePath        = getSaveFilePath("%s%s%s"%(folder, os.sep, file), ext)
    
    if os.path.isfile(filePath):            os.remove(filePath)   
    
def deleteFolderWithUser(folder):
    folderPath = "%s%s%s"%(G.USER_FOLDER, os.sep, folder)
    if os.path.isdir(folderPath): shutil.rmtree(folderPath) 
    
def renameFolderWithUser(oldFolder, newFolder):
    oldUserFolder = "%s%s%s"%(G.USER_FOLDER, os.sep, oldFolder)
    newUserFolder = "%s%s%s"%(G.USER_FOLDER, os.sep, newFolder)    
    if os.path.isdir(oldUserFolder): os.rename(oldUserFolder, newUserFolder)  

def loadFileWithUser(folder, file, ext="aTools"):    
    filePath    = getSaveFilePath("%s%s%s"%(folder, os.sep, file), ext)
    
    
    readFileContents = utilMod.readFile(filePath)
    
    if readFileContents != None:
        return eval(readFileContents[0])
    
    return None
    
def readFilesWithUser(folder, ext=None):
    filePath        = getSaveFilePath("%s%s%s"%(folder, os.sep, "dummy"))
    folderPath      = utilMod.getFolderFromFile(filePath)
        
    if not os.path.isdir(folderPath): return []
    
    filesInFolder   = [loopFile for loopFile in os.listdir(folderPath) if ext is None or ext is True or loopFile.endswith(".%s"%ext)]
    
    if ext is None:
        for n, loopFile in enumerate(filesInFolder):
            filesInFolder[n] = ".".join(loopFile.split(".")[:-1])
    
    return filesInFolder

def readFoldersWithUser(folder):
    folderPath = "%s%s%s"%(G.USER_FOLDER, os.sep, folder)
    
    if not os.path.isdir(folderPath): return []
    
    foldersInFolder = [loopFolder for loopFolder in os.listdir(folderPath) if os.path.isdir(folderPath) if loopFolder != ".directory"]
     
    return foldersInFolder


def saveInfoWithUser(file, attr, value, delete=False):
    filePath        = getSaveFilePath(file)
    newFileContents = []
    writeNew        = True
    
    if isinstance(value, str): value = "\"%s\""%value
    
    readFileContents = utilMod.readFile(filePath)
    
    if readFileContents != None:
        
        for loopLine in readFileContents:
            if loopLine.find(attr) == 0:
                if not delete: 
                    newFileContents.append("%s = %s\n"%(attr, value))

                writeNew = None
            else:
                if len(loopLine) > 1:
                    newFileContents.append(loopLine)
        
    if writeNew:
        if not delete: newFileContents.append("%s = %s\n"%(attr, value)) 

    
    utilMod.writeFile(filePath, newFileContents)
  

def loadInfoWithUser(file, attr):    
    filePath    = getSaveFilePath(file)
    
    readFileContents = utilMod.readFile(filePath)
    
    if readFileContents != None:
        
        for loopLine in readFileContents:
            if loopLine.find(attr) == 0:
                value = loopLine[(loopLine.find("=")+2):]
                return eval(value)
    
    return None




def getUserPref(pref, default):
    
    pref = loadInfoWithUser("userPrefs", pref)
    if pref == None: pref = default 

    return pref        

def setUserPref(pref, onOff):
    
    saveInfoWithUser("userPrefs", pref, onOff)
    
    

    
def setPref(pref, preferences, init=False, default=False):
    
    for loopPref in preferences:
        name    = loopPref["name"]
        if pref == name:
            if init: 
                onOff   = getPref(pref, preferences)
            elif default:
                onOff   = getDefPref(pref, preferences)
                cmds.menuItem("%sMenu"%name, edit=True, checkBox=onOff)
                saveInfoWithUser("userPrefs", name, "", True) 
            else:
                onOff   = cmds.menuItem("%sMenu"%name, query=True, checkBox=True)
                saveInfoWithUser("userPrefs", pref, onOff)                
            

def getPref(pref, preferences):
    r = loadInfoWithUser("userPrefs", pref)
    if r == None: 
        default = getDefPref(pref, preferences)
        r = default 
        
    return r


def getDefPref(pref, preferences):
    for loopPref in preferences:
        name    = loopPref["name"]
        if pref == name:
            default = loopPref["default"]
            return default
        
        

def getaToolsPath(level=1, inScriptsFolder=True):
    if inScriptsFolder: 
        mayaAppDir      = mel.eval('getenv MAYA_APP_DIR')
        scriptsDir      = "%s%sscripts%s"%(mayaAppDir, os.sep, os.sep)
        aToolsFolder    = "%s%saTools%s"%(scriptsDir, os.sep, os.sep)
        if level==1: return aToolsFolder
        if level==2: return scriptsDir
    return utilMod.getFolderFromFile(__file__, level)
    
    
def getSaveFilePath(saveFile, ext="aTools"):
    
    saveFilePath    = G.USER_FOLDER + os.sep + saveFile
    if ext:         saveFilePath += ".%s"%ext
    
    return saveFilePath
  