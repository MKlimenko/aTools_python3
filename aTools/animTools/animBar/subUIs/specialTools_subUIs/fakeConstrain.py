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
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod

   
class FakeConstrain(object):    
    
    def __init__(self):
        self.copyCache          = []               
        self.locators           = []
        self.locatorGroup       = ""
        self.locatorGroupName   = "fakeConstrain_group"
        self.selection          = None
                
        
    def popupMenu(self):
        cmds.popupMenu(postMenuCommand=self.populateMenu)
    
    def populateMenu(self, menu, *args):
                    
        uiMod.clearMenuItems(menu)  
        
        if self.copyCache != []: 
            cmds.menuItem(label='Copy', command=self.copy, parent=menu)
            cmds.menuItem(label='Paste to All Frames' , command=lambda *args: self.paste('allFrames'), parent=menu)            
            cmds.menuItem(divider=True, parent=menu)    
        
        
        cmds.menuItem(label='Copy Relative to World' , command=self.copyWorld, parent=menu)  
        
    def copyPaste(self):
            
        if len(self.copyCache) > 0: self.paste()
        else: self.copy()
        
    def copy(self, *args):
        #print "copy"
        self.selection   = cmds.ls(selection=True)
        
        if len(self.selection) < 1: 
            cmds.warning("You need to select at least 2 objects.")
            return
        if len(self.selection) == 1:
            self.copyWorld()
            return
        
        if len(self.selection) > 20: 
            message         = "Too many objects selected, continue?"
            confirm         = cmds.confirmDialog( title='Confirm', message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if confirm != 'Yes': return  
        
        cmds.refresh(suspend=True)
        cmds.undoInfo(stateWithoutFlush=False)        
        self.flushCopyCache(force=True)        
        self.scriptJob()       
        
        self.sourceObjs = self.selection[0:-1]
        self.targetObj  = self.selection[-1] 
        selObjects      = utilMod.getNameSpace(self.selection)[1]                
        self.locators   = []
        
        self.locatorGroup = animMod.group(name=self.locatorGroupName)      
        G.aToolsBar.align.align([self.locatorGroup], self.targetObj)
        self.locators.append(self.locatorGroup) 
         
        
        for loopObj in self.sourceObjs:
            
            nameSpace       = utilMod.getNameSpace([loopObj])
            loopSelName     = "%s_%s"%(nameSpace[0][0], nameSpace[1][0]) 
            locatorName     = "fakeConstrain_%s"%loopSelName 
            
            locator = animMod.createNull(locatorName)            
            self.locators.append(locator)
            with G.aToolsBar.createAToolsNode: cmds.parent(locator, self.locatorGroup)            
            G.aToolsBar.align.align([locator], loopObj)
            
            matrix     = cmds.xform(locator, query=True, matrix=True)

            self.copyCache.append(matrix)
        
        self.clearLocators()
        
        cmds.select(self.selection)
        
        cmds.iconTextButton("fakeConstrainBtn", edit=True, image= uiMod.getImagePath("specialTools_fake_constrain_active"),         highlightImage= uiMod.getImagePath("specialTools_fake_constrain_active copy"))
       
        cmds.refresh(suspend=False)
        cmds.undoInfo(stateWithoutFlush=True)

    def copyWorld(self, *args):
        #print "copyworld"
        self.selection   = cmds.ls(selection=True)
        
        if len(self.selection) < 1: return
        
        if len(self.selection) > 20: 
            message         = "Too many objects selected, continue?"
            confirm         = cmds.confirmDialog( title='Confirm', message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if confirm != 'Yes': return  
        
        cmds.refresh(suspend=True)
        cmds.undoInfo(stateWithoutFlush=False)
        
        self.flushCopyCache(force=True)        
        self.scriptJob()       
        
        self.sourceObjs = self.selection
        self.targetObj  = "world"
        
        for loopObj in self.sourceObjs:        
            matrix     = cmds.xform(loopObj, query=True, ws=True, matrix=True)

            self.copyCache.append(matrix)

        
        cmds.iconTextButton("fakeConstrainBtn", edit=True, image= uiMod.getImagePath("specialTools_fake_constrain_active"),         highlightImage= uiMod.getImagePath("specialTools_fake_constrain_active copy"))
       
        cmds.refresh(suspend=False)
        cmds.undoInfo(stateWithoutFlush=True)

        
    def paste(self, type="onlyKeys"):
        
        cmds.refresh(suspend=True)        
            
        selObjects      = utilMod.getNameSpace(self.selection)[1]  
        self.locators   = []
        
        if self.targetObj != "world":
            #CREATE
            self.locatorGroup = animMod.group(name=self.locatorGroupName)   
             
            for n, loopObj in enumerate(self.sourceObjs):
                
                nameSpace       = utilMod.getNameSpace([loopObj])
                loopSelName     = "%s_%s"%(nameSpace[0][0], nameSpace[1][0]) 
                locatorName     = "fakeConstrain_%s"%loopSelName 
                
                locator = animMod.createNull(locatorName)            
                self.locators.append(locator)
                with G.aToolsBar.createAToolsNode: cmds.parent(locator, self.locatorGroup)   
               
            self.locators.append(self.locatorGroup)
        
        currFrame   = cmds.currentTime(query=True)
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]         
        
        if animCurves:
            keysSel = animMod.getTarget("keysSel", animCurves, getFrom)
            keysSel = utilMod.mergeLists(keysSel)    
            if keysSel == []:
                 keysSel = [currFrame]   
        else:
            keysSel = [currFrame]
        
        frames = keysSel
        
        if type == "allFrames":
            frameRange = animMod.getTimelineRange(float=False)
            frames = list(range(int(frameRange[0]),int(frameRange[1])))
            
        if self.targetObj != "world":
            G.aToolsBar.align.align([self.locatorGroup], self.targetObj, frames=frames)
                        
        for n, loopObj in enumerate(self.sourceObjs):
                 
            matrix     = self.copyCache[n]         
            
            if self.targetObj != "world":
                cmds.xform(self.locators[n], matrix=matrix)
                        
                G.aToolsBar.align.align([loopObj], self.locators[n], frames=frames, showProgress=True)
                
            else:
                for loopFrame in frames:
                    cmds.currentTime(loopFrame)          
                    cmds.xform(loopObj, ws=True, matrix=matrix)
                
                cmds.currentTime(currFrame)
                        
            for loopFrame in frames:
                for loopAttr in ["translate", "rotate"]:
                    breakdown = (loopFrame not in keysSel)
                    cmds.keyframe(loopObj, edit=True, attribute=loopAttr, time=(loopFrame, loopFrame), breakdown=breakdown)
        
            
        if self.targetObj != "world":
            self.clearLocators()     
            cmds.select(self.selection) 
        
        cmds.refresh(suspend=False)
        

    def clearLocators(self):        
    
        for loopLocator in self.locators:
            if cmds.objExists(loopLocator): cmds.delete(loopLocator)
                  
        if cmds.objExists(self.locatorGroup): cmds.delete(self.locatorGroup)
                
    def flushCopyCache(self, force=False):
        
        if not force and cmds.ls(selection=True) == self.selection:
            self.scriptJob()
            return
        
        cmds.iconTextButton("fakeConstrainBtn", edit=True, image= uiMod.getImagePath("specialTools_fake_constrain"),         highlightImage= uiMod.getImagePath("specialTools_fake_constrain copy"))
        
        self.clearLocators()
        self.copyCache = []
        
    def scriptJob(self):
        #scriptjob
        cmds.scriptJob(runOnce = True, killWithScene = True,  event =('SelectionChanged',  self.flushCopyCache))
        
