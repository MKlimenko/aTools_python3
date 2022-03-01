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

from maya import mel
from maya import cmds
from maya import OpenMaya
from maya import OpenMayaAnim
from maya import OpenMayaUI
from maya import OpenMayaRender
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod
from aTools.commonMods import aToolsMod


import os
import math
import time   
from itertools import cycle


class MotionTrail(object):   
    
    
    def __init__(self):
        
        if G.aToolsBar.motionTrail: return
        G.aToolsBar.motionTrail = self
        
        self.STORE_NODE                 = "specialTools"
        self.MOTION_TRAIL_ATTR          = "twistIkObjs"
        self.PRE_POS_RANGE              = "motionTrailPrePosRange"
        self.SIZE                       = "motionTrailSize"
        self.PREF_KEY                   = "motionTrailPrefKey"
        self.CAMERA_KEY                 = "motionTrailCameraRelative"
        self.mainGroupNode              = "aTools_MotionTrail"
        self.queueOrder                 = 5
        self.prePosRanges               = [3, 6, 12, 24, "Playback Range"]
        self.defaultPrePosRange         = 24
        self.twistIkObjs                = []
        self.constraintLocators         = []
        self.firstFrame                 = 0
        self.lastFrame                  = 0
        self.nodeInfo                   = {}
        self.offsetCtrlsPosition        = {}
        self.onOff                      = False
        self.blockingMode               = False
        self.lastCurvesEdited           = None
        cameraRelativeMode              = aToolsMod.loadInfoWithUser("userPrefs", self.CAMERA_KEY)
        self.cameraRelativeMode         = cameraRelativeMode if cameraRelativeMode != None else True
        
        
        #MOTION TRAIL DRAW
        self.color                      = {"curr_frame"     :(1,0,0),
                                           "key_before"     :(0,0,1),
                                           "key_after"      :(0,1,0),
                                           "frame_before"   :(0,0,1),
                                           "frame_after"    :(0,1,0),
                                           "dirty"          :(1,1,1),
                                           "line"           :[(1,1,1), (1,1,0), (0,1,1), (1,0,1)]
                                           }
        self.size                       = {"curr_frame"     :5,
                                           "key_before"     :3,
                                           "key_after"      :3,
                                           "frame_before"   :1,
                                           "frame_after"    :1,
                                           "dirty"          :1,
                                           "line"           :.5
                                           }
        self.baseOpacity                = 1
        self.customSizes                = [["small", 1], ["medium", 2], ["large",4]]
        self.defaultSize                = "medium"
        self.prefKeys                   = ["selection", "motionTrail"]
        self.defaultPrefKey             = "selection"
        
        self.clear()
        
        
    def popupMenu(self, *args):            
        cmds.popupMenu("motionTrailMenu",         postMenuCommand=self.populateMenu)
        
    def populateMenu(self, menu, *args):
        uiMod.clearMenuItems(menu)
        #cmds.menuItem(label="Camera Relative", parent=menu, checkBox=self.cameraRelativeOnOff, command=self.cameraRelativeSwitch)
  
        
        if cmds.objExists(self.mainGroupNode):
            cmds.menuItem(label="Add Selection", parent=menu, command=self.addSelection)
            cmds.menuItem(label="Remove Selection", parent=menu, command=self.removeSelection)
            cmds.menuItem(label="Set Frame Range", parent=menu, command=self.setFrameRange)
            cmds.menuItem( divider=True, parent=menu)
            
            
        if cmds.objExists(self.mainGroupNode):        
            for loopMotionTrail in self.nodeInfo.keys():
                ctrl    =  self.nodeInfo[loopMotionTrail]["ctrlNode"]
                cmds.menuItem(label="Grab Offset Ctrl (%s)"%ctrl, parent=menu, command=lambda x, loopMotionTrail=loopMotionTrail, *args:self.grabOffsetCtrl(loopMotionTrail))
        
            cmds.menuItem( divider=True, parent=menu)
            
        subMenu = cmds.menuItem(label="Preferences", subMenu=True, parent=menu, tearOff=True)
         
        #Pre pos range           
        cmds.radioMenuItemCollection(parent=subMenu)
        rangeSelected = self.getPrePosRange()
        for loopPref in self.prePosRanges:    
            radioSelected = (str(rangeSelected) == str(loopPref))
            cmds.menuItem(label="%s"%loopPref, radioButton=radioSelected, command=lambda x, loopPref=loopPref, *args:self.savePrePosRange(loopPref), parent=subMenu)
        
        #Size     
        cmds.menuItem( divider=True, parent=subMenu)
        cmds.radioMenuItemCollection(parent=subMenu)
        sizeSelected = self.getPrefSize()
        for loopSize in self.customSizes:
            sizeName        = loopSize[0]
            radioSelected   = (str(sizeSelected) == str(sizeName))
            cmds.menuItem(label=utilMod.toTitle(sizeName), radioButton=radioSelected, command=lambda x, sizeName=sizeName, *args:self.savePrefSize(sizeName), parent=subMenu)
        
        # Keys    
        cmds.menuItem( divider=True, parent=subMenu)
        cmds.radioMenuItemCollection(parent=subMenu)
        keySelected = self.getPrefKey()
        for loopPref in self.prefKeys:  
            radioSelected = (str(keySelected) == str(loopPref))
            cmds.menuItem(label="Show %s Keys"%utilMod.toTitle(loopPref), radioButton=radioSelected, command=lambda x, loopPref=loopPref, *args:self.savePrefKey(loopPref), parent=subMenu)
       
        # Camera Relative    
        cmds.menuItem( divider=True, parent=subMenu)
        cmds.menuItem(label="Camera Relative", checkBox=self.cameraRelativeMode, command=self.setCameraRelativeMode, parent=subMenu)
    
        
        cmds.menuItem(divider=True, parent=menu)
        cmds.menuItem(label="Refresh", parent=menu, command=self.refreshMotionTrail)
        
        
    def addSelection(self, *args):
        
        sel     = cmds.ls(selection=True)        
        self.createMotionTrail(sel) 
        
        
    def removeSelection(self, *args):
        
        sel     = cmds.ls(selection=True)
        
        for loopSel in sel:
            ctrlName = self.getCtrlName(loopSel)
            self.removeMotionTrail(ctrlName)
        
    
    def removeMotionTrail(self, motionTrail):
        
        if self.nodeInfo.has_key(motionTrail): 
            
            groupNode   = self.nodeInfo[motionTrail]["groupNode"]
            
            self.saveOffset([motionTrail])
            self.nodeInfo.pop(motionTrail, None)  
            if cmds.objExists(groupNode): cmds.delete(groupNode)              
            self.refreshViewports()
            
        if len(self.nodeInfo.keys()) == 0: self.clear()
    
 
        
    # PREFS===========================================
    
    def setCameraRelativeMode(self, onOff):
        
        self.cameraRelativeMode = onOff
        
        aToolsMod.saveInfoWithUser("userPrefs", self.CAMERA_KEY, onOff)
        self.refreshViewports()
    
    def setPrefs(self):
        self.setPrefKey(self.getPrefKey())
        self.setPrePosRange(self.getPrePosRange())
        self.setPrefSize(self.getPrefSize())  
    
    def setPrefKey(self, prefKey):   
        self.prefKey = prefKey
        
        self.updateKeysTimes()
        self.refreshViewports()
        
    def getPrefKey(self):
        prefKey = aToolsMod.loadInfoWithUser("userPrefs", self.PREF_KEY)   
        if not prefKey: prefKey = self.defaultPrefKey
        return prefKey   
    
    def savePrefKey(self, prefKey):
        self.setPrefKey(prefKey)
        aToolsMod.saveInfoWithUser("userPrefs", self.PREF_KEY, prefKey)     
          
    
    def getPrePosRange(self):
        range = aToolsMod.loadInfoWithUser("userPrefs", self.PRE_POS_RANGE)   
        if not range: range = self.defaultPrePosRange
        return range   
    
    def setPrePosRange(self, range):   
        self.prePosRange = 0 if range == "Playback Range" else range
        self.refreshViewports()
    
    def savePrePosRange(self, range):
        self.setPrePosRange(range)
        aToolsMod.saveInfoWithUser("userPrefs", self.PRE_POS_RANGE, range)  
    
    def setPrefSize(self, sizeValue):         
        
        for loopSize in self.customSizes:
            
            if loopSize[0] == self.defaultSize:          
                self.sizeMultiplier = loopSize[1] 
            
            if loopSize[0] == sizeValue:          
                self.sizeMultiplier = loopSize[1] 
                break

        self.refreshViewports()
        
    def getPrefSize(self):
        size = aToolsMod.loadInfoWithUser("userPrefs", self.SIZE)   
        if not size: size = self.defaultSize
        return size   
    
    def savePrefSize(self, sizeValue):
        self.setPrefSize(sizeValue)
        aToolsMod.saveInfoWithUser("userPrefs", self.SIZE, sizeValue) 
    
    #==========================================================================
    
    def grabOffsetCtrl(self, motionTrail, *args):
        cmds.select(self.nodeInfo[motionTrail]["offsetNode"])
        cmds.setToolTo("Move")
        cmds.manipMoveContext('Move', edit=True, mode=0)
            
    def click(self):
        
        mod = uiMod.getModKeyPressed()
            
        if mod == "shift":
            if not self.onOff: self.setMode(True)
            self.addSelection() 
        elif mod == "ctrl":
            if not self.onOff: self.setMode(True)
            self.removeSelection()
        else:
            self.switch()
    
    
    def switch(self):
        
        sel     = cmds.ls(selection=True)
        img     = cmds.iconTextButton(self.toolBarButton, query=True, image=True)
        onOff   = (img[-10:-4] != "active")
        
        if len(sel) == 0 and onOff:  
            cmds.warning("Please select at least one object.")
            return
        
        if len(sel) > 10 and onOff: 
            message         = "Too many objects selected, continue?"
            confirm         = cmds.confirmDialog( title='Confirm', message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if confirm != 'Yes': return  
            
         
        self.clear()          
        self.setMode(onOff)
        

    
    def setMode(self, onOff):
        
        sel                     = cmds.ls(selection=True)
        self.onOff              = onOff
        
        
        if onOff:
            
            cmds.iconTextButton(self.toolBarButton, edit=True, image=uiMod.getImagePath("specialTools_motion_trail_active"), highlightImage= uiMod.getImagePath("specialTools_motion_trail_active"))
            
            self.setPrefs()
            self.updateFrameRange()
            self.createMotionTrail(sel) 
            self.addMessages()              
            self.addScriptJobs()
      
        else:
            cmds.iconTextButton(self.toolBarButton, edit=True, image=uiMod.getImagePath("specialTools_motion_trail"), highlightImage= uiMod.getImagePath("specialTools_motion_trail copy"))
            self.removeAllCallbacks()
    
        
    def callbackTimeChanged(self):
        self.updateSortedRange()
        self.refreshDagNodes()
        
    
    def refreshDagNodes(self):
        
        for loopMotionTrail in self.nodeInfo.keys():                
                
            motionTrailNode    = self.nodeInfo[loopMotionTrail]["motionTrailNode"] 
            motionTrailAttr    = self.nodeInfo[loopMotionTrail]["motionTrailAttr"]  
        
            cmds.setAttr("%s.update"%motionTrailNode, 0)
            cmds.setAttr("%s.update"%motionTrailNode, 1)
            cmds.dgeval(motionTrailAttr)

    
    def callbackSelectionChange(self):
        
        self.updateKeysTimes()
        self.addNodeMessages()
        G.deferredManager.sendToQueue(self.refreshViewports, 1, "MT_refreshViewports") 
        
    
    def addScriptJobs(self):
        
        G.callbackManager.removeFromQueue("MT_scriptJobs")

        G.callbackManager.sendToQueue(cmds.scriptJob(runOnce=False,     killWithScene=False, event=('SelectionChanged', self.callbackSelectionChange )),    "scriptJob", "MT_scriptJobs")
        G.callbackManager.sendToQueue(cmds.scriptJob(runOnce = False,   killWithScene=False, event=('timeChanged',      self.callbackTimeChanged )),        "scriptJob", "MT_scriptJobs")
            
    
        
    def addMessages(self):
        
        G.callbackManager.removeFromQueue("MT_anim")        
        G.callbackManager.removeFromQueue("MT_view")
        
        viewports   = utilMod.getAllViewports()
        
        G.callbackManager.sendToQueue(OpenMayaAnim.MAnimMessage.addAnimCurveEditedCallback(self.callbackCurveEdited), "OpenMayaAnim.MAnimMessage", "MT_anim")
        
        for loopViewport in viewports:
            G.callbackManager.sendToQueue(OpenMayaUI.MUiMessage.add3dViewPostRenderMsgCallback(loopViewport, self.drawViewports), "OpenMayaUI.MUiMessage", "MT_view")
       
        self.addNodeMessages()
    
    def addNodeMessages(self):  
        
        sel         = cmds.ls(selection=True)    
        
        G.callbackManager.removeFromQueue("MT_node")
        
        for loopSel in sel:     
            node = utilMod.getMObject(loopSel)
            
            G.callbackManager.sendToQueue(OpenMaya.MNodeMessage.addAttributeChangedCallback(node, self.callbackAttrEdited, None), "OpenMaya.MNodeMessage", "MT_node")
        
             
    """  
    def addDirtyMessage(self, node):  
        
        node                = utilMod.getMObject(node)            
        .append(OpenMaya.MNodeMessage.addNodeDirtyPlugCallback(node, self.callbackNodeDirty, None)) 
    """
   
    def removeAllCallbacks(self):          
        
        G.callbackManager.removeFromQueue("MT_scriptJobs")
        G.callbackManager.removeFromQueue("MT_node")
        G.callbackManager.removeFromQueue("MT_anim")
        G.callbackManager.removeFromQueue("MT_view")
        
    
    def callbackCurveEdited(self, *args):
        
        curveMsg                = args[0]
        self.lastCurvesEdited   = [OpenMaya.MFnDependencyNode(curveMsg[n]).name() for n in xrange(curveMsg.length())] 
        
        self.updateCurrFrameMotionTrailPoints()
        G.deferredManager.sendToQueue(self.updateDirtyMotionTrails, self.queueOrder, "motionTrailUpdate")

           
    def callbackAttrEdited(self, msg, mplug, otherMplug, clientData):
        
        if OpenMaya.MNodeMessage.kAttributeSet == (OpenMaya.MNodeMessage.kAttributeSet & msg):
            
            self.updateCurrFrameMotionTrailPoints()
            G.deferredManager.sendToQueue(self.updateDirtyMotionTrails, self.queueOrder, "motionTrailUpdate")
            
    def updateCurrFrameMotionTrailPoints(self):
        
        if not self.currFrame in self.sortedRange: return

        for loopMotionTrail in self.nodeInfo.keys():
            
            if self.checkIfDeleted(loopMotionTrail): continue
                            
            offsetNode  = self.nodeInfo[loopMotionTrail]["offsetNode"]
            pointMatrix = cmds.getAttr("%s.wm"%offsetNode)
            
            self.nodeInfo[loopMotionTrail][self.currFrame]["pointMatrix"]   = pointMatrix
            
 
            
    def updateDirtyMotionTrails(self):    
        
        for loopMotionTrail in self.nodeInfo.keys():
            
            if self.checkIfDeleted(loopMotionTrail): continue
                      
            motionTrailAttr         = self.nodeInfo[loopMotionTrail]["motionTrailAttr"]
            isDirty                 = cmds.isDirty(motionTrailAttr, datablock=True)
                
            if isDirty: self.makeDirty(loopMotionTrail)                
                
                
        G.deferredManager.removeFromQueue("motionTrailUpdate")
        self.updateKeysTimes()
        self.updateBlockingMode() 
        self.updateSortedRange()   
        self.updateMotionTrail()
        
    
    def getTotalDirty(self):
        
        totalDirty = 0
        
        for loopMotionTrail in self.nodeInfo.keys():
        
            for loopFrame in self.sortedRange:  
    
                if not self.nodeInfo[loopMotionTrail].has_key(loopFrame): 
                    totalDirty += 1
                    continue
                
                if self.nodeInfo[loopMotionTrail][loopFrame]["status"] != "clean": totalDirty += 1
        

                
        return totalDirty
                
        
    def updateMotionTrail(self, lightningMode=False):
                
        showProgress    = lightningMode
        totalDirty      = self.getTotalDirty()
        progressInfo    = None
        
        G.deferredManager.removeFromQueue("motionTrailUpdate")
        
        if totalDirty == 0: return
        
        if showProgress:
            firstStep       = 0
            thisStep        = 0
            estimatedTime   = None
            totalSteps      = totalDirty
            status          = "aTools - Creating Motion Trail..."
            startChrono     = None
            progressInfo    = [startChrono, firstStep, thisStep, totalSteps, estimatedTime, status] 
            
            utilMod.startProgressBar(status)  
                
        self.updateCache(lightningMode, progressInfo)
        if showProgress: utilMod.setProgressBar(endProgress=True)
         
    
    def updateCache(self, lightningMode=False, progressInfo=None, *args):
                
        nextBit = self.getNextBit()
        
        if not nextBit: 
            self.refreshViewports()
            return        
        
        if lightningMode:
            
            startChrono, firstStep, thisStep, totalSteps, estimatedTime, status = progressInfo
            thisStep        += 1
            startChrono     = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)
            
            self.updateBit(nextBit)   
            
            estimatedTime   = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
            progressInfo    = [startChrono, firstStep, thisStep, totalSteps, estimatedTime, status]
            
            self.updateCache(lightningMode, progressInfo)
        
            
        else:               
            G.deferredManager.sendToQueue(lambda *args: self.updateBit(nextBit),            self.queueOrder, "motionTrailUpdate")
            G.deferredManager.sendToQueue(self.refreshViewports,                            self.queueOrder, "MT_refreshViewports")
            G.deferredManager.sendToQueue(lambda *args: self.updateCache(lightningMode),    self.queueOrder, "motionTrailUpdate")
            
            
        
        
    def updateBit(self, bit):
         
        motionTrail, frame = bit  

        self.cacheMotionTrail(motionTrail, frame) 
            
    
    def getNextBit(self):
        
         
        for loopFrame in self.sortedRange:
            for loopMotionTrail in self.nodeInfo.keys():                
                
                if self.nodeInfo[loopMotionTrail].has_key(loopFrame): 
                    if self.nodeInfo[loopMotionTrail][loopFrame]["status"] == "clean": continue
                else:
                    self.nodeInfo[loopMotionTrail][loopFrame]           = {}
                    self.nodeInfo[loopMotionTrail][loopFrame]["status"] = "dirty" 
                
                return [loopMotionTrail, loopFrame]  
    
    def checkIfDeleted(self, motionTrail):
        
        if not cmds.objExists(self.nodeInfo[motionTrail]["offsetNode"]):            
            self.nodeInfo.pop(motionTrail, None)
            return True
            

    
    
    def makeDirty(self, motionTrail):
                
        if self.checkIfDeleted(motionTrail): return        
        
        motionTrailAttr    = self.nodeInfo[motionTrail]["motionTrailAttr"]   
        cmds.dgeval(motionTrailAttr)
            
        for loopFrame in self.sortedRange:  
    
            if not self.nodeInfo[motionTrail].has_key(loopFrame): self.nodeInfo[motionTrail][loopFrame] = {}
                    
            self.nodeInfo[motionTrail][loopFrame]["status"] = "dirty" 
            
            
            

    def cacheMotionTrail(self, motionTrail, frame):
        
        
        if self.checkIfDeleted(motionTrail): return
        
        self.disableTwistObjs()
        
        offsetNode                                          = self.nodeInfo[motionTrail]["offsetNode"]
        pointMatrix                                         = cmds.getAttr("%s.wm"%offsetNode, time=frame)
        self.nodeInfo[motionTrail][frame]["pointMatrix"]    = pointMatrix 
        self.nodeInfo[motionTrail][frame]["status"]         = "clean"  
                
        self.reenableTwistObjs()        
       
    def createMainGroup(self):
        
        if cmds.objExists(self.mainGroupNode): return self.mainGroupNode         
        
        with G.aToolsBar.createAToolsNode: 
            groupNode = cmds.createNode("transform", name=self.mainGroupNode, skipSelect=True) or False
            return groupNode
    
    def createCtrlGroup(self, ctrlName):
        
        ctrlGroup                 = "%s_aTools_group"%ctrlName    
            
        if not cmds.objExists(ctrlGroup): 
            with G.aToolsBar.createAToolsNode:
                groupNode = cmds.createNode("transform", name=ctrlGroup, skipSelect=True) 
                return groupNode
    
    def createMotionTrailNode(self, masterNode):
        
        with G.aToolsBar.createAToolsNode: 
        
            motionTrailNode         = cmds.createNode("motionTrail", name="%s_motionTrailNode"%masterNode, skipSelect=True)
            motionTrailShape        = cmds.createNode("motionTrailShape", skipSelect=True)
            motionTrailTransform    = cmds.rename(cmds.listRelatives(motionTrailShape, parent=True)[0], "%s_motionTrailTransform"%masterNode)
            motionTrailAttr         = "%s.points"%motionTrailNode
            
            cmds.hide(motionTrailTransform)
            cmds.connectAttr("%s.worldMatrix"%masterNode, "%s.inputMatrix"%motionTrailNode, force=True)
            cmds.connectAttr("%s.points"%motionTrailNode, "%sShape.points"%motionTrailTransform, force=True)
        
        return [motionTrailTransform, motionTrailAttr, motionTrailNode]
    
    def createMotionTrail(self, ctrls):
        
        cmds.waitCursor(state=True)
        self.saveTwistObjsInfo()        
        self.createMainGroup()
        
        for loopCtrl in ctrls: 
            ctrlName                    = self.getCtrlName(loopCtrl)
            groupNode                   = self.createCtrlGroup(ctrlName)
            
            if not groupNode: continue
            
            motionTrail                 = "%s_aTools_motionTrail"%ctrlName
            offsetNode                  = "%s_aTools_offset"%ctrlName
            currentLocators             = [motionTrail, offsetNode]
            
            for loopLocator in currentLocators: animMod.createNull(loopLocator)
            cmds.hide(currentLocators)
            
            motionTrailList             = self.createMotionTrailNode(offsetNode)
            motionTrailTransform        = motionTrailList[0]
            motionTrailAttr             = motionTrailList[1]
            motionTrailNode             = motionTrailList[2]
            self.nodeInfo[ctrlName]     = {"ctrlNode":loopCtrl, "offsetNode":offsetNode, "groupNode":groupNode, "motionTrailTransform":motionTrailTransform, "motionTrailAttr":motionTrailAttr, "motionTrailNode":motionTrailNode, "lineColor":self.lineColorCycle.next()}            
            
            
            with G.aToolsBar.createAToolsNode: 
                
                cmds.parent(offsetNode, motionTrail) 
                cmds.parent(motionTrail, groupNode)
                cmds.parent(motionTrailTransform, groupNode)
                cmds.parent(groupNode, self.mainGroupNode)
                cmds.parentConstraint(loopCtrl, motionTrail)
                
            
            if self.offsetCtrlsPosition.has_key(ctrlName): 
                offsetNodePosition = self.offsetCtrlsPosition[ctrlName][0]
                if offsetNodePosition != (0,0,0): cmds.setAttr("%s.translate"%offsetNode, offsetNodePosition[0], offsetNodePosition[1], offsetNodePosition[2])
           
            self.makeDirty(ctrlName)
            
        cmds.select(ctrls)
        self.updateMotionTrail(lightningMode=True)
        self.updateKeysTimes() 
        self.updateSortedRange() 
        cmds.waitCursor(state=False)
        
    def getCtrlName(self, ctrl):        
        return ctrl.replace(":", "___")
    
    def updateFrameRange(self, all=False):
        
        rangeVisible            = cmds.timeControl(G.playBackSliderPython, query=True, rangeVisible=True )
        
        if not rangeVisible or all:
            range = [cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)+1]
        else:            
            range = cmds.timeControl(G.playBackSliderPython, query=True, rangeArray=True)
            #range[1] -= 1            
                
        self.firstFrame         = range[0]
        self.lastFrame          = range[1]-1
        
        self.updateSortedRange()
        self.updateCameraMatrices()
        
    def getAllCameras(self):
        defaultCameras  = [u'frontShape', u'perspShape', u'sideShape', u'topShape']
        cameras         = [cam for cam in cmds.ls(cameras=True) if cam not in defaultCameras]  
        return cameras 
    
    def getCamFromNodes(self, nodes):
        if len(nodes) > 0:
            if "camera" in cmds.nodeType(nodes[0], inherited=True):
                transformNode   = cmds.listRelatives(nodes[0], parent=True)[0]
                shapeNode       = nodes[0]
                
            elif cmds.nodeType(nodes[0]) == "transform":
                transformNode   = nodes[0]
                shapeNode       = cmds.listRelatives(nodes[0], shapes=True)[0]
                
            return [transformNode, shapeNode]
        
    def updateCameraMatrices(self):    
        
        self.cameraInfo = {}
        cameraShapes    = self.getAllCameras()
        cameraNodes     = self.getCamFromNodes(cameraShapes)
        
        if not cameraNodes: return
        
        for loopCamera in cameraNodes:        
            self.cameraInfo[loopCamera] = {}
        
            for loopFrame in self.sortedRange:
                self.cameraInfo[loopCamera][loopFrame] = {}                
                self.cameraInfo[loopCamera][loopFrame]["pointMatrix"] = cmds.getAttr("%s.wm"%loopCamera, time=loopFrame)

    def addFrameCameraMatrices(self, frame):
        
        cameraShapes    = self.getAllCameras()
        cameraNodes     = self.getCamFromNodes(cameraShapes)
        
        if not cameraNodes: return
        
        for loopCamera in cameraNodes:   
        
            self.cameraInfo[loopCamera][frame] = {}                
            self.cameraInfo[loopCamera][frame]["pointMatrix"] = cmds.getAttr("%s.wm"%loopCamera, time=frame)

    def setFrameRange(self, *args):
        
        self.updateFrameRange()
        #self.updateMotionTrail()
        self.updateMotionTrail(lightningMode=True)
        self.refreshViewports()
    
    def saveOffset(self, motionTrails=None):
        
        motionTrails = motionTrails or self.nodeInfo.keys() 
        
        for loopMotionTrail in motionTrails:
            offsetNode = self.nodeInfo[loopMotionTrail]["offsetNode"]
                        
            if not cmds.objExists(offsetNode): continue
            
            offsetNodePosition                         = cmds.getAttr("%s.translate"%offsetNode)
            self.offsetCtrlsPosition[loopMotionTrail]  = offsetNodePosition

    def clear(self): 
        
        self.saveOffset()    
        self.removeAllCallbacks()    
        G.deferredManager.removeFromQueue("motionTrailUpdate")
        self.loadTwistObjsInfo()
        if self.onOff: self.setMode(False)
        cmds.refresh(suspend=False)
        if cmds.objExists(self.mainGroupNode): cmds.delete(self.mainGroupNode)


        self.nodeInfo       = {}
        self.lineColorCycle = cycle(self.color["line"])
        
    
    def getKeyTimes(self, prefKey=None):
        
        prefKey         = prefKey or self.prefKey  
        getFrom         = None   
        keyTimesDict    = {}
        keyTimes        = []
        
        
        if prefKey in ["selection", "selection_list"]:
            
            animCurves  = cmds.keyframe(query=True, name=True)   
            keyTimes    = animMod.getTarget("keyTimes", animCurves) if animCurves else []
            keyTimes    = sorted(utilMod.mergeLists(keyTimes))  
                    
            for n, loopMotionTrail in enumerate(self.nodeInfo.keys()): keyTimesDict[loopMotionTrail] = keyTimes
            
        else: 
            for loopMotionTrail in self.nodeInfo.keys():
                
                animCurves                      = cmds.keyframe(loopMotionTrail, query=True, name=True)            
                keyTimes                        = animMod.getTarget("keyTimes", animCurves) if animCurves else []
                keyTimesDict[loopMotionTrail]   = utilMod.mergeLists(keyTimes)
                
        
        return keyTimesDict
    
    def updateKeysTimes(self):        
        
        self.keysTimesDict   = self.getKeyTimes()
        self.keysTimes       = self.keysTimesDict[self.keysTimesDict.keys()[0]] if len(self.keysTimesDict) > 0 else []
            
    
    def updateBlockingMode(self):
        
        if not self.lastCurvesEdited: return
        
        tangentType         = list(set(cmds.keyTangent(self.lastCurvesEdited[0], query=True, outTangentType=True)))[0]
        self.blockingMode   = (tangentType == "step")
        
    def refreshMotionTrail(self, *args):
        
        for loopMotionTrail in self.nodeInfo.keys(): self.makeDirty(loopMotionTrail)
        
        self.updateMotionTrail(lightningMode=True)    
    
    def updateSortedRange(self):
        
        self.sortedRange = self.getSortedRange()
    
    def getSortedRange(self):
        
        range           = utilMod.rangeToList([self.firstFrame, self.lastFrame])
        keys            = self.keysTimes if self.blockingMode else []
        currTime        = int(cmds.currentTime(query=True))
        currFrame       = currTime if currTime in range else range[0]
        sortedRange     = [currFrame] if currFrame in range else []
        ranges          = [keys, range]
        self.currFrame  = currTime
                        
        for loopRange in ranges:  
                    
            if len(loopRange) == 0: continue         
            
            count       = 0
            direction   = 1  
            frame       = currFrame    
            
            while True: 
                if frame in range:          
                    if frame in loopRange and frame not in sortedRange: 
                        sortedRange.append(frame)
                else: break
                
                increase    = ((1+count) * direction)
                next        = (increase + frame)
                
                if next > loopRange[-1] or next < loopRange[0]:
                    increase = 1 * direction *-1
                else: 
                    direction *= -1 
                    
                frame       += increase  
                count       += 1 
                        
        return sortedRange
    
    
    def getCameraPoint(self, camera, frame, currFrame, pointMatrix):
        
        if not self.cameraInfo[camera].has_key(currFrame): self.addFrameCameraMatrices(currFrame)
        
        camMatrixAtFrame    = utilMod.getApiMatrix(self.cameraInfo[camera][frame]["pointMatrix"])
        camMatrixCurrFrame  = utilMod.getApiMatrix(self.cameraInfo[camera][currFrame]["pointMatrix"])
        pointMatrix         = utilMod.getApiMatrix(pointMatrix)
        localMatrix         = pointMatrix * camMatrixAtFrame.inverse()        
        worldMatrix         = localMatrix * camMatrixCurrFrame
        mt                  = OpenMaya.MTransformationMatrix(worldMatrix)
        translation         = mt.translation(OpenMaya.MSpace.kWorld)
        point               = [translation[0], translation[1], translation[2]]
        
        return point
    
    
    def getPointsArray(self, motionTrail, currFrame, camera=None):
        
        range           = [self.firstFrame, self.lastFrame] if self.prePosRange == 0 else [currFrame-self.prePosRange, currFrame+self.prePosRange]
        range[0]        = range[0] if range[0] >= self.firstFrame else self.firstFrame
        range[1]        = range[1] if range[1] <= self.lastFrame else self.lastFrame 
        rangeList       = utilMod.rangeToList(range)
        worldPoints     = []
        cameraPoints    = []
                
        for loopFrame in rangeList: 
                        
            if self.nodeInfo[motionTrail].has_key(loopFrame):
                if self.nodeInfo[motionTrail][loopFrame].has_key("pointMatrix"):                    
                    pointMatrix = self.nodeInfo[motionTrail][loopFrame]["pointMatrix"]
                    worldPoints.append(pointMatrix[12:15])
                    if camera: 
                        cameraPoint = self.getCameraPoint(camera, loopFrame, currFrame, pointMatrix)
                        cameraPoints.append(cameraPoint)
            
        return {"world":worldPoints, "camera":cameraPoints}
        
        
    
    def getIndexMap(self, motionTrail, keysTimes, currFrame, pointArray):
        
        indexMap    = {"curr_frame":[], "key_before":[], "frame_before":[], "key_after":[], "frame_after":[], "dirty":[], "ommited":[]}
        indexOffset =  self.firstFrame if self.prePosRange == 0 else currFrame - self.prePosRange if (currFrame - self.prePosRange) > self.firstFrame else self.firstFrame
        
        
        for loopIndex in xrange(len(pointArray)):
            
            frame = loopIndex + indexOffset
            
            if self.nodeInfo[motionTrail][frame]["status"] == "dirty":
                if self.blockingMode and frame not in keysTimes:    indexMap["ommited"].append(loopIndex)
                else:                                               indexMap["dirty"].append(loopIndex)
            elif frame == currFrame:                                indexMap["curr_frame"].append(loopIndex)
            elif frame < currFrame: 
                if frame in keysTimes:                              indexMap["key_before"].append(loopIndex)
                else:                                               indexMap["frame_before"].append(loopIndex)
            elif frame > currFrame: 
                if frame in keysTimes:                              indexMap["key_after"].append(loopIndex)
                else:                                               indexMap["frame_after"].append(loopIndex)
                
        return indexMap
     
    def drawPoints(self, glFT, indexMap, pointArray):
                
        for loopKey in indexMap:   
            
            if loopKey == "ommited": continue
            
            opacity     = self.baseOpacity         
            color       = self.color[loopKey]
            pointSize   = self.size[loopKey]*self.sizeMultiplier
            
            glFT.glPointSize(pointSize)  
            glFT.glBegin(OpenMayaRender.MGL_POINTS)
            glFT.glColor4f(color[0], color[1], color[2], opacity)                          
             
            for loopPoint in indexMap[loopKey]: 
                point           = pointArray[loopPoint]           
                glFT.glVertex3f( point[0],point[1],point[2] )
                         
            glFT.glEnd()   
    
    def drawLine(self, glFT, indexMap, pointArray, color):

        opacity     = self.baseOpacity  
        lineSize    = self.size["line"]*self.sizeMultiplier

                
        glFT.glLineWidth(lineSize)
        glFT.glBegin(OpenMayaRender.MGL_LINE_STRIP) 
        glFT.glColor4f(color[0], color[1], color[2], opacity)                          
            
        for n, loopPoint in enumerate(pointArray):
            
            if n in indexMap["ommited"]: continue
            
            glFT.glVertex3f( loopPoint[0],loopPoint[1],loopPoint[2] )                
        
        glFT.glEnd()
        
    def drawViewports(self, *args):
                
        glRenderer      = OpenMayaRender.MHardwareRenderer.theRenderer()
        glFT            = glRenderer.glFunctionTable()      
        currFrame       = int(cmds.currentTime(query=True))
                
        for loopViewport in utilMod.getAllViewports():  
            
            rendererName = cmds.modelEditor(loopViewport, query=True, rendererName=True)
                  
            for loopMotionTrail in self.nodeInfo.keys():
                
                
                viewportCamera  = cmds.modelEditor(loopViewport, query=True, camera=True) if self.cameraRelativeMode else None
                camera          = viewportCamera if viewportCamera in self.cameraInfo.keys() and self.cameraRelativeMode else None
                points          = self.getPointsArray(loopMotionTrail, currFrame, camera)
                pointArray      = points["camera"] if camera else points["world"]   
                loopKeysTimes   = [] if not self.keysTimesDict.has_key(loopMotionTrail) else self.keysTimesDict[loopMotionTrail]
                indexMap        = self.getIndexMap(loopMotionTrail, loopKeysTimes, currFrame, pointArray)  
                lineColor       = self.nodeInfo[loopMotionTrail]["lineColor"]      
                view            = OpenMayaUI.M3dView()
                
                
                OpenMayaUI.M3dView.getM3dViewFromModelPanel(loopViewport, view)
                view.beginGL()
                glFT.glPushAttrib(OpenMayaRender.MGL_ALL_ATTRIB_BITS)
                glFT.glPushMatrix()
                glFT.glDepthRange(0,0)                
                glFT.glEnable( OpenMayaRender.MGL_LINE_SMOOTH )
                glFT.glEnable( OpenMayaRender.MGL_POINT_SMOOTH )
                glFT.glEnable( OpenMayaRender.MGL_BLEND )
                glFT.glDisable(OpenMayaRender.MGL_LIGHTING)
                glFT.glBlendFunc( OpenMayaRender.MGL_SRC_ALPHA, OpenMayaRender.MGL_ONE_MINUS_SRC_ALPHA )
                
                #DRAW
                if rendererName == "ogsRenderer":               
                    self.drawLine(glFT, indexMap, pointArray, lineColor)
                    self.drawPoints(glFT, indexMap, pointArray) 
                else:                    
                    self.drawPoints(glFT, indexMap, pointArray)                
                    self.drawLine(glFT, indexMap, pointArray, lineColor)
              
                #WRAP
                glFT.glDisable( OpenMayaRender.MGL_BLEND )
                glFT.glDisable( OpenMayaRender.MGL_LINE_SMOOTH )
                glFT.glDisable( OpenMayaRender.MGL_POINT_SMOOTH )
                glFT.glEnable(OpenMayaRender.MGL_LIGHTING)
                glFT.glPopMatrix()
                glFT.glPopAttrib()
                view.endGL() 
    
    def refreshViewports(self):
        
        G.deferredManager.removeFromQueue("MT_refreshViewports")
        
        for loopViewport in utilMod.getAllViewports():    
    
            view        = OpenMayaUI.M3dView()
            OpenMayaUI.M3dView.getM3dViewFromModelPanel(loopViewport, view)            
            
            view.refresh(True, True) 
            
                
    
    #functions to deal with twist IKs offset bug======================================
    
    def saveTwistObjsInfo(self):
        self.loadTwistObjsInfo()
        # get twist ik objs 
        self.twistIkObjs = []
        splineIkObjs = cmds.ls(type="ikHandle")
        for loopObj in splineIkObjs:
            att = "%s.dTwistControlEnable"%loopObj
            if cmds.objExists(att):
                if cmds.getAttr(att) == True:
                    self.twistIkObjs.append(loopObj)
        # set ik twist to 0
        aToolsMod.saveInfoWithScene(self.STORE_NODE, self.MOTION_TRAIL_ATTR, self.twistIkObjs) 

        
    def disableTwistObjs(self):
        for loopObj in self.twistIkObjs:
            att = "%s.dTwistControlEnable"%loopObj
            cmds.setAttr(att, False)
        

    def reenableTwistObjs(self):
        for loopObj in self.twistIkObjs:
            att = "%s.dTwistControlEnable"%loopObj
            cmds.setAttr(att, True)
        
    def loadTwistObjsInfo(self):  
        loadInfo = aToolsMod.loadInfoWithScene(self.STORE_NODE, self.MOTION_TRAIL_ATTR)
        if loadInfo: 
            self.twistIkObjs = eval(loadInfo)
            # set ik twist back to 1
            self.reenableTwistObjs()
            aToolsMod.saveInfoWithScene(self.STORE_NODE, self.MOTION_TRAIL_ATTR, []) 

    
