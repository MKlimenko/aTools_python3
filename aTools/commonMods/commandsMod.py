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
import math
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import animMod
from aTools.commonMods import utilMod

from itertools import cycle

def toggleRotateMode():
    rot = cmds.manipRotateContext('Rotate', query=True, mode=True)
    
    # 0 = Local, 1 = Global, 2 = Gimbal
    if (rot == 0):
        cmds.manipRotateContext('Rotate', edit=True, mode=1)
    elif (rot == 1):
        cmds.manipRotateContext('Rotate', edit=True, mode=2)
    else:
        cmds.manipRotateContext('Rotate', edit=True, mode=0)

def toggleMoveMode():
    mov = cmds.manipMoveContext('Move', query=True, mode=True)
    
    # 0 = Local, 1 = Global, 2 = Gimbal
    if (mov == 0):
        cmds.manipMoveContext('Move', edit=True, mode=1)
    elif (mov == 1):
        cmds.manipMoveContext('Move', edit=True, mode=2)
    else:
        cmds.manipMoveContext('Move', edit=True, mode=0)

def orientMoveManip():
    selection   = cmds.ls(selection=True)
    
    if len(selection) < 2: 
        cmds.warning("You need to select at least 2 objects.")
        return
    
    sourceObjs  = selection[0:-1]
    targetObj   = selection[-1]
    orient      = cmds.xform(targetObj, query=True, ws=True, rotation=True)
    orientRad   = [math.radians(loopDeg) for loopDeg in orient]
    cmds.manipMoveContext('Move', edit=True, mode=6, orientAxes=orientRad)
    cmds.select(sourceObjs, replace=True)
    cmds.setToolTo("Move")
    
def cameraOrientMoveManip():
    selection   = cmds.ls(selection=True)    
    if len(selection) == 0: return
    
    shotCamera = animMod.getShotCamera()    
    if not shotCamera or not cmds.objExists(shotCamera): 
        cmds.warning("No shot camera detected.")
        return
    
    cmds.refresh(suspend=True)
    
    sourceObjs      = selection[0:-1]
    targetObj       = selection[-1]    
    locator         = animMod.createNull("tempCameraOrient_locator")
    cameraNode      = utilMod.getCamFromSelection([shotCamera])[0]
        
    G.aToolsBar.align.align([locator], targetObj, translate=True, rotate=False)   
    with G.aToolsBar.createAToolsNode: constraint = cmds.aimConstraint(cameraNode, locator, name="tempCameraOrient_constraint", aimVector=[0, 0, 1], worldUpType="objectrotation", worldUpObject=cameraNode, maintainOffset=False)[0]

    cmds.select(selection)
    cmds.select(locator, add=True)
    orientMoveManip()
  
    if cmds.objExists(locator):         cmds.delete(locator)
    if cmds.objExists(constraint):      cmds.delete(constraint)
    
    cmds.refresh(suspend=False)

def toggleObj(type):
    panelName   = cmds.getPanel(withFocus=True)
    value       = eval("cmds.modelEditor(panelName, query=True, %s=True)"%type[0])
    for loopType in type:
        eval("cmds.modelEditor(panelName, edit=True, %s=not value)"%loopType)

def togglePanelLayout():
    
    layouts     = ["graphEditor1", "persp"]
    currLayout  = getCurrentPanelLayout()
    
    licycle     = cycle(layouts)
    nextItem    = next(licycle)

    for loopItem in layouts:
        nextItem = next(licycle)
        if nextItem == currLayout: 
            nextItem = next(licycle)
            break
        
    setPanelLayout(nextItem)

def setPanelLayout(layout):
    
    if layout == "graphEditor1":
        mel.eval("setNamedPanelLayout \"Single Perspective View\";"+\
                 "scriptedPanel -e -rp modelPanel4 graphEditor1;")
    else:
        mel.eval("setNamedPanelLayout \"Single Perspective View\";"+\
                 "lookThroughModelPanel persp modelPanel4;")
    

def getCurrentPanelLayout():
    if "graphEditor1" in cmds.getPanel(visiblePanels=True):
        return "graphEditor1"
    else:
        return "persp"
    
    



    
    
def setSmartKey(time=None, animCurves=None, select=True, insert=True, replace=True, addTo=False):
    
    if not time: time   = animMod.getTimelineTime()    
    getFrom             = "timeline"
    
    if not animCurves:
        getCurves  = animMod.getAnimCurves()
        animCurves = getCurves[0]
        getFrom    = getCurves[1]
    
    
    if animCurves and getFrom != "timeline": 
        cmds.setKeyframe(animCurves, time=time, insert=insert)
        if select: cmds.selectKey(animCurves, replace=replace, addTo=addTo, time=time)
        
    else:
        objects = animMod.getObjsSel()
        if objects:
            
            channelboxSelObjs = animMod.channelBoxSel()
            if channelboxSelObjs:
                #objsAttrs     = ["%s.%s"%(loopObj, loopChannelboxSel) for loopObj in objects for loopChannelboxSel in channelboxSel]
                         
                #key selected attributes in the channelbox
                for n, loopObjAttr in enumerate(channelboxSelObjs):
                    prevKey       = cmds.findKeyframe(loopObjAttr, time=(time,time), which="previous")
                    tangentType   = cmds.keyTangent(loopObjAttr, query=True, outTangentType=True, time=(prevKey,prevKey)) 
               
                    if not tangentType: #if there is no key 
                        tangentType = cmds.keyTangent(query=True, g=True, outTangentType=True)
                        inTangentType  = tangentType[0].replace("fixed", "auto").replace("step", "auto")
                        outTangentType = tangentType[0].replace("fixed", "auto")
                        cmds.setKeyframe(loopObjAttr, time=time, insert=False, shape=False, inTangentType=inTangentType, outTangentType=outTangentType)
                        continue
                    
                    inTangentType  = tangentType[0].replace("fixed", "auto").replace("step", "auto")
                    outTangentType = tangentType[0].replace("fixed", "auto")
                
                    cmds.setKeyframe(loopObjAttr, time=time, insert=insert, shape=False, inTangentType=inTangentType, outTangentType=outTangentType)
                    
            else:
                #allChannels   = animMod.getAllChannels(objects)
                #objAttrs      = ["%s.%s"%(objects[n], loopAttr) for n, loopObj in enumerate(allChannels) for loopAttr in loopObj]
                prevKeys      = [cmds.findKeyframe(obj, time=(time,time), which="previous") for obj in objects]
                tangentTypes  = [cmds.keyTangent(obj, query=True, outTangentType=True, time=(prevKeys[n],prevKeys[n])) for n, obj in enumerate(objects)]
                #prevKeys      = [cmds.findKeyframe(obj, time=(time,time), which="previous") for obj in objAttrs]
                #tangentTypes  = [cmds.keyTangent(obj, query=True, outTangentType=True, time=(prevKeys[n],prevKeys[n])) for n, obj in enumerate(objAttrs)]
                #key all atributes
                cmds.setKeyframe(objects, time=time, insert=insert, shape=False) 
                #cmds.setKeyframe(objAttrs, time=time, insert=insert, shape=False)    
                            
                if insert: #will force create key if there is no key
                    for n, loopTangent in enumerate(tangentTypes):
                        if not loopTangent:
                            cmds.setKeyframe(objects[n], time=time, insert=False, shape=False)
                            #cmds.setKeyframe(objAttrs[n], time=time, insert=False, shape=False)
                        
                
                
                
                
def unselectChannelBox():
    currList = cmds.channelBox('mainChannelBox', query=True, fixedAttrList=True)
    cmds.channelBox('mainChannelBox', edit=True, fixedAttrList=[""])
    
    function = lambda *args:cmds.channelBox('mainChannelBox', edit=True, fixedAttrList=currList)
    G.deferredManager.sendToQueue(function, 1, "unselectChannelBox")

                
                
def goToKey(which, type="key"):
    cmds.undoInfo(stateWithoutFlush=False)    
    
    cmds.refresh(suspend=True)
    frame = cmds.findKeyframe(timeSlider=True, which=which) if type == "key" else cmds.currentTime(query=True) + (1 if which == "next" else -1)
    cmds.currentTime(frame)
    
    G.aToolsBar.timeoutInterval.removeFromQueue("goToKey")
    G.aToolsBar.timeoutInterval.setTimeout(animMod.refresh, sec=.05, id="goToKey")
    
    cmds.undoInfo(stateWithoutFlush=True)         
                
                
def selectOnlyKeyedObjects():
    
    getCurves   = animMod.getAnimCurves()
    animCurves  = getCurves[0]
    getFrom     = getCurves[1]
    
    if animCurves:
    
        keysSel      = animMod.getTarget("keysSel", animCurves, getFrom)
        objects      = animMod.getTarget("", animCurves, getFrom)[0]
        selObjs      = []

        
        for n, loopObj in enumerate(objects):
            if len(keysSel[n]) > 0:
                if not loopObj in selObjs:
                    selObjs.append(loopObj)
                    
        if len(selObjs) > 0: cmds.select(selObjs, replace=True)
                    

def cropTimelineAnimation():
    
    getCurves  = animMod.getAnimCurves()
    animCurves = getCurves[0]
    getFrom    = getCurves[1] 
    range      = animMod.getTimelineRange()  
        
    if animCurves:        
        keyTimes            = animMod.getTarget("keyTimes", animCurves, getFrom)
    
        for n, aCurve in enumerate(animCurves):
            
            firstKey = keyTimes[n][0]
            lastKey = keyTimes[n][-1]
            
           
            if range[0] >= firstKey: 
                cmds.cutKey(aCurve, time=(firstKey, range[0]-1), clear=True)
                
            if range[1] <= lastKey: 
                cmds.cutKey(aCurve, time=(range[1], lastKey), clear=True)        



def smartSnapKeys():
        
    getCurves       = animMod.getAnimCurves()
    animCurves      = getCurves[0]
    
    if not animCurves or len(animCurves) == 0: return
    
    getFrom         = getCurves[1]           
    keyTimes        = animMod.getTarget("keyTimes", animCurves, getFrom)  
    keysSel         = animMod.getTarget("keysSel", animCurves, getFrom)
    hasDecimalKeys  = False
        
    for loopKey in utilMod.mergeLists(keysSel):
        if loopKey != round(loopKey) > 0:
            hasDecimalKeys = True
            break
    
    if not hasDecimalKeys: return
      
    keyTangentsType = animMod.getTarget("keyTangentsType", animCurves, getFrom)
    firstStep       = 0
    totalSteps      = len(animCurves)
    estimatedTime   = None
    status          = "aTools - Smart Snap Curves..."
    startChrono     = None
    utilMod.startProgressBar(status)
    
    for thisStep, loopCurve in enumerate(animCurves):
        
        startChrono = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)
        
        if None in [keyTimes[thisStep], keysSel[thisStep]]: continue
        
        stepKeys        = [loopKey for nn, loopKey in enumerate(keyTimes[thisStep]) if loopKey != round(loopKey) and loopKey in keysSel[thisStep] and keyTangentsType[thisStep][nn][1] == "step"]
        linearKeys      = [loopKey for nn, loopKey in enumerate(keyTimes[thisStep]) if loopKey != round(loopKey) and loopKey in keysSel[thisStep] and keyTangentsType[thisStep][nn][1] == "linear"]
        decimalKeys     = [loopKey for nn, loopKey in enumerate(keyTimes[thisStep]) if loopKey != round(loopKey) and loopKey in keysSel[thisStep] and loopKey not in stepKeys + linearKeys]
        
        for loopKey in stepKeys:        cmds.snapKey(loopCurve, time=(loopKey, loopKey))
        for loopKey in linearKeys:      cmds.snapKey(loopCurve, time=(loopKey, loopKey))
        
        if len(decimalKeys) == 0: continue
        
        if not getFrom: 
            if cmds.keyframe(query=True, selected=True) != None: getFrom = "graphEditor"
        
        #inLinearKeys    = [round(loopKey) for nn, loopKey in enumerate(keyTimes[thisStep]) if keyTangentsType[thisStep][nn][0] == "linear"]
        #outLinearKeys   = [round(loopKey) for nn, loopKey in enumerate(keyTimes[thisStep]) if keyTangentsType[thisStep][nn][1] == "linear"]
        createKeys      = list(set([round(loopKey) for loopKey in decimalKeys]))
        selectKeys      = []
        
        #print "inlinearKeys", inLinearKeys, outLinearKeys  
        
        
        if getFrom == "graphEditor": 
            selectKeys  = list(set([round(loopKey) for loopKey in keysSel[thisStep] if round(loopKey) in createKeys]))
         
        for loopKey in createKeys:      cmds.setKeyframe(loopCurve, time=(loopKey, loopKey), insert=True)            
        for loopKey in selectKeys:      cmds.selectKey(loopCurve, addTo=True, time=(loopKey, loopKey))    
        for loopKey in decimalKeys:     cmds.cutKey(loopCurve, time=(loopKey, loopKey))        
        #for loopKey in outLinearKeys:   cmds.keyTangent(loopCurve, edit=True, time=(loopKey, loopKey), outTangentType="linear")
        #for loopKey in inLinearKeys:    cmds.keyTangent(loopCurve, edit=True, time=(loopKey, loopKey), inTangentType="linear")
        
        estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
    
    utilMod.setProgressBar(endProgress=True)
    
    
def scrubbingUndo(onOff):

    G.playBackSliderPython = G.playBackSliderPython or mel.eval('$aTools_playBackSliderPython=$gPlayBackSlider')
    pc = "from maya import cmds;"
    rc = "from maya import cmds;"
    
    if not onOff:
        pc += "cmds.undoInfo(stateWithoutFlush=False); "
        rc += "cmds.undoInfo(stateWithoutFlush=True); "
    
    pc += "cmds.timeControl('%s',edit=True,beginScrub=True)"%G.playBackSliderPython
    rc += "cmds.timeControl('%s',edit=True,endScrub=True)"%G.playBackSliderPython
    
    cmds.timeControl( G.playBackSliderPython, edit=True, pressCommand=pc, releaseCommand=rc)    
    
def topWaveform(onOff):
    G.playBackSliderPython  = G.playBackSliderPython or mel.eval('$aTools_playBackSliderPython=$gPlayBackSlider')
    onOff                   = 'top' if onOff else 'both'
    
    cmds.timeControl(G.playBackSliderPython, edit=True, waveform=onOff)     
    
def eulerFilterSelection():
    getCurves   = animMod.getAnimCurves()
    animCurves  = getCurves[0]
    
    animMod.eulerFilterCurve(animCurves) 
    

def setThreePanelLayout():     
    shotCamera = animMod.getShotCamera()
    if not shotCamera: shotCamera = "persp"
    mel.eval("toolboxChangeQuickLayoutButton \"Persp/Graph/Hypergraph\" 2;"+\
             #"ThreeTopSplitViewArrangement;"+\
             "lookThroughModelPanel %s hyperGraphPanel2;"%shotCamera+\
             "lookThroughModelPanel persp modelPanel4;")
             #"scriptedPanel -e -rp modelPanel2 graphEditor1;")
    viewports = [view for view in cmds.getPanel(type='modelPanel') if view in cmds.getPanel(visiblePanels=True)]
    defaultCameras = ['front', 'persp', 'side', 'top']
    
    for view in viewports:
        camera          = utilMod.getCamFromSelection([cmds.modelEditor(view, query=True, camera=True)])
        cameraTransform = camera[0]
        cameraShape     = camera[1]
    
        if cameraTransform in defaultCameras:
            utilMod.animViewportViewMode(view)
            
            if cameraTransform == "persp":
                cmds.camera(cameraTransform, edit=True, orthographic=False)
                cmds.setAttr("%s.nearClipPlane"%cameraShape, 1000)
                cmds.setAttr("%s.farClipPlane"%cameraShape, 10000000)
                cmds.setAttr("%s.focalLength"%cameraShape, 3500)
        else:
            utilMod.cameraViewMode(view)
            cmds.setAttr("%s.displayFilmGate"%cameraShape, 1)
            cmds.setAttr("%s.overscan"%cameraShape, 1)
            
                    
