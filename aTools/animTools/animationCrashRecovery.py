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
from maya import OpenMaya
from maya import OpenMayaAnim
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod
from aTools.commonMods import aToolsMod

import os
import time
import datetime
import math



class AnimationCrashRecovery(object): 
    
    def __init__(self):
        
        
        G.animationCrashRecovery    = self
        
        self.deferredQueue          = []
        self.animCurvesNames        = []
        self.animCurvesInfo         = {}
        self.nonKeyedAttrInfo       = {}
        self.baseFolderName         = "animationCrashRecovery"  
        self.baseLatestFolderName   = "latest"
        self.baseBackupFolderName   = "backup"
        self.infoDataFileName       = "infoData"
        self.selectedObjs           = []  
        self.ignoreAttrs            = ["visibility"]  
        self.curveExt               = "curve"  
        self.attrExt                = "attr"  
        self.curvesInFile           = []
        self.nonKeyedAttrsInFile    = []
        self.mayaFileName           = None    
        self.pause                  = False
        self.mayaFileName           = utilMod.getMayaFileName()
        self.mayaFilePath           = utilMod.getMayaFileName("path")
        G.ACR_messages              = G.ACR_messages or {"anim":[], "node":[], "scene":[], "mdg":[]}
        self.blinkingLedState       = False
        self.saveRecommended        = True
        self.checkNodeCreated       = True
        G.lastSaveWarning           = G.lastSaveWarning or None
        self.redBlinkingSecs        = 300#300 = 5 minutes
        self.daysToKeepOldFiles     = 5*86400#5days
        self.nodesCreated           = []
        #self.daysToKeepOldFiles     = 10#TMP
        
        self.checkForCrashLog()
        self.checkAndClearOldFiles()
        
        #G.deferredManager.removeFromQueue("ACR")#TMP

    def switch(self, onOff):
        
        
        self.removeMessages() 
        utilMod.killScriptJobs("G.animationCrashRecoveryScriptJobs")  
                
        if onOff:

            #self.saveAllAnimationData(update=True)
            self.addAnimSceneMessages()
            self.addNodeMessages()  
            self.addMdgMessages()            
            G.animationCrashRecoveryScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('SelectionChanged', self.addNodeMessages )))
            
            
            self.recommendSaving(True)
            #self.recommendSaving(False)#TMP
            
        else:
            G.deferredManager.removeFromQueue("ACR")
            self.setLed("off")
    
    def setLed(self, state):
        
        if not cmds.image("animationCrashRecoveryLed", query=True, exists=True): return
        
        self.blinkingRed(False)
        
        if state == "on":
            if self.saveRecommended:    
                image               = "ACR_red"
                ann                 = "Animation Crash Recovery recommends you to save"
                G.lastSaveWarning   = time.time() if not G.lastSaveWarning else G.lastSaveWarning
                
                if time.time() - G.lastSaveWarning >= self.redBlinkingSecs: self.blinkingRed(True)
                    
            else:                       
                image               = "ACR_green"
                ann                 = "Animation Crash Recovery is ON"
                G.lastSaveWarning   = None
            
            cmds.image("animationCrashRecoveryLed", edit=True, image= uiMod.getImagePath(image), ann=ann) 
            
        elif state == "off":
            cmds.image("animationCrashRecoveryLed", edit=True, image= uiMod.getImagePath("ACR_off"), ann="Animation Crash Recovery is OFF") 

        elif state == "blinking":
            self.blinkingLedState = not self.blinkingLedState
            image = "ACR_white_half" if self.blinkingLedState else "ACR_white_bright"
            cmds.image("animationCrashRecoveryLed", edit=True, image= uiMod.getImagePath(image), ann="Animation Crash Recovery is saving animation") 
            
        elif state == "blinking_red":
            self.blinkingLedState = not self.blinkingLedState
            image = "ACR_red_half" if self.blinkingLedState else "ACR_red_bright"
            cmds.image("animationCrashRecoveryLed", edit=True, image= uiMod.getImagePath(image), ann="Animation Crash Recovery HIGHLY recommends you to save") 

            
             
    def blinkingRed(self, onOff):
        
        if onOff:   G.aToolsBar.timeoutInterval.setInterval(self.toggleRed, .3, id="ACR_red_blinking")
        else:       G.aToolsBar.timeoutInterval.stopInterval("ACR_red_blinking")
        

    def toggleRed(self):
        self.setLed("blinking_red")

        
    
    def optionBoxWindow(self, *args):
        
        sceneId         = aToolsMod.getSceneId()
        idFolder        = "%s%s%s"%(self.baseFolderName, os.sep, sceneId)    
        bkpFolder       = "%s%s%s"%(idFolder, os.sep, self.baseBackupFolderName)         
        infoData        = aToolsMod.loadFileWithUser(bkpFolder, self.infoDataFileName, ext="info")
        infoDataFile    = "%s%s%s%s%s.info"%(G.USER_FOLDER, os.sep, bkpFolder, os.sep, self.infoDataFileName)
        modDate         = os.path.getmtime(infoDataFile) if os.path.isfile(infoDataFile) else None
        
        
        if not infoData or not modDate: 
            cmds.warning("There is no crash file to restore.")
            return
        
        
        def loadWindow():
            
            mayaFileName    = infoData["mayaFileName"]
            message         = "%s\n%s\n\nWarning: Loading crash files after editing your Maya file can lead to unpredictable results."%(mayaFileName, time.ctime(modDate))
            
            formLayout      = cmds.setParent(query=True)        
            icon            = cmds.image(image= uiMod.getImagePath("ACR_white_bright")) 
            titleText       = cmds.text(label="Do you want to load?", font="boldLabelFont", align="left")  
            messageText     = cmds.text(label=message, align="left")
            buttonLoad      = cmds.button(label='Load', command='cmds.layoutDialog(dismiss="load")')
            buttonLoadSel   = cmds.button(label='Load On Selection', command='cmds.layoutDialog(dismiss="load_selection")', w=110)
           
            cmds.formLayout (formLayout, edit=True, width=300, height=170,
                            attachPosition   = [
                                             (icon, 'left', 10, 0), 
                                             (icon, 'top', 10, 0),  
                                             (titleText, 'top', 10, 0), 
                                             (messageText, 'left', 10, 0), 
                                             (messageText, 'top', 0, 30),
                                             (buttonLoad, 'left', 10, 0),
                                             (buttonLoad, 'bottom', 10, 100),
                                             (buttonLoadSel, 'bottom', 10, 100)
                                             ],
                            attachForm       = [
                                             (buttonLoad, 'left', 10),
                                             (buttonLoadSel, 'right', 10)
                                             ],
                            attachControl    = [
                                             (titleText, 'left', 10, icon),
                                             (buttonLoad, 'right', 5, buttonLoadSel)
                                             ])

            
        def window(dismiss):
         
            if dismiss == "dismiss": return

            onlySelectedNodes   = True if dismiss == "load_selection" else False
            
            self.loadData(onlySelectedNodes, self.baseBackupFolderName)  
                         
        
        window(cmds.layoutDialog(title="aTools Animation Crash Recovery", ui=loadWindow)) 
        
        
               
      

                    
    def checkForAnimationSaved(self, clearDeferredQueue=False, *args):
        if clearDeferredQueue: self.deferredQueue      = []
        
        sceneId         = aToolsMod.getSceneId()
        idFolder        = "%s%s%s"%(self.baseFolderName, os.sep,  sceneId)
        latestFolder    = "%s%s%s"%(idFolder, os.sep, self.baseLatestFolderName)  
        infoFile        = "%s%s%s%s%s.info"%(G.USER_FOLDER, os.sep, latestFolder, os.sep, self.infoDataFileName)
        mayaFile        = cmds.file(query=True, sceneName=True)
        
        if not os.path.isfile(infoFile) or not os.path.isfile(mayaFile): return
        
        mayaFileModTime = os.path.getmtime(mayaFile) 
        infoFileModTime = os.path.getmtime(infoFile)
        
        if mayaFileModTime < infoFileModTime:   
            
            infoData    = aToolsMod.loadFileWithUser(latestFolder, self.infoDataFileName, ext="info")
            
            if not infoData: return
            
            height              = 170
            completed           = infoData["completed"]
            mayaFileModTimeStr  = time.ctime(mayaFileModTime)
            infoFileModTimeStr  = time.ctime(infoFileModTime)            
            message             = "This Maya file:\n%s\n\n"%(mayaFileModTimeStr)
            message             += "Latest Animation Crash Recovery file:\n%s"%(infoFileModTimeStr)
            
            if not completed:   
                message += "\n\n*Some animation may not be loaded.\nAnimation Crash Recovery did not finish saving before Maya crashed."
                height  += 40
                
            self.warningForLoading(message, height)
        
        
        
               

    def warningForLoading(self, message, height):
        
        def warningWindow():
        
            formLayout      = cmds.setParent(query=True)        
            icon            = cmds.image(image= uiMod.getImagePath("ACR_white_bright")) 
            titleText       = cmds.text(label="You have newer animation. Do you want to load?", font="boldLabelFont", align="left")
            messageText     = cmds.text(label=message, align="left")
            buttonLoad      = cmds.button(label='Load', command='cmds.layoutDialog(dismiss="load")')
            buttonMaybe     = cmds.button(label='Maybe Later', command='cmds.layoutDialog(dismiss="maybe")', w=100)
            
          
            cmds.formLayout (formLayout, edit=True, width=300, height=height,
                            attachPosition   = [
                                             (icon, 'left', 10, 0), 
                                             (icon, 'top', 10, 0),  
                                             (titleText, 'top', 10, 0), 
                                             (messageText, 'left', 10, 0), 
                                             (messageText, 'top', 0, 30),
                                             (buttonLoad, 'left', 10, 0),
                                             (buttonLoad, 'bottom', 10, 100),
                                             (buttonMaybe, 'bottom', 10, 100)
                                             ],
                            attachForm       = [
                                             (buttonLoad, 'left', 10),
                                             (buttonMaybe, 'right', 10)
                                             ],
                            attachControl    = [
                                             (titleText, 'left', 10, icon),
                                             (buttonLoad, 'right', 5, buttonMaybe)
                                             ])
            
            
            
        def window(dismiss):
            if dismiss == "load":                 
                self.loadData()
            else:                 
                cmds.warning("If you want to load later, go to aTools menu/Animation Crash Recovery option box")
            
            self.saveBackup()           
        
        window(cmds.layoutDialog(title="aTools Animation Crash Recovery", ui=warningWindow)) 
               
        
    def saveBackup(self):            
        
        sceneId         = aToolsMod.getSceneId()
        idFolder        = "%s%s%s"%(self.baseFolderName, os.sep,  sceneId)
        latestFolder    = "%s%s%s"%(idFolder, os.sep, self.baseLatestFolderName)     
        bkpFolder       = "%s%s%s"%(idFolder, os.sep, self.baseBackupFolderName)  
                
        aToolsMod.deleteFolderWithUser(bkpFolder)
        aToolsMod.renameFolderWithUser(latestFolder, bkpFolder)
        aToolsMod.deleteFolderWithUser(latestFolder)
        
                
    def getSavedData(self, crashFolder=None, onlySelectedNodes=False, *args):
        
        idFolder                = aToolsMod.getSceneId()
        crashFolder             = self.baseLatestFolderName if not crashFolder else crashFolder
        folder                  = "%s%s%s%s%s"%(self.baseFolderName, os.sep,  idFolder, os.sep, crashFolder)
        filePath                = cmds.file(query=True, sceneName=True)
        fileModTime             = None
        
        
        if os.path.isfile(filePath):
            fileModTime             = os.path.getmtime(filePath) 
        
        curveFiles              = aToolsMod.readFilesWithUser(folder, ext=self.curveExt)
        attrFiles               = aToolsMod.readFilesWithUser(folder, ext=self.attrExt)

        status          = "aTools Animation Crash Recovery - Step 1/3 - Loading crash files..."
        utilMod.startProgressBar(status)
        totalSteps      = len(curveFiles + attrFiles)           
        firstStep       = 0
        thisStep        = 0
        estimatedTime   = None
        startChrono     = None
        progressInfo    = [startChrono, firstStep, thisStep, totalSteps, estimatedTime, status]
          
        data            = self.getDataFromFiles("anim", folder, curveFiles, fileModTime, self.curveExt, progressInfo, onlySelectedNodes)
        
        if not data: return
        
        animData        = data[0]
        progressInfo    = data[1]        
        data            = self.getDataFromFiles("attr", folder, attrFiles, fileModTime, self.attrExt, progressInfo, onlySelectedNodes)
        attrData        = data[0]
        
        if not data: return
        
        utilMod.setProgressBar(endProgress=True)
        
        return {"fileModTime":fileModTime, "animData":animData, "attrData":attrData}
    

        
    def getDataFromFiles(self, animAttr, folder, infoFiles, fileModTime, ext, progressInfo, onlySelectedNodes):
        currSel             = animMod.getObjsSel()
        data                = {"data":[], "modTime":None}
        infoFileModTimeList = []
        startChrono, firstStep, thisStep, totalSteps, estimatedTime, status = progressInfo
        initialStep         = thisStep
        
        for n, loopFile in enumerate(infoFiles): 
            if cmds.progressBar(G.progBar, query=True, isCancelled=True ):  
                utilMod.setProgressBar(endProgress=True)
                return
            
            thisStep        = n+initialStep
            startChrono     = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)  
                      
            infoFileStr     = loopFile.replace(":", "_aTools_")[0:-(len(ext)+1)]
            infoFilePath    = aToolsMod.getSaveFilePath("%s%s%s"%(folder, os.sep, infoFileStr), ext=ext)
            infoFileModTimeList.append(os.path.getmtime(infoFilePath))
            
            if infoFileModTimeList[-1] > fileModTime: #load only what is newer
                object          = loopFile.replace("_aTools_", ":")[0:-(len(ext)+1)]
                value           = aToolsMod.loadFileWithUser(folder, infoFileStr, ext=ext)
            
                if onlySelectedNodes:
                    if animAttr == "anim":
                        obj = value["objects"][0]
                    else:  
                        obj = object.split(".")[0]

                    if obj not in currSel: continue           
            
            
                data["data"].append({"_modTime":infoFileModTimeList[-1],"object":object, "value":value})
            
            estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
            
        #file mod date
        data["data"].sort() #sort newer files last
        if len(infoFileModTimeList) > 0:
            data["modTime"] = max(infoFileModTimeList)
        
        progressInfo = [startChrono, firstStep, thisStep, totalSteps, estimatedTime, status]
        #blend animation data=================
        
        return [data, progressInfo]
        
    def loadData(self, onlySelectedNodes=False, crashFolder=None, *args):  
        
        cmds.waitCursor(state=True)
        cmds.refresh(suspend=True)
        cmds.undoInfo(openChunk=True)
        utilMod.startProgressBar("aTools Animation Crash Recovery - Loading data...")                
        
        self.pause      = True
        savedData       = self.getSavedData(crashFolder, onlySelectedNodes)
                
        if savedData:
        
            animData    = savedData["animData"]["data"]
            attrData    = savedData["attrData"]["data"] 
        
            self.applyAttrData(attrData)
            self.applyAnimData(animData)
            if not crashFolder: self.loadInfoData()
        
        utilMod.setProgressBar(endProgress=True)
        
        self.pause = False
        
        cmds.undoInfo(closeChunk=True)
        cmds.refresh(suspend=False)    
        cmds.waitCursor(state=False)

    def blendAnimData(self, acrAnimData):
    
        blendedAnimData = {"objects":[], "animData":[]} 
        
        for loopData in acrAnimData:
            data        = loopData["value"]
            objects     = data["objects"]
            animData    = data["animData"]
            
            blendedAnimData["objects"].extend(objects)
            blendedAnimData["animData"].extend(animData)
            
        return blendedAnimData

    def applyAnimData(self, animData):
        
        if len(animData) == 0 : return
        animData = self.blendAnimData(animData)  
        animMod.applyAnimData(animData, pasteInPlace=False, showProgress=True, status="aTools Animation Crash Recovery - Step 3/3 - Applying animation data...")

            
        
    def applyAttrData(self, attrData):
        
        firstStep       = 0
        totalSteps      = len(attrData)
        estimatedTime   = None
        status          = "aTools Animation Crash Recovery - Step 2/3 - Applying attributes data..."
        startChrono     = None
                        
        for thisStep, loopData in enumerate(attrData):
            if cmds.progressBar(G.progBar, query=True, isCancelled=True ):  return
            startChrono = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)

            objAttr = loopData["object"]
            value   = loopData["value"]["value"]
            
            if not cmds.objExists(objAttr):                     continue            
            if not cmds.getAttr(objAttr, settable=True):        continue 
            if cmds.getAttr(objAttr, lock=True):                continue 
            if cmds.getAttr(objAttr, type=True) == "string":    continue
            
            cmds.cutKey(objAttr)
            
            
            if type(value) is list: #translate, rotate, scale
                value = value[0]
                cmds.setAttr(objAttr, value[0],value[1],value[2], clamp=True)
            else: #translatex, translatey, etc           
                cmds.setAttr(objAttr, value, clamp=True)
            
            
            estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
            
    
    def getAllAnimCurves(self):        
        return cmds.ls(type=["animCurveTA","animCurveTL","animCurveTT","animCurveTU"])
    
    def getAllNonKeyedAttrs(self):
        return self.getNonKeyedAttrs(cmds.ls(transforms=True, visible=True))
        #return self.getNonKeyedAttrs([loopObj for loopObj in cmds.ls() if "transform" in cmds.nodeType(loopObj, inherited=True)])
   
     
    def saveSelectedCurve(self, *args):    

        if self.pause: return   
        
        curveMsg = args[0]
        curves  = [OpenMaya.MFnDependencyNode(curveMsg[n]).name() for n in xrange(curveMsg.length())]
        
        
        function = lambda *args:self.sendDataToSaveDeferred(curves, [])
        G.deferredManager.sendToQueue(function, 50, "ACR")
        
        
                
            
    def saveSelectedAttr(self, msg, mplug, otherMplug, clientData):         
        
        if self.pause: return   
        
        if OpenMaya.MNodeMessage.kAttributeSet == (OpenMaya.MNodeMessage.kAttributeSet & msg):
            #nodeName, attrName = mplug.name().split('.')        
            nonKeyedAttr = mplug.name()
            
            #if cmds.keyframe(nonKeyedAttr,  query=True): return
            
            function = lambda *args:self.sendDataToSaveDeferred([], [nonKeyedAttr])
            G.deferredManager.sendToQueue(function, 50, "ACR")
            
                
    
    
        
    def getNonKeyedAttrs(self, animObjects):
        objAttrs            = animMod.getAllChannels(animObjects, changed=True, withAnimation=False)
        nonKeyedObjAttrs    = []
       
        
        for n, loopObj in enumerate(animObjects): 
            loopObjAttrs = objAttrs[n]
            if not loopObjAttrs: continue
            for loopAttr in loopObjAttrs:
                if loopAttr in self.ignoreAttrs: continue
                objAttr = "%s.%s"%(loopObj, loopAttr)
                if not cmds.objExists(objAttr): continue
                frameCount = cmds.keyframe(objAttr, query=True, keyframeCount=True)
                if frameCount <= 0:
                    nonKeyedObjAttrs.append(objAttr)
                    
        return nonKeyedObjAttrs
    
    def saveAllAnimationData(self, update=False, *args):#nao precisa???
        #print "saveAllAnimationData"
        if update:
            self.curvesInFile          = self.getAllAnimCurves()
            self.nonKeyedAttrsInFile   = self.getAllNonKeyedAttrs()
                
        self.sendDataToSaveDeferred(self.curvesInFile, self.nonKeyedAttrsInFile)
        
    def sendDataToSaveDeferred(self, curves, nonKeyedAttrs):
                
        if not len(curves) > 0 and not len(nonKeyedAttrs) > 0: 
            return
        
        for loopCurve in curves:
            
            curveStr            = loopCurve.replace(":", "_aTools_")
            if not cmds.objExists(loopCurve): 
                if curveStr in self.deferredQueue: self.deferredQueue.remove(curveStr)
                continue
            
            if curveStr in self.deferredQueue: continue
                  
            self.deferredQueue.append(curveStr)
            function            = lambda function=self.saveCurve, mayaFileName=self.mayaFileName, attrStr=curveStr, *args: self.sendToDeferredManager(function, mayaFileName, attrStr)
            G.deferredManager.sendToQueue(function, 50, "ACR")
        
            
        for loopNonKeyedAttr in nonKeyedAttrs:
            
            nonKeyedAttrsStr    = loopNonKeyedAttr.replace(":", "_aTools_")
            
            if not cmds.objExists(loopNonKeyedAttr): 
                if nonKeyedAttrsStr in self.deferredQueue: self.deferredQueue.remove(nonKeyedAttrsStr)
                continue
            
            if cmds.keyframe(loopNonKeyedAttr,  query=True): continue 
            
            if nonKeyedAttrsStr in self.deferredQueue: continue
                  
            self.deferredQueue.append(nonKeyedAttrsStr)
            function            = lambda function=self.saveNonKeyedAttrs, mayaFileName=self.mayaFileName, attrStr=nonKeyedAttrsStr, *args: self.sendToDeferredManager(function, mayaFileName, attrStr)
            G.deferredManager.sendToQueue(function, 50, "ACR")
            
        
        G.deferredManager.sendToQueue(lambda *args:self.stopBlinking(self.mayaFileName), 50, "ACR")
    
    def stopBlinking(self, mayaFileName):    
        if G.deferredManager.inQueue("ACR") <= 1: 
            self.setLed("on")
            self.saveInfoData(mayaFileName, completed=True)
            self.checkDeletedNodesCreated()
            
    
    def checkDeletedNodesCreated(self):
        
        if len(G.ACR_messages["mdg"]) == 0: return
        
        toRemove = []
        
        for loopNode in self.nodesCreated:
            if not cmds.objExists(loopNode): toRemove.append(loopNode)
            
        for loopNode in toRemove: self.nodesCreated.remove(loopNode)        
        if len(self.nodesCreated) == 0: self.recommendSaving(False)
        
    
    def sendToDeferredManager(self, function, mayaFileName, attrStr):
        function(mayaFileName, attrStr)
        
    def saveCurve(self, mayaFileName, curveStr):
        self.setLed("blinking")
        
        sceneId  = aToolsMod.getSceneId()
        curve    = curveStr.replace("_aTools_", ":")
        animData = animMod.getAnimData([curve])               

        if curveStr in self.deferredQueue: self.deferredQueue.remove(curveStr)
        
        if animData is None: return
        
        if not self.animCurvesInfo.has_key(sceneId): self.animCurvesInfo[sceneId] = {}
        
        if self.animCurvesInfo[sceneId].has_key(curveStr):
            if self.animCurvesInfo[sceneId][curveStr] == animData: return
        
        self.animCurvesInfo[sceneId][curveStr] = animData                

        #save curve to disk
        aToolsMod.saveFileWithUser("%s%s%s%s%s"%(self.baseFolderName, os.sep, sceneId, os.sep, self.baseLatestFolderName), curveStr, animData, ext=self.curveExt)
        self.saveInfoData(mayaFileName)

        
    def saveInfoData(self, mayaFileName, completed=False):
        
        sceneId     = aToolsMod.getSceneId()
        currFrame   = cmds.currentTime(query=True)
        currSel     = cmds.ls(selection=True)
        infoData    = {"mayaFileName":mayaFileName, "currFrame":currFrame, "currSel":currSel, "completed":completed}
        
        aToolsMod.saveFileWithUser("%s%s%s%s%s"%(self.baseFolderName, os.sep, sceneId, os.sep, self.baseLatestFolderName), self.infoDataFileName, infoData, ext="info")
        
    def loadInfoData(self):
        sceneId     = aToolsMod.getSceneId()
        infoData    = aToolsMod.loadFileWithUser("%s%s%s%s%s"%(self.baseFolderName, os.sep,  sceneId, os.sep, self.baseLatestFolderName), self.infoDataFileName, ext="info")
        
        if not infoData: return
        
        currFrame   = infoData["currFrame"]
        currSel     = infoData["currSel"]
                
        if currFrame:           cmds.currentTime(currFrame)
        if len(currSel) > 0:    cmds.select(currSel, replace=True)
    
    def saveNonKeyedAttrs(self, mayaFileName, nonKeyedAttrsStr):
        self.setLed("blinking")      
        
        sceneId         = aToolsMod.getSceneId()
        nonKeyedAttr    = nonKeyedAttrsStr.replace("_aTools_", ":")
        attrData        = self.getNonKeyedAttrData(nonKeyedAttr)
        
        if nonKeyedAttrsStr in self.deferredQueue: self.deferredQueue.remove(nonKeyedAttrsStr)
        
        if attrData is None: return
        
        if not self.nonKeyedAttrInfo.has_key(sceneId): self.nonKeyedAttrInfo[sceneId] = {}
        
        if self.nonKeyedAttrInfo[sceneId].has_key(nonKeyedAttrsStr):
            if self.nonKeyedAttrInfo[sceneId][nonKeyedAttrsStr] == attrData: return
        
        self.nonKeyedAttrInfo[sceneId][nonKeyedAttrsStr]   = attrData      
        
        #save curve to disk
        aToolsMod.saveFileWithUser("%s%s%s%s%s"%(self.baseFolderName, os.sep, sceneId, os.sep, self.baseLatestFolderName), nonKeyedAttrsStr, attrData, ext=self.attrExt)
        self.saveInfoData(mayaFileName)
    
    
    def checkAndClearOldFiles(self):

        allIdFolders    = aToolsMod.readFoldersWithUser(self.baseFolderName)
        timeNow         = time.time() 
        
        for loopIdFolder in allIdFolders:
            idFolder        = "%s%s%s"%(self.baseFolderName, os.sep, loopIdFolder)
            modDate         = None
            
            for loopInfoFile in [self.baseLatestFolderName, self.baseBackupFolderName]:            
                infoDataFile    = "%s%s%s%s%s%s%s.info"%(G.USER_FOLDER, os.sep, idFolder, os.sep, loopInfoFile, os.sep, self.infoDataFileName)
                if os.path.isfile(infoDataFile):
                    modDate         = os.path.getmtime(infoDataFile)
                    break
                           
            if not modDate: return
            
            if timeNow - modDate >= self.daysToKeepOldFiles:          
                aToolsMod.deleteFolderWithUser(idFolder)
           
            
        
        
    
    def clearLatestFolder(self):
        self.deferredQueue      = []
        G.deferredManager.removeFromQueue("ACR")
        
        sceneId         = aToolsMod.getSceneId()
        idFolder        = "%s%s%s"%(self.baseFolderName, os.sep,  sceneId)
        latestFolder    = "%s%s%s"%(idFolder, os.sep, self.baseLatestFolderName) 
        
        aToolsMod.deleteFolderWithUser(latestFolder)
    
    
    
    def getNonKeyedAttrData(self, nonKeyedAttr):        
        value = None
        
        if cmds.objExists(nonKeyedAttr): value = cmds.getAttr(nonKeyedAttr)
        return {"value":value}  
    
    
    def recommendSaving(self, trueFalse):
        self.saveRecommended    = trueFalse
    
        if not trueFalse:       self.addMdgMessages()
        self.setLed("on") 
        
    def isCrashSaving(self):
        t                   = datetime.date.today()
        todaySt             = ".%s%s%s."%(str(t.year).zfill(4),str(t.month).zfill(2),str(t.day).zfill(2))
          
        return (todaySt in utilMod.getMayaFileName())
    
    def beforeSave(self, *args):
        pass
        
    def afterSave(self, *args):
        
        if self.isCrashSaving():    
            self.saveCrashLog(cmds.file(query=True, sceneName=True), self.mayaFilePath, self.mayaFileName)
            return                   
            
        self.mayaFileName       = utilMod.getMayaFileName()  
        self.mayaFilePath       = utilMod.getMayaFileName("path")
              
        self.recommendSaving(False)
        self.addMdgMessages()
        self.clearLatestFolder()
        
    def afterNew(self, *args):
        #print "afterOpen"
        self.mayaFileName       = utilMod.getMayaFileName()
        self.mayaFilePath       = utilMod.getMayaFileName("path")

        self.recommendSaving(False)
        
    def beforeOpen(self, *args):
        self.pause = True
        
    def afterOpen(self, *args):
        self.pause = False
        #print "afterOpen"
        self.mayaFileName       = utilMod.getMayaFileName()
        self.mayaFilePath       = utilMod.getMayaFileName("path")

        self.recommendSaving(False)
        
        function = lambda *args: self.checkForAnimationSaved(clearDeferredQueue=True)
        G.deferredManager.sendToQueue(function, 80, "ACR")
        #self.checkForAnimationSaved(clearDeferredQueue=True)
    
    def checkForCrashLog(self):
        
        crashLog        = self.loadCrashLog()

        if crashLog and crashLog.has_key("crashFilePath"):    self.warnCrashLog(crashLog)
    
    def saveCrashLog(self, crashFilePath, beforeCrashPath, beforeCrashName):
        
        crashData   = {"crashFilePath":crashFilePath, "beforeCrashPath":beforeCrashPath, "beforeCrashName":beforeCrashName}
        aToolsMod.saveFileWithUser("%s"%(self.baseFolderName), "crashLog", crashData, ext="info")
        
    def loadCrashLog(self):        
        
        return aToolsMod.loadFileWithUser("%s"%(self.baseFolderName), "crashLog", ext="info")
    
    def warnCrashLog(self, crashLog):
        
        crashFilePath       = crashLog["crashFilePath"]
        beforeCrashPath     = crashLog["beforeCrashPath"]
        beforeCrashName     = crashLog["beforeCrashName"]
        
        if not os.path.isfile(crashFilePath) or not os.path.isfile(beforeCrashPath): return
        
        crashFileModTime    = time.ctime(os.path.getmtime(crashFilePath)) 
        beforeCrashModTime  = time.ctime(os.path.getmtime(beforeCrashPath))
        message             = "Looks like last Maya session crashed and saved a crash file.\n\nOriginal file:\n%s\n%s\n\nCrash saved file:\n%s\n%s\n\nDo you want to open the crash saved file?"%(beforeCrashName, beforeCrashModTime, crashFilePath, crashFileModTime)
        confirm             = cmds.confirmDialog( title='aTools Animation Crash Recovery', message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

        if confirm == 'Yes':
            if cmds.file(query=True, sceneName=True):
                message         = "Save current file first? If you click NO, changes will be lost."
                confirm         = cmds.confirmDialog( title='aTools Animation Crash Recovery', message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            
                if confirm == 'Yes': cmds.file(save=True)
                
            cmds.file(new=True, force=True)
            cmds.file(crashFilePath, open=True, prompt=True)
        
        aToolsMod.deleteFileWithUser("%s"%(self.baseFolderName), "crashLog", ext="info")
        
            
    
    
    """
    def sceneUpdate(self, *args):
        self.clearOldFiles()
        self.mayaFileName  = utilMod.getMayaFileName()
        #print "sceneUpdate", args, self.mayaFileName
        
    
    def beforeSaveCheck(self, retCode, *args):
        self.clearOldFiles()
        OpenMaya.MScriptUtil.setBool(retCode, True)
        
        print "beforeSaveCheck", args, self.mayaFileName
    """
    
    
    
    def afterNodeCreated(self, *args):
        
        if not self.checkNodeCreated: return
        
        nodeCreated = OpenMaya.MFnDependencyNode(args[0]).name()
        nodeType    = cmds.nodeType(nodeCreated)        
                
        if nodeType in ["animCurveTA","animCurveTL","animCurveTT","animCurveTU"]:
            return
        
        print "nodeCreated", nodeCreated, nodeType
        
        if nodeCreated not in self.nodesCreated: self.nodesCreated.append(nodeCreated)
        
        self.recommendSaving(True)
        #self.removeMdgMessages()
        
    def afterNodeParent(self, *args): 
        
        if not self.checkNodeCreated: return
        
        dag         = args[0]         
        firstObj    = dag.partialPathName()
        
        #print "firstObj",firstObj
        if not firstObj: return
        
        dag         = args[1]         
        secondObj   = dag.partialPathName()
        
        #print "secondObj",secondObj
        if not firstObj: return
        
        #if firstObj not in self.nodesCreated: self.nodesCreated.append(firstObj)
        
        print "parented", firstObj, secondObj
         
        self.recommendSaving(True)
        self.removeMdgMessages()  
    
    def addAnimSceneMessages(self):
        
        self.removeMessages()        
        
        #ANIM MESSAGES
        G.ACR_messages["anim"].append(OpenMayaAnim.MAnimMessage.addAnimCurveEditedCallback(self.saveSelectedCurve))
        
        #SCENE MESSAGES
        G.ACR_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kBeforeSave, self.beforeSave))
        G.ACR_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kAfterSave, self.afterSave))
        G.ACR_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kBeforeOpen, self.beforeOpen))
        G.ACR_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kAfterOpen, self.afterOpen))
        G.ACR_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kAfterNew, self.afterNew))
        #G.ACR_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kSceneUpdate, self.sceneUpdate))
        #G.ACR_messages["scene"].append(OpenMaya.MSceneMessage.addCheckCallback( OpenMaya.MSceneMessage.kBeforeSaveCheck, self.beforeSaveCheck))
        
       
    
    def addMdgMessages(self):
        self.removeMdgMessages()   
        #MDG MESSAGES        
        G.ACR_messages["mdg"].append(OpenMaya.MDGMessage.addNodeAddedCallback(self.afterNodeCreated))
        G.ACR_messages["mdg"].append(OpenMaya.MDagMessage.addParentAddedCallback(self.afterNodeParent, "_noData_"))
        
        
    def addNodeMessages(self):
        self.removeNodeMessages() 
        #NODE MESSAGES
        currSel             = cmds.ls(selection=True)
        MSelectionList      = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)        
        node                = OpenMaya.MObject() 
        
        for n, loopSel in enumerate(currSel):           
                   
            MSelectionList.getDependNode(n, node)
            G.ACR_messages["node"].append(OpenMaya.MNodeMessage.addAttributeChangedCallback(node, self.saveSelectedAttr, None))     
    
    
    
        
    def removeMessages(self):  
        
        try:
            for loopId in G.ACR_messages["anim"]:
                OpenMayaAnim.MAnimMessage.removeCallback(loopId)
        except: pass   
        
        self.removeNodeMessages()
        
        try:
            for loopId in G.ACR_messages["scene"]:
                OpenMaya.MSceneMessage.removeCallback(loopId)
        except: pass
           
        self.removeMdgMessages()
        
        G.ACR_messages["anim"]  = []        
        G.ACR_messages["scene"] = []  
    
    def removeMdgMessages(self):
        
        try:
            for loopId in G.ACR_messages["mdg"]:
                OpenMaya.MDGMessage.removeCallback(loopId)
        except: pass          
           
        G.ACR_messages["mdg"] = []

    def removeNodeMessages(self):
        try:
            for loopId in G.ACR_messages["node"]:
                OpenMaya.MNodeMessage.removeCallback(loopId)
        except: pass  
        
        G.ACR_messages["node"]  = [] 

   
"""
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

def undoTest(*args):
    print 'Checking Undo callback'
    

def undoRedoCallback(arg):
    global callbackIDs
    
    Null = om.MObject()
    objs = cmds.ls(sl=1)
    
    if arg == 'add':
        
        undoID = oma.MAnimMessage.addAnimCurveEditedCallback(undoTest)
        #undoID = oma.MAnimMessage.addAnimKeyframeEditedCallback(undoTest)
        #undoID = oma.MAnimMessage.addNodeAnimKeyframeEditedCallback(undoTest)
        #undoID = oma.MAnimMessage.addAnimKeyframeEditCheckCallback(undoTest)
        #undoID = oma.MAnimMessage.addAnimKeyframeEditedCallback(undoTest)
        
        
        callbackIDs = [undoID]
    
    elif arg == 'remove':
        try:
            for i in callbackIDs:
                oma.MAnimMessage.removeCallback(i)
        except:
            print 'There is no ID to delete'


undoRedoCallback("add")
undoRedoCallback("remove")

MNodeMessage.addAttributeChangedCallback

"""
    
