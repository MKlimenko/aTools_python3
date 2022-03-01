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
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import utilMod
import importlib

def toggleframePlaybackRange(onOff):
    utilMod.killScriptJobs("G.framePlaybackRangeScriptJobs")
    
    if onOff:
        G.framePlaybackRangeScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False,  event =('ToolChanged',  framePlaybackRangeFn)) )
        G.framePlaybackRangeScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False,  event =('SelectionChanged',  framePlaybackRangeFn)) )
        
        framePlaybackRangeFn()
 
def getMinMax(rangeStart=None, rangeEnd=None):            
    
    displayNormalized = cmds.animCurveEditor( 'graphEditor1GraphEd', query=True, displayNormalized=True)
    if displayNormalized: return [-1.1, 1.1]  
   
    if not rangeStart:
        rangeStart  = cmds.playbackOptions(query=True, minTime=True)
        rangeEnd    = cmds.playbackOptions(query=True, maxTime=True)
    curvesShown = cmds.animCurveEditor( 'graphEditor1GraphEd', query=True, curvesShown=True)
    keysTimes   = []
    keysValues  = []
    keysShown   = []
    
    if curvesShown:
        for aCurve in curvesShown:
            kTimes = cmds.keyframe(aCurve, query=True, timeChange=True)
            if kTimes:
                keysTimes.extend(kTimes)
                keysValues.extend(cmds.keyframe(aCurve, query=True, valueChange=True))
                for n, key in enumerate(keysTimes):
                    if rangeStart <= key <= rangeEnd:
                        keysShown.append(keysValues[n])
        
        if not keysShown:
            keyMax = 0
            keyMin = 0
        else:                  
            keyMax = max(keysShown)
            keyMin = min(keysShown)
        
        total  = keyMax - keyMin
        if total == 0: total = 10
        border = total * .1
        
        return [keyMax+border, keyMin-border]
    else:
        return [0, 100]

def framePlaybackRangeFn(rangeStart=None, rangeEnd=None): 
    
    from aTools.commonMods import animMod; importlib.reload(animMod)
    animMod.filterNonAnimatedCurves()
    
    if not rangeStart:
        rangeStart  = cmds.playbackOptions(query=True, minTime=True) -1
        rangeEnd    = cmds.playbackOptions(query=True, maxTime=True) +1
    val         = getMinMax(rangeStart, rangeEnd)
    minVal      = val[0]
    maxVal      = val[1]
    
    cmds.animView('graphEditor1GraphEd', startTime=rangeStart, endTime=rangeEnd, minValue=minVal, maxValue=maxVal)
    
  
