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

# maya modules
from maya import cmds
from maya import mel
import math
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import utilMod
from aTools.commonMods import aToolsMod
from aTools.animTools import framePlaybackRange

G.lastCurrentFrame   = None
G.lastRange          = None
G.currNameSpace      = None

def getTarget(target, animCurves=None, getFrom=None, rangeAll=None):
    # object from curves, object selected, anim curves, attributes, keytimes, keys selected    
    
    if target == "keysSel" or target == "keysIndexSel":        
        if animCurves:              
            keysSel = []
            if getFrom == "graphEditor":               
                for node in animCurves:                
                    if target == "keysSel":         keysSel.append(cmds.keyframe(node, selected=True, query=True, timeChange=True))
                    if target == "keysIndexSel":    keysSel.append(cmds.keyframe(node, selected=True, query=True, indexValue=True))
            else:
                if rangeAll is None:               
                    timeline_range    = getTimelineRange() 
                    
                allKeys      = [cmds.keyframe(node, query=True, timeChange=True) for node in animCurves if cmds.objExists(node)]
                allIndexKeys = [cmds.keyframe(node, query=True, indexValue=True) for node in animCurves if cmds.objExists(node)]
                keysSel = []
                for n, loopKeyArrays in enumerate(allKeys):
                    keysSel.append([])
                    if loopKeyArrays:
                        for nn, loopKey in enumerate(loopKeyArrays):
                            
                            if rangeAll or timeline_range[0] <= loopKey < timeline_range[1]:
                                if target == "keysSel":         keysSel[n].append(loopKey)
                                if target == "keysIndexSel":    keysSel[n].append(allIndexKeys[n][nn])
                          
            return keysSel
               
    elif target == "keyTimes":        
        if animCurves:  
            keyTimes    = []            
            for node in animCurves:
                keyTimes.append(cmds.keyframe(node, query=True, timeChange=True))
                
            return keyTimes 
               
    elif target == "keyIndexTimes":        
        if animCurves:  
            keyIndexTimes    = []            
            for node in animCurves:
                keyIndexTimes.append(cmds.keyframe(node, query=True, indexValue=True))
                
            return keyIndexTimes  
               
    elif target == "keyValues":        
        if animCurves:  
            keyValues    = []            
            for node in animCurves: 
                keyValues.append(cmds.keyframe(node, query=True, valueChange=True))
                
            return keyValues 
               
    elif target == "currValues":        
        if animCurves:  
            keyValues    = []            
            for node in animCurves: 
                keyValues.append(cmds.keyframe(node, query=True, eval=True, valueChange=True)[0])
                
            return keyValues 
               
    elif target == "keyTangentsAngle":        
        if animCurves:  
            keyTangents    = []            
            for n, node in enumerate(animCurves):
                indexes = cmds.keyframe(node, query=True, indexValue=True)
                keyTangents.append([])
                for loopIndex in indexes:
                    keyTangents[n].append(cmds.keyTangent(node, query=True, index=(loopIndex,loopIndex),inAngle=True, outAngle=True))
                
            return keyTangents  
        
    elif target == "keyTangentsY":        
        if animCurves:  
            keyTangents    = []            
            for node in animCurves:
                keyTangents.append(cmds.keyTangent(node, query=True, iy=True, oy=True))
                
            return keyTangents  
        
    elif target == "keyTangentsX":        
        if animCurves:  
            keyTangents    = []            
            for node in animCurves:
                keyTangents.append(cmds.keyTangent(node, query=True, ix=True, ox=True))
                
            return keyTangents   
        
    elif target == "keyTangentsType":         
        if animCurves:  
            keyTangents    = []            
            for n, node in enumerate(animCurves):
                indexes = cmds.keyframe(node, query=True, indexValue=True)
                keyTangents.append([])
                for loopIndex in indexes:
                    keyTangents[n].append(cmds.keyTangent(node, query=True, index=(loopIndex,loopIndex),inTangentType=True, outTangentType=True))
                
            return keyTangents 
        
        
        
        
        
        
    else: # objFromCurves, attr 
        if animCurves:
            objs        = []
            attrs       = []
            
            for node in animCurves:
                if not cmds.objExists(node): continue
                for n in range(100): # find transform node (obj) and attribute name
                    obj  = None
                    attr = None
                    type = "animBlendNodeEnum"
                    while type == "animBlendNodeEnum": #skip anim layer nodes
                        if node is None: break
                        if cmds.objectType(node) == "animBlendNodeAdditiveRotation":
                            xyz = node[-1:]
                            node = cmds.listConnections("%s.output%s"%(node.split(".")[0], xyz), source=False, destination=True, plugs=True, skipConversionNodes=True)
                            if node is None:
                                continue
                            else:
                                node = node[0]
                        else:
                            node = cmds.listConnections("%s.output"%node.split(".")[0], source=False, destination=True, plugs=True, skipConversionNodes=True)
                            
                            if node is None:
                                continue
                            else:
                                node = node[0]
                        
                        type = cmds.nodeType(node)
            
                    if node is None: break    
                    obj = node.split(".")[0]
                    attr = node.split(".")[-1]                    
                    if type.find("animBlendNodeAdditive") == -1 and type != "animCurveTU": break
                
                   
                objs.append(obj)
                attrs.append(attr)
                
            return [objs, attrs]  


def getMirrorObjs(selObjs, side="both"):   
    
    MIRROR_PATTERN  = [["l", "r"], ["lf", "rt"], ["left", "right"]]
    SEPARATORS      = ["_", "-"]
    mirrorObjs      = []
    mirrorPatern    = []
    
    for loopPattern in MIRROR_PATTERN: #add uppercase and title to search
        mirrorPatern.append([loopPattern[0], loopPattern[1]])
        mirrorPatern.append([loopPattern[0].upper(), loopPattern[1].upper()])
        mirrorPatern.append([loopPattern[0].title(), loopPattern[1].title()])
    
    for loopObj in selObjs:
        if not loopObj: continue
        nameSpaceIndex = loopObj.find(":") + 1
        nameSpace      = loopObj[:nameSpaceIndex]
        objName        = loopObj[nameSpaceIndex:]
        mirrorObj      = objName
        sideDetected   = None
        
        for loopSeparator in SEPARATORS:
            mirrorObj = "%s%s%s"%(loopSeparator, mirrorObj, loopSeparator)
            
            for loopPattern in mirrorPatern:
                                
                leftPattern     = "%s%s%s"%(loopSeparator, loopPattern[0], loopSeparator)
                rightPattern    = "%s%s%s"%(loopSeparator, loopPattern[1], loopSeparator)
                
                if side == "both" or side == "left":
                    if not sideDetected or sideDetected == "left":
                        doReplace       = (mirrorObj.find(leftPattern) != -1)
                        if doReplace:
                            sideDetected = "left"
                            mirrorObj   = mirrorObj.replace(leftPattern, rightPattern)

                if side == "both" or side == "right":  
                    if not sideDetected or sideDetected == "right": 
                        doReplace       = (mirrorObj.find(rightPattern) != -1)
                        if doReplace:
                            sideDetected = "right"
                            mirrorObj   = mirrorObj.replace(rightPattern, leftPattern)
                        
            mirrorObj = mirrorObj[1:-1]
            
            
        if mirrorObj == objName: 
            mirrorObj = None
        else:
            mirrorObj = "%s%s"%(nameSpace, mirrorObj)
            
                            
        mirrorObjs.append(mirrorObj)
               
    return mirrorObjs




"""
def align(sourceObjs, targetObj, translate=True, rotate=True, suspend=True, onlyCurrFrame=True):
    
    startTime       = cmds.timer( startTimer=True)
    
    if not sourceObjs or not targetObj: return
    if suspend: cmds.refresh(suspend=True)
    
    currFrame   = cmds.currentTime(query=True) 
    currSel     = cmds.ls(selection=True)
    tempNull    = None
    
    if onlyCurrFrame: 
        keysSel = [currFrame]
    else:
        getCurves   = getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]
        
        
        if animCurves:
            keysSel = getTarget("keysSel", animCurves, getFrom)
            keysSel = utilMod.mergeLists(keysSel)    
            if keysSel == []:
                 keysSel = [currFrame]   
        else:
            keysSel = [currFrame]
    
    
    for loopKey in keysSel:                    
        if currFrame != loopKey: cmds.currentTime(loopKey)  
    
    
        
        if translate:
            translation = cmds.xform(targetObj, query=True, ws=True, rotatePivot=True)
        
        if rotate:
            rotation    = cmds.xform(targetObj, query=True, ws=True, rotation=True)
            orderMap    = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
            targetOrder = cmds.getAttr( targetObj+'.ro' ) 
    
    
        for loopSourceObj in sourceObjs:
        
            objOrder    = cmds.getAttr( loopSourceObj+'.ro' ) 
   
   
            if rotate:
                if targetOrder != objOrder:
                    if not tempNull: 
                        tempNull    = cmds.group(empty=True, world=True )
                   
                if tempNull != None:                
                    cmds.xform(tempNull, ws=True, absolute=False, rotateOrder=orderMap[targetOrder], rotation=rotation)
                    cmds.xform(tempNull, ws=True, absolute=False, rotateOrder=orderMap[objOrder], p = True)
                    
                    rotation       = cmds.xform(tempNull, query=True, ws=True, rotation=True)
                 
                cmds.xform(loopSourceObj, ws=True, rotation=rotation)
                cmds.xform(loopSourceObj, ws=True, rotation=rotation)#bug workaround
                
                
                
            if translate:     
                localPivot  = cmds.xform(loopSourceObj, query=True, os=True, rotatePivot=True)
                cmds.xform(loopSourceObj, ws=True, translation=(localPivot[0]*-1,localPivot[1]*-1,localPivot[2]*-1))
                globalPivot = cmds.xform(loopSourceObj, query=True, ws=True, rotatePivot=True)
                cmds.move(globalPivot[0]*-1,globalPivot[1]*-1,globalPivot[2]*-1, loopSourceObj, relative=True, worldSpace=True)
                cmds.move(translation[0],translation[1],translation[2], loopSourceObj, relative=True, worldSpace=True)
                
                #cmds.xform(loopSourceObj, ws=True, translation=translation)


    if tempNull != None and cmds.objExists(tempNull): 
        cmds.delete(tempNull)
        if len(currSel) > 0: cmds.select(currSel, replace=True)
    
    if suspend: 
        cmds.refresh(suspend=False)        
        #refresh()
        
    fullTime = cmds.timer( endTimer=True)
    print "timer: ", fullTime

"""

def createNull(locatorName="tmp"):
    
    with G.aToolsBar.createAToolsNode: newNull = cmds.spaceLocator(name=locatorName)[0]

    cmds.xform(cp=True)
    cmds.setAttr(".localScaleX", 0)
    cmds.setAttr(".localScaleY", 0)
    cmds.setAttr(".localScaleZ", 0)
    
    return newNull
    

def group(nodes=None, name="aTools_group", empty=True, world=False):
    with G.aToolsBar.createAToolsNode: 
        if nodes:   newGroup = cmds.group(nodes, empty=False, name=name, world=world)
        else:       newGroup = cmds.group(empty=empty, name=name, world=world)  
    return newGroup

def eulerFilterCurve(animCurves, filter="euler"):
    
    if animCurves:
        for loopCurve in animCurves:
                #euler filter
            if not isNodeRotate(loopCurve): continue 
            
            xyzCurves = ["%sX"%loopCurve[:-1], "%sY"%loopCurve[:-1], "%sZ"%loopCurve[:-1]]
            
            apply = True
            for loopXyzCurve in xyzCurves:
                if not cmds.objExists(loopXyzCurve):
                    apply = False
                    break
            
            if apply: cmds.filterCurve(xyzCurves, filter=filter)
    
   

def getObjsSel(): 
    return cmds.ls(sl=True)   

def getAngle(keyTimeA, keyTimeB, keyValA, keyValB):
    
    relTime    = keyTimeB - keyTimeA
    relVal     = keyValB - keyValA
    angle      = math.degrees(math.atan(relVal/relTime))
    #outOpp        = relTimeInA*math.tan(math.radians(outAngleA))
        
    return angle      

def getAnimCurves(forceGetFromGraphEditor=False):
        
        # get selected anim curves from graph editor
        animCurves       = cmds.keyframe(query=True, name=True, selected=True)
        #graphEditorFocus = cmds.getPanel(withFocus=True) == "graphEditor1"
        visiblePanels    = cmds.getPanel(visiblePanels=True)
        graphEditor      = None
        for loopPanel in visiblePanels:
            if loopPanel == "graphEditor1":
                graphEditor = True
                break
        getFrom          = "graphEditor"
        if not animCurves or not graphEditor and not forceGetFromGraphEditor: #get from timeline   
            getFrom = "timeline"  
            G.playBackSliderPython  = G.playBackSliderPython or mel.eval('$aTools_playBackSliderPython=$gPlayBackSlider')
            animCurves              = cmds.timeControl(G.playBackSliderPython, query=True, animCurveNames=True) 
            
        return [animCurves, getFrom]
    
def getTimelineRange(float=True):
    
    #if G.lastCurrentFrame == cmds.currentTime(query=True): return G.lastRange
        
    G.playBackSliderPython  = G.playBackSliderPython or mel.eval('$aTools_playBackSliderPython=$gPlayBackSlider')
    timeline_range                   = cmds.timeControl(G.playBackSliderPython, query=True, rangeArray=True)
    if float: timeline_range[1]      -= .0001
    #G.lastRange        = timeline_range
    #G.lastCurrentFrame = cmds.currentTime(query=True)
    
    return timeline_range    

def getTimelineTime():
    timelineTime = cmds.currentTime(query=True);  timelineTime = (timelineTime, timelineTime)
    return timelineTime



def refresh():
    cmds.undoInfo(stateWithoutFlush=False)
    #cmds.refresh(force=True)
    #print "refresh"
    cmds.refresh(suspend=False)
    cmds.currentTime(cmds.currentTime(query=True), edit=True)
    cmds.undoInfo(stateWithoutFlush=True) 

def isNodeRotate(node, xyz=None):
    
    isRotate      = False
    attr = "%s.output"%node.split(".")[0]
    type = cmds.getAttr(attr, type=True)
    #if type == "double3":
    if type == "doubleAngle":
        if xyz:
            if attr.find("rotate%s"%xyz.upper()) != -1 or (attr.find("Merged_Layer_input") != -1 and attr.find(xyz.upper()) != -1): 
                isRotate  = True 
        else:
            isRotate  = True 

            
    return isRotate

def isNodeTranslate(node, xyz=None):
    
    isTranslate      = False
    attr = "%s.output"%node.split(".")[0]
    type = cmds.getAttr(attr, type=True)
    
    if type == "doubleLinear":
        if xyz:
            if attr.find("translate%s"%xyz.upper()) != -1 or (attr.find("Merged_Layer_input") != -1 and attr.find(xyz.upper()) != -1): 
                isTranslate  = True 
        else:
            isTranslate  = True 
            
            
    return isTranslate

def isAnimCurveTranslate(aCurve):
    
    isTranslate      = False
    if aCurve.find("translate") != -1:
        isTranslate  = True 
            
    return isTranslate

def isAnimCurveRotate(aCurve):
    
    isRotate      = False
    if aCurve.find("rotate") != -1:
        isRotate  = True 
            
    return isRotate

def isAnimCurveScale(aCurve):
    
    isScale      = False
    if aCurve.find("scale") != -1:
        isScale  = True 
            
    return isScale

def channelBoxSel():
    
    channelsSel = []
    
    mObj            = cmds.channelBox('mainChannelBox', query=True, mainObjectList              =True)
    sObj            = cmds.channelBox('mainChannelBox', query=True, shapeObjectList             =True)
    hObj            = cmds.channelBox('mainChannelBox', query=True, historyObjectList           =True)
    oObj            = cmds.channelBox('mainChannelBox', query=True, outputObjectList            =True)
    mAttr           = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes      =True)
    sAttr           = cmds.channelBox('mainChannelBox', query=True, selectedShapeAttributes     =True)
    hAttr           = cmds.channelBox('mainChannelBox', query=True, selectedHistoryAttributes   =True)
    oAttr           = cmds.channelBox('mainChannelBox', query=True, selectedOutputAttributes    =True)
    
    if mObj and mAttr: channelsSel.extend(["%s.%s"%(loopObj, loopAttr) for loopObj in mObj for loopAttr in mAttr if cmds.objExists("%s.%s"%(loopObj, loopAttr))])
    if sObj and sAttr: channelsSel.extend(["%s.%s"%(loopObj, loopAttr) for loopObj in sObj for loopAttr in sAttr if cmds.objExists("%s.%s"%(loopObj, loopAttr))])
    if hObj and hAttr: channelsSel.extend(["%s.%s"%(loopObj, loopAttr) for loopObj in hObj for loopAttr in hAttr if cmds.objExists("%s.%s"%(loopObj, loopAttr))])
    if oObj and oAttr: channelsSel.extend(["%s.%s"%(loopObj, loopAttr) for loopObj in oObj for loopAttr in oAttr if cmds.objExists("%s.%s"%(loopObj, loopAttr))])
     
    return channelsSel
    

def getAllChannels(objs=None, changed=False, withAnimation=True):
    #startTime       = cmds.timer( startTimer=True)
    
    allChannels = []
    
    if not objs: objs = getObjsSel()
    
    for loopObj in objs:
        if not cmds.objExists(loopObj): continue
        isReference = False
        if changed: isReference = cmds.referenceQuery(loopObj, isNodeReferenced=True)
        
        #if not withAnimation:
            #cmds.listConnections(loopObj, source=True, destination=False, connections=True)
        
        allChannels.append(cmds.listAttr(loopObj, settable=True, keyable=True, locked=False, write=True, read=True, changedSinceFileOpen=isReference))
        #allChannels.append([loopAttr for loopAttr in cmds.listAttr(loopObj, settable=True, keyable=True, locked=False, write=True, read=True, changedSinceFileOpen=isReference) if cmds.getAttr("%s.%s"%(loopObj, loopAttr), settable=True)])
        
        
        
        shapes = cmds.listRelatives(loopObj, shapes=True, fullPath=True)
        if shapes:
            for loopShape in shapes:
                newChannel = cmds.listAttr(loopShape, userDefined=True, settable=True, keyable=True, locked=False, write=True, read=True)
                if newChannel and allChannels[-1]: 
                    allChannels[-1].extend(newChannel)         

    #fullTime = cmds.timer( endTimer=True)
    
                
    return allChannels  
"""
def getAllChannels(objs=None):
    startChrono    = cmds.timerX()
    total = 0
    allChannels = []
    if not objs: objs = getObjsSel()
    
    for loopObj in objs:
        attrList = cmds.listAttr(loopObj, keyable=True)
        allChannels.append([])
        if attrList:
            total += len(attrList)
            for loopAttr in attrList:
                
                if cmds.objExists("%s.%s"%(loopObj, loopAttr)):
                    if cmds.getAttr("%s.%s"%(loopObj, loopAttr), settable=True):
                        allChannels[-1].extend(loopAttr)
        shapes = cmds.listRelatives(loopObj, shapes=True)
        if shapes and allChannels[-1]:
            for loopShape in shapes:
                attrList = cmds.listAttr(loopShape, userDefined=True, keyable=True)
                if attrList:
                    for loopAttr in attrList:
                        if cmds.objExists("%s.%s"%(loopObj, loopAttr)):
                            if cmds.getAttr("%s.%s"%(loopObj, loopAttr), settable=True):
                                allChannels[-1].extend(loopAttr) 
                                total += len(loopAttr)               
    
    endChrono       = cmds.timerX(startTime=startChrono)
    print "taotal", total, endChrono          
    return allChannels       
"""    

def jumpToSelectedKey():
    
    frames = cmds.keyframe(query=True, selected=True)

    if frames:
        if frames[0] > 0:
            size = 0
            sum  = 0
            for loopFrame in frames:
                sum  += loopFrame
                size += 1
            average = sum / size
            cmds.currentTime(average)
        
def expandKeySelection(frames = 1):
    getCurves    = getAnimCurves()
    animCurves   = getCurves[0]
    getFrom      = getCurves[1]
    
    if animCurves:
    
        keysSel      = getTarget("keysSel", animCurves, getFrom)
        keyTimes     = getTarget("keyTimes", animCurves)
        
        # add tail and head keys
        for n, loopCurve in enumerate(animCurves):
            for key in keysSel[n]:
                index       = keyTimes[n].index(key)
                startIndex  = index-frames
                endIndex    = index+frames                
                if startIndex < 0: startIndex = 0
                
                cmds.selectKey(loopCurve, addTo=True, index=(startIndex, endIndex))   
        

def getShotCamera():
    STORE_NODE      = "tUtilities"
    CAMERA_ATTR     = "cameraSelected" 
    
    shotCamera      = aToolsMod.loadInfoWithScene(STORE_NODE, CAMERA_ATTR)

    if not shotCamera:
        cameras = utilMod.getAllCameras()
        if cameras:
            aToolsMod.saveInfoWithScene(STORE_NODE, CAMERA_ATTR, cameras[0])
            return cameras[0]
        
    return shotCamera
        

          
            
def filterNonAnimatedCurves():
    
    curvesShown = cmds.animCurveEditor( 'graphEditor1GraphEd', query=True, curvesShown=True)
    
    if curvesShown:
        objsAttrs = getTarget("", curvesShown)
        cmds.selectionConnection( 'graphEditor1FromOutliner', e=True, clear=True)        
        
        cmds.waitCursor(state=True)
        
        for n, loopCurve in enumerate(curvesShown):
            keyValues    = cmds.keyframe(loopCurve, query=True, valueChange=True)
            if max(keyValues) != min(keyValues):
                cmds.selectionConnection('graphEditor1FromOutliner', edit=True, select="%s.%s"%(objsAttrs[0][n], objsAttrs[1][n]))
            
        #framePlaybackRange.framePlaybackRangeFn()    
        cmds.waitCursor(state=False)
    
    
def getAnimData(animCurves=None, showProgress=None):   
    
    if animCurves is None:           
        getCurves    = getAnimCurves(True)
        animCurves   = getCurves[0]
        getFrom      = getCurves[1]
    else:    
        getFrom      = None
        
    if not animCurves: return
    
    if getFrom is None: keysSel = getTarget("keysSel", animCurves, getFrom, rangeAll=True)
    else:               keysSel = getTarget("keysSel", animCurves, getFrom)        
    
    if utilMod.isEmpty(keysSel): return
    
    if showProgress: utilMod.startProgressBar("aTools - Saving animation data...")
    
    objsAttrs       = getTarget("", animCurves=animCurves)
    objects         = objsAttrs[0]
    attributes      = objsAttrs[1]
    animData        = {"objects":objects, "animData":[]}        
    
    if showProgress:
        firstStep       = 0
        totalSteps      = len(animCurves)
        estimatedTime   = None
        status          = "aTools - Saving animation data..."
        startChrono     = None
    
    for thisStep, loopCurve in enumerate(animCurves):        
        
        if showProgress: startChrono = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)
        
        if objects[thisStep] is None:   continue            
        if len(keysSel[thisStep]) == 0: continue        
        
        weighted    = cmds.keyTangent(loopCurve, query=True, weightedTangents=True)
        if weighted is not None: weighted = weighted[0]
        objAttr     = "%s.%s"%(objects[thisStep], attributes[thisStep])
        infinity    = cmds.setInfinity(objAttr, query=True, preInfinite=True, postInfinite=True)
        
        animData["animData"].append({"objAttr":objAttr, "curveData":[weighted, infinity], "keyframeData":[], "tangentData":[]})            
        
        time            = (keysSel[thisStep][0], keysSel[thisStep][-1])
        timeChange      = cmds.keyframe(loopCurve, query=True, time=time, timeChange=True)
        valueChange     = cmds.keyframe(loopCurve, query=True, time=time, valueChange=True)
        breakdowns      = cmds.keyframe(loopCurve, query=True, time=time, breakdown=True)
        
        inTangentType   = cmds.keyTangent(loopCurve, query=True, time=time, inTangentType=True)
        outTangentType  = cmds.keyTangent(loopCurve, query=True, time=time, outTangentType=True)
        ix              = cmds.keyTangent(loopCurve, query=True, time=time, ix=True)
        iy              = cmds.keyTangent(loopCurve, query=True, time=time, iy=True)
        ox              = cmds.keyTangent(loopCurve, query=True, time=time, ox=True)
        oy              = cmds.keyTangent(loopCurve, query=True, time=time, oy=True)
        lock            = cmds.keyTangent(loopCurve, query=True, time=time, lock=True)
        weightLock      = cmds.keyTangent(loopCurve, query=True, time=time, weightLock=True)   
        
        for n, loopKey in enumerate(keysSel[thisStep]):
            breakdown       = (timeChange[n] in breakdowns) if breakdowns else []
            keyframe        = [timeChange[n], valueChange[n], breakdown]
            tangent         = [inTangentType[n], outTangentType[n], ix[n], iy[n], ox[n], oy[n], lock[n], weightLock[n]]
            
            animData["animData"][-1]["keyframeData"].append(keyframe)
            animData["animData"][-1]["tangentData"].append(tangent)
        
        if showProgress: estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
       
    if showProgress: utilMod.setProgressBar(endProgress=True)
        
    return animData

        

def applyAnimData(animData, pasteInPlace=True, onlySelectedNodes=False, showProgress=None, status=None): 
    
    if animData:   
        
        status      = "aTools - Applying animation data..." if not status else status
        objects     = animData["objects"]
                        
        if not onlySelectedNodes:
            #print "objects1", objects
            if len(objects) > 0: objects = [loopObj for loopObj in objects if loopObj is not None and cmds.objExists(loopObj)]
            #print "objects2", objects
            if len(objects) > 0: cmds.select(objects)        
        else:
            objects      = getObjsSel()
        
        if not objects: 
            cmds.warning("No objects to apply.")
            return
                
        cmds.refresh(suspend=True)
        if showProgress: utilMod.startProgressBar(status)
        
        if pasteInPlace:
            currKey  = cmds.currentTime(query=True) 
            for aData in animData["animData"]:
                allKeys         = []
                keys            = aData["keyframeData"]
                for n, key in enumerate(keys):
                    timeChange      = aData["keyframeData"][n][0]                        
                    allKeys.append(timeChange)
            
            firstKey = 0    
            if allKeys: 
                firstKey    = min(allKeys)
                lastKey     = max(allKeys)
                cutIn       = currKey+firstKey
                cuOut       = lastKey+firstKey
            
        else: 
            cutIn   = -49999
            cuOut   = 50000
            
   
        objsAttrs       = [loopItem["objAttr"] for loopItem in animData["animData"]]        
        existObjsAttrs  = [loopObjAttr for loopObjAttr in objsAttrs if cmds.objExists(loopObjAttr)]
                
        createDummyKey(existObjsAttrs)
        cmds.cutKey(existObjsAttrs, time=(cutIn, cuOut), clear=True)
        
        if showProgress:
            totalSteps      = 0            
            firstStep       = 0
            thisStep        = 0
            estimatedTime   = None
            startChrono     = None            
            
            for loopObjAttr in existObjsAttrs:  
                index           = objsAttrs.index(loopObjAttr)
                aData           = animData["animData"][index]
                keys            = aData["keyframeData"] 
                totalSteps      = totalSteps + len(keys)
        
        
        for loopObjAttr in existObjsAttrs: 
            
            index           = objsAttrs.index(loopObjAttr)
            aData           = animData["animData"][index]
            weighted        = aData["curveData"][0]
            infinity        = aData["curveData"][1]
            keys            = aData["keyframeData"] 
             
            
            for n, key in enumerate(keys):
                
                if showProgress: 
                    if cmds.progressBar(G.progBar, query=True, isCancelled=True ): 
                        refresh() 
                        utilMod.setProgressBar(endProgress=True)
                        return
                    startChrono = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)   
                
                #read values
                timeChange      = aData["keyframeData"][n][0]
                valueChange     = aData["keyframeData"][n][1]
                breakdown       = aData["keyframeData"][n][2]
                inTangentType   = aData["tangentData"][n][0]
                outTangentType  = aData["tangentData"][n][1]
                ix              = aData["tangentData"][n][2]
                iy              = aData["tangentData"][n][3]
                ox              = aData["tangentData"][n][4]
                oy              = aData["tangentData"][n][5]
                lock            = aData["tangentData"][n][6]
                weightLock      = aData["tangentData"][n][7]  
                
                if pasteInPlace: timeChange  = timeChange-firstKey+currKey                      
                
                time            = (timeChange,timeChange)                        
                
                # create key
                cmds.setKeyframe(loopObjAttr, time=time, value=valueChange, noResolve=True)
                
                if n == 0:
                    cmds.keyTangent(loopObjAttr, weightedTangents=weighted)
                    cmds.setInfinity(loopObjAttr, edit=True, preInfinite=infinity[0], postInfinite=infinity[1])
                
                if breakdown: cmds.keyframe(loopObjAttr, edit=True, time=time, breakdown=True)
                cmds.keyTangent(loopObjAttr,  time=time, ix=ix, iy=iy, ox=ox, oy=oy, lock=lock)
                if weighted: cmds.keyTangent(loopObjAttr, time=time, weightLock=weightLock)
                cmds.keyTangent(loopObjAttr,  time=time, inTangentType=inTangentType, outTangentType=outTangentType)
        
                if showProgress: estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
                thisStep += 1
        
        deleteDummyKey(existObjsAttrs)
            
        if showProgress: 
            refresh()
            utilMod.setProgressBar(endProgress=True)
            

        
def selectCtrlGroup(g):
    sel = cmds.ls(selection=True)
    if not sel and G.currNameSpace == None: 
        cmds.warning("Please select any controller.")
        return
    if sel: 
        nameSpaces = utilMod.getNameSpace(sel)
        G.currNameSpace = nameSpaces[0][0]
    
    cmds.select(clear=True)
    
    nameSpaceAndObjs = ["%s%s"%(G.currNameSpace, loopObj) for loopObj in g]
    
    cmds.select(nameSpaceAndObjs)

def setAttribute(obj, attr, value):
    
    sel = cmds.ls(selection=True)
    if not sel and G.currNameSpace == None: 
        cmds.warning("Please select any controller.")
        return
    if sel: 
        nameSpaces = utilMod.getNameSpace(sel)
        G.currNameSpace = nameSpaces[0][0]
    
    cmds.setAttr("%s%s.%s"%(G.currNameSpace, obj, attr), value)

def filterNoneObjects(objects):
    objs = []
    if objects:
        for loopObj in objects:
            if loopObj:
                if cmds.objExists(loopObj):
                    objs.append(loopObj)
                
    return objs

def createDummyKey(objects=None, select=False):
                
    objs = filterNoneObjects(objects)
    
    if len(objs) == 0: objs = getObjsSel()
    cmds.setKeyframe(objs, time=(-50000, -50000), insert=False)
    if select: cmds.selectKey(objs, replace=True, time=(-50000, -50000))
    
def deleteDummyKey(objects=None):
    
    objs = filterNoneObjects(objects)
    
    if not objs: objs = getObjsSel()
    if len(objs) > 0:
        cmds.cutKey(objs, time=(-50000, -50000), clear=True)
    
def getDefaultValue(node):
    
    type = cmds.nodeType(node)
    
    if "animCurve" in type: 
        target  = getTarget("", [node], "")        
        object  = target[0][0]
        attr    = target[1][0]
    else:
        object, attr = node.split(".")
    
    if not object: return 0
    
    isScale = isAnimCurveScale(node)
    if isScale: 
        value = 1
        return value
    
    
    value               = cmds.attributeQuery(attr, node=object, listDefault=True)
    if len(value) > 0:  value = value[0]
    else:               value = 0
        
    return value



def frameSection(nudge=24):
    
    
    curvesShown = cmds.animCurveEditor( 'graphEditor1GraphEd', query=True, curvesShown=True)    
    if not curvesShown: return
    
    
    
    
    
    firstSelKey = cmds.keyframe(selected=True, query=True, timeChange=True)
    #lastKey     = max(cmds.keyframe(selected=False, query=True, timeChange=True))
    lastKey     = cmds.playbackOptions(query=True, maxTime=True)  
    
    if firstSelKey: #if key is selected
        firstSelKey = min(firstSelKey)
    else:      
        #firstSelKey = min(cmds.keyframe(selected=False, query=True, timeChange=True))
        firstSelKey = cmds.playbackOptions(query=True, minTime=True) 
        
        try: 
            if G.AM_lastFrameSection + nudge < lastKey and G.AM_lastCurvesShown == curvesShown:
                        firstSelKey = G.AM_lastFrameSection + nudge
        except:
            pass
            
    
    G.AM_lastFrameSection = firstSelKey
    G.AM_lastCurvesShown  = curvesShown
    
    framePlaybackRange.framePlaybackRangeFn(rangeStart=(firstSelKey-1), rangeEnd=(firstSelKey+nudge+2))
    cmds.currentTime(firstSelKey, edit=True)


def getTokens(obj, att):
    objAttr     = "%s.%s"%(obj, att)
    enumTokens  = []
    
    if cmds.objExists(objAttr):
    
        enumFields  = None
        type        = cmds.getAttr(objAttr, type=True)
        if type == "enum":         
            if utilMod.isDynamic(obj, att):
                enumFields  = cmds.addAttr("%s.%s"%(obj, att), query=True, enumName=True)
    
        if enumFields:      enumTokens  = enumFields.split(":")

    return enumTokens













