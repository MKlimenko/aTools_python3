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


def togglejumpToSelectedKey(onOff):
    utilMod.killScriptJobs("G.jumpToSelectedKeyScriptJobs")
    
    if onOff:
        G.jumpToSelectedKeyScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False,  event =('SelectionChanged',  animMod.jumpToSelectedKey)) )

        animMod.jumpToSelectedKey()

def getMinMax():            
          
    rangeStart  = cmds.playbackOptions(query=True, minTime=True)
    rangeEnd    = cmds.playbackOptions(query=True, maxTime=True)
    curvesShown = cmds.animCurveEditor( 'graphEditor1GraphEd', query=True, curvesShown=True)
    keysTimes   = []
    keysValues  = []
    keysShown   = []
    
    if curvesShown:
        for aCurve in curvesShown:
            keysTimes.extend(cmds.keyframe(aCurve, query=True, timeChange=True))
            keysValues.extend(cmds.keyframe(aCurve, query=True, valueChange=True))
            for n, key in enumerate(keysTimes):
                if rangeStart <= key <= rangeEnd:
                    keysShown.append(keysValues[n])
                    
        keyMax = max(keysShown)
        keyMin = min(keysShown)
        total  = keyMax - keyMin
        if total == 0: total = 1
        border = total * .1
        
        return [keyMax+border, keyMin-border]
    else:
        return [0, 100]


