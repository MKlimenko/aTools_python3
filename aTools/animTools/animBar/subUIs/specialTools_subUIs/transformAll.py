'''
========================================================================================================================
Author: Alan Camilo
www.alancamilo.com
Modified: Michael Klimenko

Requirements: aTools Package

------------------------------------------------------------------------------------------------------------------------
To install aTools, please follow the instructions in the file how_to_install.txt

------------------------------------------------------------------------------------------------------------------------
To unistall aTools, go to menu (the last button on the right), Uninstall

========================================================================================================================
''' 

from maya import cmds
from maya import mel
from maya import OpenMaya
from maya import OpenMayaAnim
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod

   
class TransformAll(object):    
    
    utilMod.killScriptJobs("G.transformAllScriptJobs")
        
    def __init__(self):
        
        G.deferredManager.removeFromQueue("transformAll")  
        G.deferredManager.removeFromQueue("TA_blinking")  
        
        if G.aToolsBar.transformAll: return
        G.aToolsBar.transformAll = self
        
        self.currentValues      = {}
        self.allValues          = {}
        self.range              = None
        self.onOff              = False
        self.blendRangeMode     = False
        self.blendImg           = ""
        G.TA_messages           = G.TA_messages or {"anim":[], "node":[], "scene":[]}
        
        self.killJobs()
        
    def blinkingButton(self, onOff):
        
        if onOff:   G.aToolsBar.timeoutInterval.setInterval(self.toggleButtonActive, .3, id="TA_blinking")
        else:       G.aToolsBar.timeoutInterval.stopInterval("TA_blinking")
        

    def toggleButtonActive(self):
        onOff = "active" in cmds.iconTextButton("transformAllBtn", query=True, image=True)

        self.setButtonImg(not onOff)

    def popupMenu(self, *args):    
        
        cmds.popupMenu              ()
        cmds.menuItem               ("blendRangeModeMenu", label="Blend Range Mode", checkBox=self.blendRangeMode, command=self.setBlendRangeMode)
        
    def setBlendRangeMode(self, *args):
        self.blendRangeMode = args[0]
        if self.blendRangeMode: self.blendImg       = "_blend"
        else:                   self.blendImg       = ""
        
        self.setButtonImg(self.onOff)
        self.warn()
        
    def setButtonImg(self, onOff):
        if onOff:
            cmds.iconTextButton("transformAllBtn", edit=True, image=uiMod.getImagePath("specialTools_transform_all%s_active"%self.blendImg), highlightImage= uiMod.getImagePath("specialTools_transform_all%s_active"%self.blendImg))
        else:
            cmds.iconTextButton("transformAllBtn", edit=True, image=uiMod.getImagePath("specialTools_transform_all%s"%self.blendImg), highlightImage= uiMod.getImagePath("specialTools_transform_all%s copy"%self.blendImg))
        

    def switch(self):
        
        mod         = uiMod.getModKeyPressed()
            
        if mod == "ctrl":
            self.setBlendRangeMode(not self.blendRangeMode)
            if self.onOff: self.onOff = False
                
        
        self.onOff  = (not self.onOff)
        self.setButtonImg(self.onOff) 
        self.blinkingButton(self.onOff)  
              
        self.setMode(self.onOff)
    
    def killJobs(self):
        G.deferredManager.removeFromQueue("transformAll")  
        self.animCurvesToSend   = []
        self.removeMessages() 
        utilMod.killScriptJobs("G.transformAllScriptJobs") 
        
    
    def setMode(self, onOff):
        
        self.killJobs()
                      
        if onOff: 
            
            #self.allAnimCurves = utilMod.getAllAnimCurves()   
            self.allValues = {}
            self.setRange()                  
            self.updateCurrentValues()
            utilMod.deselectTimelineRange()
            
            G.transformAllScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('timeChanged', self.updateCurrentValues )))
            G.transformAllScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('SelectionChanged', self.updateCurrentValues )))
            
            self.warn()
            
    
        else:
            cmds.warning("Transform All is OFF.")  
    
    def addAnimMessages(self):
        
        self.removeMessages()        
        G.TA_messages["anim"].append(OpenMayaAnim.MAnimMessage.addAnimCurveEditedCallback(self.sendToSetValues))
 
        
    def removeMessages(self):  
        
        try:
            for loopId in G.TA_messages["anim"]:
                OpenMayaAnim.MAnimMessage.removeCallback(loopId)
        except: pass   
        
        G.TA_messages["anim"]  = []    

    
    

    
    def sendToSetValues(self, *args):  
        
        curveMsg                = args[0]
        animCurves              = [OpenMaya.MFnDependencyNode(curveMsg[n]).name() for n in range(curveMsg.length())] 
        
        if OpenMaya.MGlobal.isUndoing() or OpenMaya.MGlobal.isRedoing(): 
            self.updateCurrentValues(animCurves)
            return
          
        self.animCurvesToSend.extend(animCurves)
        
        
        animCurves          = list(set(self.animCurvesToSend))    
        
        G.deferredManager.removeFromQueue("transformAll")
        function            = lambda *args:self.setValues(animCurves)
        G.deferredManager.sendToQueue(function, 1, "transformAll")
        
    
    def getRange(self):
        
        animCurves  = cmds.keyframe(query=True, name=True, selected=True)
        
        if animCurves:
        
            keysSel     = animMod.getTarget("keysSel", animCurves, "graphEditor")
            keysSel     = utilMod.mergeLists(keysSel)   
            range       = [min(keysSel), max(keysSel)]
                
        else:
            G.playBackSliderPython  = G.playBackSliderPython or mel.eval('$aTools_playBackSliderPython=$gPlayBackSlider')
            range                   = cmds.timeControl(G.playBackSliderPython, query=True, rangeArray=True)
            
            range[1] -= 1
                
        return range    
     
    def getCurrentValues(self, animCurves):
         if animCurves:  
            result  = {"keyValues":[], "timeValues":[]}    
            for loopCurve in animCurves:
                time = cmds.keyframe(loopCurve, selected=True, query=True, timeChange=True)
                
                if time:
                    time = [time[0], time[-1]]
                    result["keyValues"].append(cmds.keyframe(loopCurve, query=True, time=(time[0],time[-1]), valueChange=True))
                else:
                    time = cmds.currentTime(query=True); time = [time, time]
                    result["keyValues"].append(cmds.keyframe(loopCurve, query=True, eval=True, valueChange=True))
                
                result["timeValues"].append(time)
                
            return result 
    
     
    def updateCurrentValues(self, animCurves=None, *args):      
 
        cmds.undoInfo(stateWithoutFlush=False)
   
        self.removeMessages() 
 
        if not animCurves: animCurves = utilMod.getAllAnimCurves(selection=True)
        if not animCurves: return 
         
        for loopCurve in animCurves:
            #if loopCurve in self.allAnimCurves:            
            self.currentValues[loopCurve]   = self.getCurrentValues([loopCurve])["keyValues"][0]
            self.allValues[loopCurve]       = animMod.getTarget("keyValues", [loopCurve])[0]
            
        
        self.addAnimMessages()
        cmds.undoInfo(stateWithoutFlush=True)
        

    
    def setValues(self, animCurves):
        
        cmds.refresh(suspend=True)
        
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        
        self.removeMessages() 
        self.warn()
        
        values                  = self.getCurrentValues(animCurves)
        newKeyValues            = values["keyValues"]
        timeValues              = values["timeValues"]
        offsetValues            = []
        offsetPercentsA         = []
        offsetPercentsB         = []
        pivotAs                 = []
        pivotBs                 = []
        self.animCurvesToSend   = []  
        
       
        for n, loopCurve in enumerate(animCurves):
            
            oldVal      = self.currentValues[loopCurve][0]
            newVal      = newKeyValues[n][0]
                       
            if self.blendRangeMode:          
                        
                pivotA          = cmds.keyframe(loopCurve, query=True, eval=True, time=(self.range[0],self.range[0]), valueChange=True)[0]
                pivotB          = cmds.keyframe(loopCurve, query=True, eval=True, time=(self.range[1],self.range[1]), valueChange=True)[0]
                
               
                if oldVal == pivotA: 
                    pivotA          = newVal
                    offsetPercentA  = 0
                else:
                    offsetPercentA  = float((newVal-pivotA)/(oldVal-pivotA))
                if oldVal == pivotB: 
                    pivotB          = newVal
                    offsetPercentB  = 0
                else:
                    offsetPercentB  = float((newVal-pivotB)/(oldVal-pivotB))
  
                offsetPercentsA.append(offsetPercentA)
                offsetPercentsB.append(offsetPercentB)  
                pivotAs.append(pivotA)
                pivotBs.append(pivotB)
                
            else:
                offsetVal   = newVal - oldVal
                
                offsetValues.append(offsetVal)  
        
            
        #reset change        
        cmds.undoInfo(stateWithoutFlush=False)
        for loopCurve in list(self.allValues.keys()):  
            if loopCurve in animCurves:          
                valueChange = self.allValues[loopCurve]
                for n, loopValue in enumerate(valueChange):
                    cmds.keyframe(loopCurve, edit=True, index=(n,n), valueChange=loopValue)
                #self.allValues[] = {}
        cmds.undoInfo(stateWithoutFlush=True)
        
        
        
        #set values for all keys  
        curvesToUpdate = []      
        
        if self.blendRangeMode:  
            for n, loopCurve in enumerate(animCurves):
                time        = timeValues[n]
                timeOffsetA = .01
                timeOffsetB = .01
                
                if time[0] == self.range[0]: timeOffsetA = 0
                if time[1] == self.range[1]: timeOffsetB = 0
                
                if timeOffsetA != 0 and timeOffsetB != 0 and not self.range[0] < time[0] <= time[1] < self.range[1]: 
                    cmds.warning("Selected keys out of range %s"%self.range)
                    continue 
                
                offsetPercentA = offsetPercentsA[n]
                offsetPercentB = offsetPercentsB[n]
                #if offsetPercentA != 0 or offsetPercentB != 0:
                pivotA = pivotAs[n]
                pivotB = pivotBs[n]                    
                curvesToUpdate.append(loopCurve)
                cmds.scaleKey(loopCurve, time=(self.range[0]+timeOffsetA, time[1]), valuePivot=pivotA, valueScale=offsetPercentA)
                cmds.scaleKey(loopCurve, time=(time[1]+.01, self.range[1]-timeOffsetB), valuePivot=pivotB, valueScale=offsetPercentB) 
                    
        else:
            for n, loopCurve in enumerate(animCurves):
                if offsetValues[n] != 0:
                    curvesToUpdate.append(loopCurve)
                    if self.range == "All Keys":
                        #pass
                        cmds.keyframe(loopCurve, edit=True, valueChange=offsetValues[n], relative=True)
                    else:
                        cmds.keyframe(loopCurve, edit=True, time=(self.range[0], self.range[1]), valueChange=offsetValues[n], relative=True)
        
        
        self.updateCurrentValues(curvesToUpdate)      
        cmds.undoInfo(closeChunk=True)
        cmds.refresh(suspend=False)        
        
        
    def warn(self): 
        if self.blendRangeMode: 
            blendTxt = "Blend Range Mode "
        else:
            blendTxt = ""
                    
        cmds.warning("Transform All %sis ON. Please remember to turn it OFF when you are done. Acting on range: %s"%(blendTxt, self.range))  
        
    def setRange(self):
        self.range = self.getRange()
        
        if self.range[1] - self.range[0] <= 1: #if only one key selected     
            if self.blendRangeMode: self.range = [cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)] 
            else:                   self.range = "All Keys"
 
            
            




