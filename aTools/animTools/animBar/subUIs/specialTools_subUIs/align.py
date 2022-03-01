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
from aTools.commonMods import utilMod
from aTools.commonMods import animMod

class Align(object):
    
    def __init__(self):
        
        if G.aToolsBar.align: return
        G.aToolsBar.align = self
        
    
    def popupMenu(self):
        cmds.popupMenu()
        cmds.menuItem(label="All Keys",                 command=self.alignAllKeys)
        cmds.menuItem( divider=True )
        cmds.menuItem(label="Align Position",           command=lambda *args: self.alignSelection(True, False))
        cmds.menuItem(label="Align Rotation",           command=lambda *args: self.alignSelection(False, True))
       
    
    def alignAllKeys(self, *args):
        self.alignSelection(translate=True, rotate=True, all=True)
        
    def alignSelection(self, translate=True, rotate=True, all=False):
        
        selection   = cmds.ls(selection=True)
        
        if len(selection) < 2: 
            cmds.warning("You need to select at least 2 objects.")
            return
        
        sourceObjs      = selection[0:-1]
        targetObj       = selection[-1]
        frames          = None
        currFrame       = cmds.currentTime(query=True) 
        getCurves       = animMod.getAnimCurves()
        animCurves      = getCurves[0]
        getFrom         = getCurves[1]
        showProgress    = all
        
        
        if animCurves:
            if all: keysSel = animMod.getTarget("keyTimes", animCurves, getFrom)
            else:   keysSel = animMod.getTarget("keysSel", animCurves, getFrom)
            
            frames  = utilMod.mergeLists(keysSel)
            
            if frames == []:
                 frames = [currFrame]   
        else:
            frames = [currFrame]
        
        self.align(sourceObjs, targetObj, frames, translate, rotate, showProgress, selectSorceObjs=True)
        
        
    def align(self, sourceObjs, targetObj, frames=None, translate=True, rotate=True, showProgress=False, selectSorceObjs=False):
        
        if not sourceObjs or not targetObj: return    
        
        cmds.refresh(suspend=True)
        
        currFrame   = cmds.currentTime(query=True) 
        constraints = []
        setValues   = []
        modes       = [] 
        status      = "aTools - Aligning nodes..."
        
        if translate:   modes.append({"mode":"translate", "constrain":"pointConstraint"})
        if rotate:      modes.append({"mode":"rotate",    "constrain":"orientConstraint"})
        
        if showProgress: utilMod.startProgressBar(status)
        
        if not frames: 
            getCurves   = animMod.getAnimCurves()
            animCurves  = getCurves[0]
            getFrom     = getCurves[1]
            
            
            if animCurves:
                keysSel = animMod.getTarget("keysSel", animCurves, getFrom)
                frames  = utilMod.mergeLists(keysSel)
    
                if frames == []:
                     frames = [currFrame]   
            else:
                frames = [currFrame]
    
        if showProgress:
            totalSteps      = len(sourceObjs + frames)           
            firstStep       = 0
            thisStep        = 0
            estimatedTime   = None
            startChrono     = None            
        
        
        #get values
        for thisStep, loopSourceObj in enumerate(sourceObjs):
            
            if showProgress: startChrono = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)   
                
            setValues.append({"modes":[], "values":[], "skips":[]})
            
            for loopMode in modes:
                                
                mode            = loopMode["mode"]
                constrainType   = loopMode["constrain"]
            
                allAttrs    = cmds.listAttr(loopSourceObj, settable=True, keyable=True)
                skip        = [loopXyz for loopXyz in ["x", "y", "z"] if "%s%s"%(mode, loopXyz.upper()) not in allAttrs]
                contrainFn  = eval("cmds.%s"%constrainType)
                
                with G.aToolsBar.createAToolsNode: constraints.append(contrainFn(targetObj, loopSourceObj, skip=skip)[0])
                                                
                setValues[-1]["modes"].append(mode)
                setValues[-1]["values"].append([cmds.getAttr("%s.%s"%(loopSourceObj, mode), time=loopKey)[0] for loopKey in frames])
                setValues[-1]["skips"].append(skip)
                
                
            if showProgress: estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
        
        #del constraints
        for loopConstrain in constraints: cmds.delete(loopConstrain) 
        
        for n, loopKey in enumerate(frames):
         
            if showProgress: 
                thisStep = thisStep + n + 1
                startChrono = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)
                
            for nn, loopSourceObj in enumerate(sourceObjs):
                loopSetValue = setValues[nn]
                values       = loopSetValue["values"] 
                skips        = loopSetValue["skips"]
                
                for nnn, loopMode in enumerate(modes):
                    mode    = loopMode["mode"]
                    xyz     = [loopXyz for loopXyz in ["x", "y", "z"] if loopXyz not in skips[nnn]]
 
                    
                    for nnnn, loopXyz in enumerate(xyz):
                        attr    = "%s%s"%(mode, loopXyz.upper())
                        value   = values[nnn][n][nnnn]
                        
                        if len(frames) > 1: 
                            cmds.setKeyframe(loopSourceObj, attribute=attr, time=(loopKey,loopKey), value=value)
                 
                        if currFrame == loopKey:    cmds.setAttr("%s.%s"%(loopSourceObj, attr), value)
                        
                #euler filter        
                if n == len(frames)-1 and rotate:
                    animCurves  = utilMod.mergeLists([cmds.keyframe(loopSourceObj, query=True, name=True) for loopSourceObj in sourceObjs])
                    animMod.eulerFilterCurve(animCurves) 

            if showProgress: estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)

        if showProgress: utilMod.setProgressBar(endProgress=True)
        if selectSorceObjs: cmds.select(sourceObjs)
        cmds.refresh(suspend=False)

  