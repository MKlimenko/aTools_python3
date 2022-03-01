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
import os
import copy
import webbrowser
import urllib.request, urllib.error, urllib.parse

from maya       import OpenMaya
from datetime   import datetime, timedelta

from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
    
G.UM_timerMessage   = ""  



def getAllAnimCurves(selection=False):  
    if selection: 
        sel = cmds.ls(selection=True)
        if len(sel) == 0: return []
        return cmds.keyframe(sel, query=True, name=True) 
    return cmds.ls(type=["animCurveTA","animCurveTL","animCurveTT","animCurveTU"])

def onlyShowObj(types, panelName=None):   
    allTypes    = ["nurbsCurves", "nurbsSurfaces", "polymeshes", "subdivSurfaces", "planes", "lights", "cameras", "controlVertices", "grid", "hulls", "joints", "ikHandles", "deformers", "dynamics", "fluids", "hairSystems", "follicles", "nCloths", "nParticles", "nRigids", "dynamicConstraints", "locators", "manipulators", "dimensions", "handles", "pivots", "textures", "strokes"]
    if not panelName: panelName   = cmds.getPanel(withFocus=True)
    #views       = cmds.getPanel(type='modelPanel')
    #if panelName in views:
    if not cmds.modelEditor(panelName, exists=True): return
    cmds.modelEditor(panelName, edit=True, allObjects=True, displayAppearance="smoothShaded", displayTextures=True)
   
     # 
    for loopType in allTypes:
        if not loopType in types:
            eval("cmds.modelEditor(panelName, edit=True, %s=False)"%loopType)
        else:
            eval("cmds.modelEditor(panelName, edit=True, %s=True)"%loopType)
                
def cameraViewMode(panelName=None):
    if not panelName: panelName   = cmds.getPanel(withFocus=True)
    onlyShowObj(["polymeshes"], panelName)
    
    if (len(cmds.ls(type="light")) > 0): lights =  "all"
    else : lights = "default"
    cmds.modelEditor(panelName, edit=True, displayLights=lights, selectionHiliteDisplay=False)
   
    
def animViewportViewMode(panelName=None):
    if not panelName: panelName   = cmds.getPanel(withFocus=True)
    onlyShowObj(["nurbsCurves", "polymeshes", "manipulators"], panelName)
    cmds.modelEditor(panelName, edit=True, displayLights="default", selectionHiliteDisplay=True)

def getAllCameras():
    defaultCameras  = ['frontShape', 'perspShape', 'sideShape', 'topShape']
    cameras         = [cam for cam in cmds.ls(cameras=True) if cam not in defaultCameras]  
    return cameras 

def download(progBar, downloadUrl, saveFile):
    
    response = None
 
    try:
        response        = urllib.request.urlopen(downloadUrl, timeout=60)            
    except:
        pass
    
    if response is None: return
    
    
    fileSize        = int(response.info().getheaders("Content-Length")[0])
    fileSizeDl      = 0
    blockSize       = 128
    output          = open(saveFile,'wb')    
    
    cmds.progressBar( progBar,
                    edit=True,
                    beginProgress=True,
                    progress=0,
                    maxValue=100 )
    
    
    while True:
        buffer = response.read(blockSize)
        if not buffer:
            output.close()
            cmds.progressBar(progBar, edit=True, progress=100)             
            break
    
        fileSizeDl += len(buffer)
        output.write(buffer)
        p = float(fileSizeDl) / fileSize *100
        
        cmds.progressBar(progBar, edit=True, progress=p)  
        
    return output


  

def dupList(l):    
    return copy.deepcopy(l)

def timer(mode="l", function=""):
    
    if mode == "s":
        try: 
            startTime       = cmds.timer( startTimer=True)
            G.UM_timerMessage    = "startTime: %s\n"%startTime
            G.UM_timerLap        = 1
        except:
            pass
        
    elif mode == "l":
        try: 
            lapTime = cmds.timer( lapTime=True)
            G.UM_timerMessage += "lapTime %s: %s\n"%(G.UM_timerLap, lapTime)
            G.UM_timerLap     += 1
        except:
            pass
        
    elif mode == "e":
        try: 
            fullTime = cmds.timer( endTimer=True)
            G.UM_timerMessage += "Timer: %s took %s sec.\n"%(function, fullTime)
        except:
            pass
            
        print((G.UM_timerMessage))
            
        #cmds.timer( startTimer=True)
        #print (cmds.timer( endTimer=True))
        

def getRenderResolution():

    defaultResolution = "defaultResolution"
    width = cmds.getAttr(defaultResolution+".width")
    height = cmds.getAttr(defaultResolution+".height")

    return [width, height]





def mergeLists(lists):
    
    
    mergedList = []
    
    
    if lists:    
        for loopList in lists:
            if not loopList: continue
            for loopItem in loopList:
                if not loopItem in mergedList:
                    mergedList.append(loopItem)
                
    return mergedList

def listIntersection(list, sublist):    
    return list(filter(set(list).__contains__, sublist))

    

def getNameSpace(objects):
    
    nameSpaces  = []
    objectNames = []
    for loopObj in objects:
        
        nameSpaceIndex = loopObj.find(":") + 1
        nameSpace      = loopObj[:nameSpaceIndex]
        objName        = loopObj[nameSpaceIndex:]
        
        nameSpaces.append(nameSpace)
        objectNames.append(objName)
        
    return [nameSpaces, objectNames]

def listAllNamespaces():
    
    removeList = ["UI", "shared"]
    nameSpaces = list(set(cmds.namespaceInfo(listOnlyNamespaces=True))- set(removeList))
        
    if nameSpaces: nameSpaces.sort()
    
    return nameSpaces
    



def makeDir(directory):   
    if not os.path.exists(directory):
        try:
            os.makedirs(directory) 
        except:
            print(("Was not able to create folder: %s"%directory))
        

    
def listReplace(list, search, replace):
    newList = []
    for loopList in list:
        for n, loopSearch in enumerate(search):
            loopList = loopList.replace(loopSearch, replace[n])
            #if replaced != loopList: break
        newList.append(loopList)
            
            
    return newList

            
def killScriptJobs(jobVar):
    
    exec("%s = %s or []"%(jobVar, jobVar))
    
    jobs = eval(jobVar)
    #kill previous jobs    
    if jobs:
        for job in jobs:
            try:
                if cmds.scriptJob (exists = job):
                    cmds.scriptJob (kill = job)    
            except:
                Warning ("Job " + str(job) + " could not be killed!")
        jobs = []    
        
    exec("%s = %s"%(jobVar, jobs))


def getCurrentCamera():
    panel    = cmds.getPanel(withFocus=True)
    views    = cmds.getPanel(type='modelPanel')
    if panel in views:
        camera   = cmds.modelEditor(panel, query=True, camera=True)
        return camera


def getFolderFromFile(filePath, level=0):
    folderArray = filePath.split(os.sep)[:-1-level]
    newFolder = ""
    for loopFolder in folderArray:
        newFolder += loopFolder + os.sep
        
    return newFolder

def formatPath(path):
    path = path.replace("/", os.sep)
    path = path.replace("\\", os.sep)
    return path


def writeFile(filePath, contents):
    
    contentString = ""
    
    if contents != None:
        for loopLine in contents:
            contentString += "%s"%loopLine
    
    
    # write
    try:
        output = open(filePath, 'w')  # Open file for writing
        output.write(contentString)
        output.close()
    except:
        print(("aTools - Error writing file: %s"%filePath))

def readFile(filePath):   
    
    try:
        with open(filePath, 'r'):
            
            input = open(filePath, 'r')        # Open file for reading
            return input.readlines()           # Read entire file into a list of line strings
                    
    except IOError:
        return None
    
def toTitle(string):
    newString = ""
    for n, loopChar in enumerate(string):
        if n == 0:         
            newString += "%s"%loopChar.upper()
        elif loopChar.isupper() and not string[n-1].isupper() and not string[n-1] == " ":
            newString += " %s"%loopChar
        else:
            newString += "%s"%loopChar
    
    return newString.replace("_", " ")

def capitalize(string):
    spacers   = [" ", "_"]
    newString = ""
    cap = True
    for n, loopChar in enumerate(string):
        if cap: newString += loopChar.upper()
        else:   newString += loopChar
        cap = False
        if loopChar in spacers:
            cap = True
            
    return newString
                
def getUrl(url):
    webbrowser.open(url)
     





def loadDefaultPrefs(preferences, *args):
    for loopPref in preferences:
        name    = loopPref["name"]
        setPref(name, preferences, False, True)    

 
def isEmpty(list):
    try:
        return all(map(isEmpty, list))
    except TypeError:
        return False  

def startProgressBar(status="", isInterruptable=True):
    
    G.progBar       = G.progBar or mel.eval('$aTools_gMainProgressBar = $gMainProgressBar')
        
    cmds.progressBar( G.progBar,
                        edit=True,
                        beginProgress=True,
                        status=status,
                        isInterruptable=isInterruptable,
                        progress=0,
                        maxValue=100 )
   
    """
    cmds.progressWindow(title='Doing Nothing',
                        status=status,
                        isInterruptable=isInterruptable,
                        progress=0,
                        maxValue=100 )
    """

def setProgressBar(status=None, progress=None, endProgress=None):  
    G.progBar       = G.progBar or mel.eval('$aTools_gMainProgressBar = $gMainProgressBar')
    
    if status:      cmds.progressBar(G.progBar, edit=True, status=status)
    if progress:    cmds.progressBar(G.progBar, edit=True, progress=progress)
    if endProgress: cmds.progressBar(G.progBar, edit=True, endProgress=True)
    
        
 
def getMayaFileName(path=False):
    if path == "path": return cmds.file(query=True, sceneName=True)
    
    fileName        =  cmds.file(query=True, sceneName=True, shortName=True)
    if fileName:    shotName    = ".".join(fileName.split(".")[:-1])
    else:           shotName    = "Unsaved_shot"
        
    return shotName

def getCamFromSelection(sel):
    if len(sel) > 0:
        if "camera" in cmds.nodeType(sel[0], inherited=True):
            transformNode   = cmds.listRelatives(sel[0], parent=True)[0]
            shapeNode       = sel[0]
            
        elif cmds.nodeType(sel[0]) == "transform":
            transformNode   = sel[0]
            shapeNode       = cmds.listRelatives(sel[0], shapes=True)[0]
            
        return [transformNode, shapeNode]
        
def isAffected(nodeAffected, nodeDriver):
    
 
    driverFamily = cmds.ls(nodeDriver, dagObjects=True)
    if nodeAffected in driverFamily: return True
    
    nodeAffectedConnections = cmds.listHistory(nodeAffected)
    if nodeDriver in nodeAffectedConnections: return True
    
    
    
    
    steps1to3=set()
    steps1to3.update(steps1and3)
    step4=[]
    for each in (cmds.ls(list(steps1to3),shapes=True)):
       try:
           step4.extend(cmds.listConnections(each+'.instObjGroups', t='shadingEngine', et=1))
       except TypeError:
           pass
    steps1to3.update(step4)
    steps1to4=set()
    steps1to4.update(steps1to3)
    steps1to4.update(step4)
    step5=set(steps1to4)
    step5.update(cmds.listHistory(list(steps1to4)))
    print(step5)        
            
            
def getMObject(objectName):
    '''given an object name string, this will return the MDagPath api handle to that object'''
    sel = OpenMaya.MSelectionList()
    sel.add( str( objectName ) )
    obj = OpenMaya.MObject()
    sel.getDependNode(0,obj)

    return obj

def getMDagPath(nodeName):
    """
    Convenience function that returns a MDagPath for a given Maya DAG node.
    """
    selList = OpenMaya.MSelectionList()
    selList.add(nodeName)
    mDagPath = OpenMaya.MDagPath()
    selList.getDagPath(0, mDagPath)
    return mDagPath        
        
def isDynamic(object, attribute):
    
    MSelectionList  = OpenMaya.MSelectionList()
    MSelectionList.add(object)
    node            = OpenMaya.MObject() 
    MSelectionList.getDependNode(0, node)    
    fnThisNode      = OpenMaya.MFnDependencyNode(node)
    try:
        attr            = fnThisNode.attribute(attribute)
        plug            = OpenMaya.MPlug(node, attr)
    
        return plug.isDynamic()    
    except:
        pass
    
def formatTime(sec):
    sec = timedelta(seconds=int(sec))
    d   = datetime(1,1,1) + sec
    l   = ["day", "hour", "minute", "second"]        
    
    for loopL in l:
        t = eval("d.%s"%loopL)
        if loopL == "day": t -= 1
        if t > 0:
            if t > 1: loopL+= "s"
            return [t, loopL]
        
    return None    



def chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status):
    
    if not startChrono and thisStep == firstStep +1: startChrono    = cmds.timerX()
    
    if estimatedTime: 
        estimatedTimeSt = "%s %s"%(estimatedTime[0],estimatedTime[1]) 
        status          += " about %s remaining"%estimatedTimeSt
        
    p           = float(thisStep) / totalSteps * 100
    setProgressBar(status=status, progress=p)
    

    return startChrono


def chronoEnd(startChrono, firstStep, thisStep, totalSteps):
            
    if thisStep >= firstStep +2:
        endChrono       = cmds.timerX(startTime=startChrono)
        estimatedTime   = formatTime((((endChrono+1)/(thisStep+1))*totalSteps)-endChrono)
    
        return estimatedTime
    
    
def checkScriptJobEvents(onOff=True):    
    
    killScriptJobs("G.checkScriptJobEventsJobs")
    
    if onOff:          
        events = cmds.scriptJob(listEvents=True)
        ignore = ["idle", "idleHigh"]    
        
        for loopEvent in events: 
            if loopEvent not in ignore: 
                G.checkScriptJobEventsJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =(loopEvent, "print('Script Job Event: %s')"%loopEvent )))  

    
def hasInternet(url):
   try:
       proxy    = urllib.request.ProxyHandler({})
       opener   = urllib.request.build_opener(proxy)
       urllib.request.install_opener(opener)
       response = urllib.request.urlopen(url, timeout=60)
       return True
   except: pass
   return False

def deselectTimelineRange():  
    currSel = cmds.ls(selection=True)
    if len(currSel) == 0:
        cmds.select(G.A_NODE)
        cmds.select(None)
        
    else:    
        cmds.select(currSel)
        
def transferAttributes(fromNode, toNode):
                
    fromAttrs = {}

    for loopAttr in cmds.listAttr(fromNode):
        try: fromAttrs[loopAttr] = cmds.getAttr("%s.%s"%(fromNode, loopAttr))
        except: pass

    for loopAttr in list(fromAttrs.keys()):
        value    = fromAttrs[loopAttr]
        
        try: cmds.setAttr("%s.%s"%(toNode, loopAttr), value)
        except: pass
    
    
    

def getAllViewports():
    
    return [view for view in cmds.getPanel(type='modelPanel') if view in cmds.getPanel(visiblePanels=True) and view != "scriptEditorPanel1"]


def rangeToList(range):
    
    list  = []
    frame = range[0]
    
    while True:
        list.append(frame)
        frame += 1
        if frame > range[1]: break
    
    return list 

def getApiMatrix (matrix):
    
    mat = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList(matrix, mat)
    
    return mat