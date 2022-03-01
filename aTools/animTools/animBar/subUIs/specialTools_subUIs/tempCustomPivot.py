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
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod
from aTools.commonMods import aToolsMod

import maya.OpenMaya as om

#============================================================================================================
class TempCustomPivot(object):    

    def __init__(self):
        self.STORE_NODE    = "tempCustomPivot"
        self.CONSTRAINTS   = "constraintObjects"
        self.LOCATORS      = "locatorObjects"
        self.CTRLS         = "ctrlsObjects"
        self.CURRENTFRAME  = "currentFrame"
        self.sel           = []
        self.deniedCtx     = ["dragAttrContext", "manipMoveContext", "manipRotateContext", "manipScaleContext"]
                
        self.clear()

    def popupMenu(self, *args):
        cmds.popupMenu()
        cmds.menuItem(label="Clear temporary custom pivots", command=self.clear)
         

    def create(self, *args):
        
        
        img = cmds.iconTextButton("TempCustomPivotBtn", query=True, image=True)
        onOff = (img[-10:-4] == "active")
        if onOff: 
            self.clear()
            cmds.select(self.sel)
            return
        
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        
        self.clear()       
        
        
        getCurves  = animMod.getAnimCurves()
        animCurves = getCurves[0]
        getFrom    = getCurves[1] 
        
        if animCurves:        
            keyTimes            = animMod.getTarget("keyTimes", animCurves, getFrom)
              
        self.sel = cmds.ls(selection=True)
        if not self.sel: return
                
        cmds.iconTextButton("TempCustomPivotBtn", edit=True, image= uiMod.getImagePath("specialTools_create_temp_custom_pivot_active"),         highlightImage= uiMod.getImagePath("specialTools_create_temp_custom_pivot_active"))
       
        targetObj  = self.sel[-1]  
        aToolsMod.saveInfoWithScene(self.STORE_NODE, self.CTRLS, self.sel)
        
        currentFrame = cmds.currentTime(query=True) 
        aToolsMod.saveInfoWithScene(self.STORE_NODE, self.CURRENTFRAME, currentFrame)
        
        locators = []
        for loopSel in self.sel: 
            nameSpace       = utilMod.getNameSpace([loopSel])
            loopSelName     = "%s_%s"%(nameSpace[0][0], nameSpace[1][0])  
            locatorName     = "tempCustomPivot_%s"%loopSelName
            
            locator = animMod.createNull(locatorName)
            locators.append(locator)
        
            G.aToolsBar.align.align([locator], loopSel)
        
            
        locatorGroup = "tempCustomPivot_group"
        animMod.group(name=locatorGroup)        
        G.aToolsBar.align.align([locatorGroup], targetObj)
        with G.aToolsBar.createAToolsNode: cmds.parent(locators, locatorGroup)
        cmds.select(locatorGroup, replace=True)
        
        locators.append(locatorGroup)   
        
        aToolsMod.saveInfoWithScene(self.STORE_NODE, self.LOCATORS, locators)
     
        #parent ctrls to locator
        constraints = ["%s_tempCustomPivot_constraint"%loopConstraint for loopConstraint in self.sel]
        
        aToolsMod.saveInfoWithScene(self.STORE_NODE, self.CONSTRAINTS, constraints)
        
        for n, loopSel in enumerate(self.sel):
            with G.aToolsBar.createAToolsNode: cmds.parentConstraint(locators[n], loopSel, name=constraints[n], maintainOffset=True)
            constraintNode = "%s.blendParent1"%loopSel
            if not cmds.objExists(constraintNode): continue
            cmds.setKeyframe(constraintNode)
            if keyTimes:
                for loopTime in keyTimes[0]:
                    cmds.setKeyframe("%s.tx"%locatorGroup, time=(loopTime,loopTime))
                    if loopTime != currentFrame:
                        cmds.setKeyframe(constraintNode, time=(loopTime,loopTime), value=0)
        
        #enter edit mode
        cmds.setToolTo(cmds.currentCtx())
        cmds.ctxEditMode()
        
        #scriptjob    
        cmds.scriptJob(runOnce = True, killWithScene = True,  event =('SelectionChanged',  self.scriptJob_SelectionChanged))
        
    def scriptJob_SelectionChanged(self):
        self.clear()
        cmds.undoInfo(closeChunk=True)
    
    def clear(self, *args):
        
        
        if cmds.iconTextButton("TempCustomPivotBtn", query=True, exists=True):
            cmds.iconTextButton("TempCustomPivotBtn", edit=True, image= uiMod.getImagePath("specialTools_create_temp_custom_pivot"),         highlightImage= uiMod.getImagePath("specialTools_create_temp_custom_pivot copy"))
               
        cmds.refresh(suspend=True)
        
        currFrame = cmds.currentTime(query=True) 
        
        loadConstraints = aToolsMod.loadInfoWithScene(self.STORE_NODE, self.CONSTRAINTS)
        loadLocators    = aToolsMod.loadInfoWithScene(self.STORE_NODE, self.LOCATORS)
        loadCtrls       = aToolsMod.loadInfoWithScene(self.STORE_NODE, self.CTRLS)
        currentFrame    = aToolsMod.loadInfoWithScene(self.STORE_NODE, self.CURRENTFRAME)
        
        #exit edit mode
        
        if cmds.currentCtx() not in self.deniedCtx: cmds.setToolTo(cmds.currentCtx())
        
        
        if currentFrame:
            cmds.currentTime(eval(currentFrame))
        
        #get values
        """
        translation = []
        rotation    = []
        if loadCtrls: 
            ctrlObjs    = eval(loadCtrls)
            for loopCtrl in ctrlObjs:
                translation.append(cmds.xform(loopCtrl, query=True, ws=True, rotatePivot=True))
                rotation.append(cmds.xform(loopCtrl, query=True, ws=True, rotation=True))
        """        
        
        
        if loadConstraints: 
            constraintObjs = eval(loadConstraints)
            for loopConstraint in constraintObjs:
                if cmds.objExists(loopConstraint): cmds.delete(loopConstraint)
                
        if loadCtrls and loadLocators: 
            locatorObjs = eval(loadLocators)
            ctrlObjs    = eval(loadCtrls)
            for n, loopCtrl in enumerate(ctrlObjs):
                if cmds.objExists(loopCtrl) and cmds.objExists(locatorObjs[n]):
                    G.aToolsBar.align.align([loopCtrl], locatorObjs[n]) 
        
            for loopLocator in locatorObjs:
                if cmds.objExists(loopLocator): cmds.delete(loopLocator)
        
        cmds.currentTime(currFrame)    
        cmds.refresh(suspend=False)
        

   

