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
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod
from aTools.commonMods import aToolsMod

import maya.OpenMaya as om

#============================================================================================================
class MicroTransform(object):    
    
    utilMod.killScriptJobs("G.microTransformScriptJobs")

    def __init__(self):
        
        G.deferredManager.removeFromQueue("MT_blinking")
        
        if G.aToolsBar.microTransform: return
        G.aToolsBar.microTransform = self
        
        self.attributes = ['translate', 'translateX','translateY','translateZ','rotate', 'rotateX', 'rotateY', 'rotateZ', 'scale', 'scaleX','scaleY','scaleZ']
        
        self.multiplierValues = [ {"name":"ultraSlow",  "value":.05
                                },{"name":"superSlow",  "value":.2
                                },{"name":"slow",       "value":.5
                                },{"name":"medium",     "value":1
                                }]
        self.defaultMultiplier          = "slow"
        self.microTransformStartTimer   = {}
        self.microTransformValues       = {}
        self.onOff                      = False
        self.rotationOrientMode         = cmds.manipRotateContext('Rotate', query=True, mode=True)
        
        self.setMultiplier(self.getMultiplier())
        self.removeMicroTransform()
        self.blinkingButton(self.onOff)
        
        
    def blinkingButton(self, onOff):
        
        if onOff:   G.aToolsBar.timeoutInterval.setInterval(self.toggleButtonActive, .3, id="MT_blinking")
        else:       G.aToolsBar.timeoutInterval.stopInterval("MT_blinking")
        

    def toggleButtonActive(self):
        onOff = "active" in cmds.iconTextButton("microTransformBtn", query=True, image=True)

        self.setButtonImg(not onOff)    
        
    def setButtonImg(self, onOff):
        if onOff:
            cmds.iconTextButton("microTransformBtn", edit=True, image=uiMod.getImagePath("specialTools_micro_transform_active"), highlightImage= uiMod.getImagePath("specialTools_micro_transform_active"))
        else:
            cmds.iconTextButton("microTransformBtn", edit=True, image=uiMod.getImagePath("specialTools_micro_transform"), highlightImage= uiMod.getImagePath("specialTools_micro_transform copy"))
         


    def switch(self):
        
        self.onOff  = (not self.onOff)
        self.setButtonImg(self.onOff) 
        self.blinkingButton(self.onOff)  
        self.setMode(self.onOff)
    
    
    def setMode(self, onOff):
        
        utilMod.killScriptJobs("G.microTransformScriptJobs")
                
        if onOff:
            
            self.rotationOrientMode         = cmds.manipRotateContext('Rotate', query=True, mode=True)
            cmds.manipRotateContext('Rotate', edit=True, mode=2)#gimbal
            #update values on turning on
            self.addMicroTransform()
            
            G.microTransformScriptJobs = []
            # get the current selected object values
            G.microTransformScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('SelectionChanged', self.addMicroTransform ))) 
            G.microTransformScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('timeChanged', self.updateValues )))
            G.microTransformScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('Undo', self.updateValues ))) 
            G.microTransformScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('Redo', self.updateValues ))) 
            G.microTransformScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('DragRelease', self.release ))) 
            

            
            #print "microTransform is ON."
            
        else:
            cmds.manipRotateContext('Rotate', edit=True, mode=self.rotationOrientMode)
            self.removeMicroTransform()
            #print "microTransform is OFF."
            
   
    def changedMicroTransform(self, msg, mplug, otherMplug, clientData):
        
        #cmds.undoInfo(stateWithoutFlush=False)
        
        
        if om.MNodeMessage.kAttributeSet == (om.MNodeMessage.kAttributeSet & msg) and not om.MGlobal.isUndoing() and not om.MGlobal.isRedoing():
            nodeName, attrName = mplug.name().split('.')
            
            #print "changed!"
            
            if attrName not in self.attributes: return            
            
            nodeAttr    = mplug.name()
            val         = cmds.getAttr(nodeAttr)                       
            mtValue     = self.microTransformValues["%s_%s"%(nodeName, attrName)]
            
            if str(val) != str(mtValue):
                #timer
                if "%s"%nodeName not in self.microTransformStartTimer: 
                    self.microTransformStartTimer["%s"%nodeName]    = cmds.timerX()
                microTransformTimer                                 = cmds.timerX(startTime=self.microTransformStartTimer["%s"%nodeName])
                self.microTransformStartTimer["%s"%nodeName]        = cmds.timerX()
                
                microTransformTimer *= 50
                if microTransformTimer == 0: microTransformTimer = 1000
                mult    = self.multiplier/microTransformTimer
                
                
                if mult >= self.multiplier: mult = self.multiplier
                
                    
                self.undoChunkFn("open")
                #print "changedMicroTransform"
                
                if type(val) is list:
            
                    temp        = ()
                    for n, loopVal in enumerate(val[0]):
                        dif     = loopVal-mtValue[0][n]
                        temp    = temp + (mtValue[0][n]+(dif*mult),)
                    newVal      = [temp]
            
                    self.microTransformValues["%s_%s"%(nodeName, attrName)]  = newVal
                    #xyz
                    self.microTransformValues["%s_%sX"%(nodeName, attrName)] = newVal[0][0]
                    self.microTransformValues["%s_%sY"%(nodeName, attrName)] = newVal[0][1]
                    self.microTransformValues["%s_%sZ"%(nodeName, attrName)] = newVal[0][2]
                    
                    eval("cmds.setAttr(nodeAttr, %s,%s,%s)"%(newVal[0][0],newVal[0][1],newVal[0][2]))
                    #xyz
                    cmds.setAttr("%sX"%nodeAttr, newVal[0][0])
                    cmds.setAttr("%sY"%nodeAttr, newVal[0][1])
                    cmds.setAttr("%sZ"%nodeAttr, newVal[0][2])
                    
                    
                else: 
                    dif     = val-mtValue
                    newVal  = mtValue+(dif*mult)
                    self.microTransformValues["%s_%s"%(nodeName, attrName)] = newVal
                    
                    #xyz inverse
                    val = cmds.getAttr("%s.%s"%(nodeName, attrName[:-1]))
                    self.microTransformValues["%s_%s"%(nodeName, attrName[:-1])] = val
                    
                    cmds.setAttr(nodeAttr, newVal)
                    
                
            else:
                self.microTransformValues["%s_%s"%(nodeName, attrName)] = cmds.getAttr(nodeAttr)
                if type(val) is list:
                    valX = cmds.getAttr("%s.%sX"%(nodeName, attrName))
                    valY = cmds.getAttr("%s.%sY"%(nodeName, attrName))
                    valZ = cmds.getAttr("%s.%sZ"%(nodeName, attrName))
                    #xyz
                    self.microTransformValues["%s_%sX"%(nodeName, attrName)] = valX
                    self.microTransformValues["%s_%sY"%(nodeName, attrName)] = valY
                    self.microTransformValues["%s_%sZ"%(nodeName, attrName)] = valZ
                
                else:                    
                    #xyz inverse
                    val = cmds.getAttr("%s.%s"%(nodeName, attrName[:-1]))
                    self.microTransformValues["%s_%s"%(nodeName, attrName[:-1])] = val
                        
                        
        #cmds.undoInfo(stateWithoutFlush=True)   
                 
    
    def release(self):        
        
        self.undoChunkFn("close")        
        self.updateValues()
        self.microTransformStartTimer    = {}
        
        
    def undoChunkFn(self, openClose):  
        if openClose == "open":
            if self.undoChunk == "closed": 
                cmds.undoInfo(openChunk=True)
                cmds.undoInfo(closeChunk=True)
                cmds.undoInfo(openChunk=True)
                cmds.undoInfo(closeChunk=True)
                cmds.undoInfo(openChunk=True)
                cmds.undoInfo(closeChunk=True)
                cmds.undoInfo(openChunk=True)
                self.undoChunk = "open"
                #print "openChunk"
        else:
            if self.undoChunk == "open":
                cmds.undoInfo(closeChunk=True)
                self.undoChunk = "closed"
                #print "closeChunk"


    def addMicroTransform(self): 
        
        self.updateValues()        
        cmds.undoInfo(stateWithoutFlush=False)
        
        
        sel = cmds.ls(selection=True)
                
        if G.MT_lastSel:
            graphEditorFocus = cmds.getPanel(withFocus=True) == "graphEditor1"
            if sel == G.MT_lastSel and graphEditorFocus: 
                cmds.undoInfo(stateWithoutFlush=True)
                return
            
        G.MT_lastSel = sel
        
        if len(sel) <= 0: 
            cmds.undoInfo(stateWithoutFlush=True)
            return
        
        self.removeMicroTransform()
        G.microTransformIds = []
        self.undoChunk      = "closed"        
        MSelectionList      = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(MSelectionList)        
        node                = om.MObject() 
        
        for n, loopSel in enumerate(sel):           
                   
            MSelectionList.getDependNode(n, node)
            clientData              = None
            G.microTransformIds.append(om.MNodeMessage.addAttributeChangedCallback(node, self.changedMicroTransform, clientData)) 
    
        cmds.undoInfo(stateWithoutFlush=True)
    
      
    
    def removeMicroTransform(self):  
        
        try:
            for loopId in G.microTransformIds:
                om.MNodeMessage.removeCallback(loopId)
        except: pass        
        
        G.microTransformIds = None  
        
        


            
    def updateValues(self):        
        #print "updateValues"
        
        self.microTransformValues    = {}        
        sel                     = cmds.ls(selection=True)        
             
        for loopSel in sel:            
            for loopAttr in self.attributes:
                val = cmds.getAttr("%s.%s"%(loopSel, loopAttr))
                self.microTransformValues["%s_%s"%(loopSel, loopAttr)] = val
    


    def setMultiplier(self, option):
        name = None
        for loopOption in self.multiplierValues:
            if loopOption["name"] == option:
                value = loopOption["value"]
                name  = loopOption["name"]
        
        if not name: #in case file is corrupt
            self.setMultiplier(self.defaultMultiplier)
            return
                
        self.multiplier = value
        aToolsMod.saveInfoWithUser("userPrefs", "microTransform", name)
    
    def getMultiplier(self):
        name                    = aToolsMod.loadInfoWithUser("userPrefs", "microTransform")            
        if name == None: name   = self.defaultMultiplier
        
        return name        

    
    def popupMenu(self, *args):        
        menu = cmds.popupMenu()
        cmds.popupMenu(menu, edit=True, postMenuCommand=self.populateMenu, postMenuCommandOnce=True)
   
        
    def populateMenu(self, menu, *args):

        cmds.radioMenuItemCollection(parent=menu)
        for loopOption in self.multiplierValues:
            radioSelected   = (self.multiplier == loopOption["value"])
            option          = loopOption["name"]
            cmds.menuItem (label=utilMod.toTitle(loopOption["name"]), radioButton=radioSelected, command=lambda x, option=option, *args: self.setMultiplier(option),  parent=menu)

        


