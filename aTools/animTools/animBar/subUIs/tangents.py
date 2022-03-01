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
from aTools.commonMods import uiMod
from aTools.commonMods import animMod
from aTools.commonMods import utilMod



class Tangents_Gui(uiMod.BaseSubUI):
        
    def createLayout(self):
        
        tangents    = Tangents()
        buttons     = ["flow", "bounce", "auto", "spline", "linear", "flat", "step"]
        
        cmds.rowLayout(numberOfColumns=8, parent=self.parentLayout)
        
        for loopButton in buttons:
            cmds.iconTextButton(style='iconAndTextVertical', image= uiMod.getImagePath("tangents_%s"%loopButton),   highlightImage= uiMod.getImagePath("tangents_%s copy"%loopButton),   w=self.wb, h=self.hb, command=lambda loopButton=loopButton, *args: tangents.setTangent(loopButton),             annotation="%s tangent\\nRight click for options"%str.title(loopButton))
            tangents.popupMenu(loopButton)
            
# end createLayout

class Tangents(object):
    
    def __init__(self):        
        if G.aToolsBar.tangents: return
        G.aToolsBar.tangents = self

    def popupMenu(self, button, *args):        
        menu = cmds.popupMenu()
        cmds.popupMenu(menu, edit=True, postMenuCommand=lambda *args:self.populateMenu(menu, button), postMenuCommandOnce=True)
   
        
    def populateMenu(self, menu, button, *args):

        print(("menu, button, *args", menu, button, args))
        
        
        if button != "step":
            cmds.menuItem(label='In Tangent',       command=lambda *args: self.setTangent(button, 'in'),                parent=menu)
            cmds.menuItem(label='Out Tangent',      command=lambda *args: self.setTangent(button, 'out'),               parent=menu)
            cmds.menuItem(divider=True, parent=menu)
            cmds.menuItem(label='First Frame',      command=lambda *args: self.setTangent(button, 'out', 'first'),      parent=menu)
            cmds.menuItem(label='Last Frame',       command=lambda *args: self.setTangent(button, 'in', 'last'),        parent=menu)
            cmds.menuItem(label='Both Ends',        command=lambda *args: self.setTangent(button, 'inOut', 'both'),     parent=menu)

        cmds.menuItem(divider=True, parent=menu)
        cmds.menuItem(label='All Keys',             command=lambda *args: self.setTangent(button, 'inOut', 'all'),     parent=menu)
        

        

    def flowAround(self, frames = 2, excludeCurrKey = False):
        
        getCurves  = animMod.getAnimCurves()
        animCurves = getCurves[0]
        getFrom    = getCurves[1] 
        
        if animCurves:
            #if getFrom == "graphEditor":
            keysSel      = animMod.getTarget("keysSel", animCurves, getFrom)
            tangentType  = "flow"
            time         = None
                
            #animMod.expandKeySelection(frames)  
            
            index        = animMod.getTarget("keysIndexSel", animCurves, getFrom)
            indexTimes   = animMod.getTarget("keyIndexTimes", animCurves, getFrom)
            
            #expand selection
            for n, loopCurve in enumerate(index):
                for x in range(frames):
                    if loopCurve[0] >= 1:
                        loopCurve.insert(0, loopCurve[0]-1)
                    if loopCurve[-1] < indexTimes[n][-1]:
                        loopCurve.append(loopCurve[-1]+1)
                
                #if excludeCurrKey:
                        
                
            
            self.applyTangent(animCurves, tangentType, getFrom, time, index)   
            
            #select back keys
            if keysSel:
                cmds.selectKey(clear=True)
                for n, aCurve in enumerate(animCurves):
                    for key in keysSel[n]:
                        cmds.selectKey(aCurve, addTo=True, time=(key, key))   
             
    def applyTangent(self, animCurves, tangentType, getFrom, time, index, tangentInOut="inOut"):
        
        
         
        if self.isDefaultTangent(tangentType): #default maya tangents
            if tangentType == "step":
                cmds.keyTangent(animCurves, edit=True, time=time, outTangentType=tangentType)
                
            else:
                if tangentInOut =="inOut" or tangentInOut == "in":
                    #print "applied in", time, tangentType
                    cmds.keyTangent(animCurves, edit=True, time=time, inTangentType=tangentType)
                if tangentInOut =="inOut" or tangentInOut == "out":
                    #print "applied out", time, tangentType
                    cmds.keyTangent(animCurves, edit=True, time=time, outTangentType=tangentType)
                
        else: #custom tangents   
            
                 
            
            keyTimes      = animMod.getTarget("keyTimes", animCurves)
            keyIndexTimes = animMod.getTarget("keyIndexTimes", animCurves)
            keysIndexSel  = index
            keyValues     = animMod.getTarget("keyValues", animCurves)
                    
         
            cycleArray    = []
            tangentArray  = []
           
            for n, aCurve in enumerate(animCurves):     
                cycleArray.append([]) 
                tangentArray.append([])    
                    
                if keysIndexSel != None and keyTimes[n] != None and keysIndexSel[n] != None and len(keyTimes[n]) >=2:
                    
                    if keyValues[n][0] == keyValues[n][-1] and keysIndexSel[n] == keyIndexTimes[n]: #it's a cycle
                        cycleArray[n] = True          
                    else:
                        cycleArray[n] = False
                    
                    #define tangent array
                    for i in keysIndexSel[n]:                        
                        tangentArray[n].append(cmds.keyTangent(aCurve, query=True, index=(i, i), inTangentType=True, outTangentType=True, inAngle=True, outAngle=True))
                    
                 
            passes = [self.averageTangent, self.flowTangent]
            #passes = [averageTangent]
            #self.fixTangentOvershoot, self.fixTangentOpposite
            self.applyPass(passes, animCurves, keyTimes, keyValues, keysIndexSel, tangentType)
            
            
            
               
            # put back saved in out sides
            for n, aCurve in enumerate(animCurves):
                
                if keysIndexSel != None and keyTimes[n] != None and keysIndexSel[n] != None and len(keyTimes[n]) >=2:
                                                                           
                    for nn, i in enumerate(keysIndexSel[n]):
                        
                        tangent = tangentArray[n][nn]
                       
                        if tangentInOut == "in":
                            cmds.keyTangent(aCurve, edit=True, index=(i, i), lock=False)
                            cmds.keyTangent(aCurve, edit=True, index=(i, i), outTangentType=tangent[3], outAngle=tangent[1])
                            cmds.keyTangent(aCurve, edit=True, index=(i, i), lock=True)
    
                        elif tangentInOut == "out":
                            cmds.keyTangent(aCurve, edit=True, index=(i, i), lock=False)
                            cmds.keyTangent(aCurve, edit=True, index=(i, i), inTangentType=tangent[2], inAngle=tangent[0]) 
                            cmds.keyTangent(aCurve, edit=True, index=(i, i), lock=True) 
            
            
            
            if tangentType == "flow": 
                # bounce ends
             
                for n, aCurve in enumerate(animCurves):
                    first = None
                    last  = None
                    
                    if 0 in keysIndexSel[n]:                    first = True
                    if len(keyTimes[n])-1 in keysIndexSel[n]:   last  = True
                    
                    if first and last:
                        self.bounceEnds([aCurve], "bounce", getFrom, tangentInOut, [keyTimes[n]], [keyIndexTimes[n]], "both")
                    elif first:  
                        self.bounceEnds([aCurve], "bounce", getFrom, tangentInOut, [keyTimes[n]], [keyIndexTimes[n]], "first")
                    elif last:
                        self.bounceEnds([aCurve], "bounce", getFrom, tangentInOut, [keyTimes[n]], [keyIndexTimes[n]], "last")
                        
                    #print "fl", first, last
                        
                # cycle?                
                for n, aCurve in enumerate(animCurves):
                    if cycleArray[n]:
                        angle = cmds.keyTangent(aCurve, query=True, index=(0, 0), outAngle=True)[0]
                        cmds.keyTangent(aCurve, time=(keyTimes[n][-1], keyTimes[n][-1]), inAngle=angle, outAngle=angle)
                    
        
                    
                    
    def applyPass(self, passes, animCurves, keyTimes, keyValues, keysIndexSel, tangentType):
        
        
        
        newKeysIndexSel = utilMod.dupList(keysIndexSel)
        
        for loopFunction in passes:
            
            #utilMod.timer("s")
            
            for n, aCurve in enumerate(animCurves):  
                                  
                if keysIndexSel != None and keyTimes[n] != None and keysIndexSel[n] != None and len(keyTimes[n]) >=2:
                    
                    #utilMod.timer()
                    
                    #unlock weights
                    weighted = cmds.keyTangent(aCurve, query=True, weightedTangents=True)[0]
                    locked   = cmds.keyTangent(aCurve, query=True, lock=True)
                    
                    #utilMod.timer() 
                    
                    if weighted: cmds.keyTangent(aCurve, edit=True, weightedTangents=False) #weight to balance in and out tangents
                    cmds.keyTangent(aCurve, edit=True, weightedTangents=True)
                        
                    #utilMod.timer()  
                    
                    if loopFunction == self.fixTangentOpposite:
                        #remove last index
                        if len(keysIndexSel[n]) > 0: keysIndexSel[n].pop()
                        if len(newKeysIndexSel[n]) > 0: newKeysIndexSel[n].pop()
                        #reorder index according with size of segment
                        keysIndexSel[n] = self.tangentOppositeReorder(keysIndexSel[n], keyValues[n])
                    
                    #utilMod.timer() 
                                                                           
                    # apply the damn function
                    for loopIndex in keysIndexSel[n]:   
                        
                        curTangType   = self.tangType(keyValues[n], keyTimes[n], loopIndex)
                            
                        applied  = loopFunction(aCurve, keyValues[n], loopIndex, tangentType, curTangType, keysIndexSel[n], keyTimes[n])
                        
                        if loopFunction == self.fixTangentOvershoot and applied:
                            #remove the applied index to avoid changind that tangent again
                            if newKeysIndexSel[n]: newKeysIndexSel[n].remove(loopIndex)
                   
                    #utilMod.timer() 
                   
                    # put back
                    for i, loopLocked in enumerate(locked):
                        cmds.undoInfo(stateWithoutFlush=False)                        
                        if loopLocked: cmds.keyTangent(aCurve, edit=True, index=(i,i), lock=loopLocked)
                        cmds.undoInfo(stateWithoutFlush=True)
                    
                    #utilMod.timer() 
                        
                    if weighted: cmds.keyTangent(aCurve, edit=True, weightedTangents=False) #weight to balance in and out tangents
                    cmds.keyTangent(aCurve, edit=True, weightedTangents=weighted)
        
            #utilMod.timer("e", loopFunction)
                          
            
    def tangentOppositeReorder(self, indexes, values):
        #put bigger segments first
        
        difList = []
        for n, loopVal in enumerate(values[2:-3]):
            dif = values[n+1+2] - values[n+2]  
            difList.append(abs(dif))
        
        indexList  = []
        tmpDifList = utilMod.dupList(difList)
        for n, loopDif in enumerate(tmpDifList):
            maxDif = max(tmpDifList)
            index  = difList.index(maxDif)
            tmpDifList[index] = -1
            indexList.append(index)
           
        newIndexes = []
        for loopIndex in indexList:
            if loopIndex in indexes:
                newIndexes.append(loopIndex)
                
        """       
        print "indexList",indexList 
        print "values",values 
        print "difList",difList      
        print "indexes",indexes
        print "newIndexes",newIndexes
        """
        
        return newIndexes
                
    def setTangent(self, tangentType, tangentInOut="inOut", targetKeys="selected", *args):
        
        #utilMod.timer(mode="s", function="MAIN FUNCTION")
        
        cmds.waitCursor(state=True)
        
        """
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undoInfo(openChunk=True)
        """
        
        #tangentType = flow, bounce, auto, etc
        #targetKeys = all, selected
        #tangentInOut = inOut, in, out
        
        #set default tangent type
        if tangentType == "flow":    
            cmds.keyTangent(edit=True, g=True, inTangentType="auto", outTangentType="auto")    
        elif tangentType == "step":        
            cmds.keyTangent(edit=True, g=True, outTangentType=tangentType)
        elif tangentType != "bounce":
            cmds.keyTangent(edit=True, g=True, inTangentType=tangentType, outTangentType=tangentType)
            
            
        # get target curves
        getCurves  = animMod.getAnimCurves()
        animCurves = getCurves[0]
        getFrom    = getCurves[1]  
        
        #if there is no curves, exit
        if animCurves: 
            status          = "aTools - Tangents..."
            utilMod.startProgressBar(status)
            totalSteps      = len(animCurves)           
            firstStep       = 0
            thisStep        = 0
            estimatedTime   = None
            startChrono     = None
            
            index = None
            time  = None
            
            if targetKeys == "all": # apply for all keys
                time  = (-50000, 500000)
                
                if not self.isDefaultTangent(tangentType): 
                    index = animMod.getTarget("keyIndexTimes", animCurves, getFrom)
                
                self.applyTangent(animCurves, tangentType, getFrom, time, index)
      
            elif targetKeys == "selected": #apply on a range
                if getFrom == "timeline": 
                    time = animMod.getTimelineRange(); time = (time[0], time[1])#flow and bounce
                    if not self.isDefaultTangent(tangentType): index = animMod.getTarget("keysIndexSel", animCurves, getFrom)
                    self.applyTangent(animCurves, tangentType, getFrom, time, index, tangentInOut)
                        
                else: 
                    if self.isDefaultTangent(tangentType):  # if the tangent types are default maya types
                        #apply individually on each key
                        keysSel     = animMod.getTarget("keysSel", animCurves, getFrom)
                        
                        for thisStep, aCurve in enumerate(animCurves):
                            if cmds.progressBar(G.progBar, query=True, isCancelled=True ):  
                                utilMod.setProgressBar(endProgress=True)
                                break
                            startChrono     = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status) 
                            
                            for loopKey in keysSel[thisStep] :
                                time = (loopKey, loopKey)
                                self.applyTangent(aCurve, tangentType, getFrom, time, index, tangentInOut)
                                
                            estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
                                
                    else: #flow and bounce
                        index = animMod.getTarget("keysIndexSel", animCurves, getFrom)
                        self.applyTangent(animCurves, tangentType, getFrom, time, index, tangentInOut)
            else:# first and last frame           
                keyTimes      = animMod.getTarget("keyTimes", animCurves, getFrom)
                keyIndexTimes = animMod.getTarget("keyIndexTimes", animCurves, getFrom)
                
                self.bounceEnds(animCurves, tangentType, getFrom, tangentInOut, keyTimes, keyIndexTimes, targetKeys)
         
            
            utilMod.setProgressBar(endProgress=True)
        #cmds.undoInfo(closeChunk=True)
        
        cmds.waitCursor(state=False)
        
        #utilMod.timer(mode="e", function="MAIN FUNCTION")
    
    def bounceEnds(self, animCurves, tangentType, getFrom, tangentInOut, keyTimes, keyIndexTimes, targetKeys):
        for n, aCurve in enumerate(animCurves):                
            if targetKeys == "first" or targetKeys == "both": 
                
                firstTime  = keyTimes[n][0]
                firstIndex = keyIndexTimes[n][0]
                time       = (firstTime,firstTime)
                index      = [firstIndex]
                
                self.applyTangent([aCurve], tangentType, getFrom, [time], [index], tangentInOut)
           
            if targetKeys == "last" or targetKeys == "both": 
                lastTime   = keyTimes[n][-1]
                lastIndex  = keyIndexTimes[n][-1]
                time       = (lastTime,lastTime)
                index      = [lastIndex]
                
                self.applyTangent([aCurve], tangentType, getFrom, [time], [index], tangentInOut)
                
    
    def isDefaultTangent(self, tangentType):
        return (tangentType != "flow" and tangentType != "bounce")
                                 
    def tangType(self, keyVal, keyTimes, index):
        
        keyValTmp = utilMod.dupList(keyVal)
        
        keyLocation = self.getKeyLocation(keyValTmp, index)
        nKeys       = len(keyValTmp)
        
        if keyLocation == "first":
            if keyValTmp[index] == keyValTmp[index+1] == keyValTmp[index+2]:        
                return "Zero"
        elif keyLocation == "last":  
            if keyValTmp[index] == keyValTmp[index-1] == keyValTmp[index-2]:        
                return "Zero"
        else:
            index += 2
            for x in range(2):
                keyValTmp.insert(0, keyValTmp[0])
                keyValTmp.append(keyValTmp[-1])  
            
            if keyValTmp[index] == keyValTmp[index+1] == keyValTmp[index+2] or keyValTmp[index] == keyValTmp[index-1] == keyValTmp[index-2] or keyValTmp[index] == keyValTmp[index+1] == keyValTmp[index-1]:        
                return "Zero"
        
        #or....
        return "Average"
                
            
    def getAverageAngle(self, keyVal, keyTimes, index):
        
        keyLocation = self.getKeyLocation(keyVal, index)
        
        if keyLocation == "mid":
        
            relTimeInA    = keyTimes[index] - keyTimes[index-1]
            relValInA     = keyVal[index-1] - keyVal[index]
            relTimeOutA   = keyTimes[index+1] - keyTimes[index]
            relValOutA    = keyVal[index+1] - keyVal[index]
            outAngleA     = math.degrees(math.atan(relValOutA/relTimeOutA))
            outOpp        = relTimeInA*math.tan(math.radians(outAngleA))
            
            return -math.degrees(math.atan(((relValInA-outOpp)/2)/relTimeInA))
        
        return 0
            
    # end getAverageAngle 
    
    def getKeyLocation(self, keyVal, index):
        if index == 0:
            return "first"
        elif index == len(keyVal)-1:
            return "last"
        else:
            return "mid"
    
    def fixTangentOvershoot(self, aCurve, keyVal, index, tangentType, curTangType, keysIndexSelN, *args):
        
        #print "qual index? ", index
        if index == None: return
        
        #fix tangent limit  ----------------------------------------------------------------------------
        applied = False
        
        
        power     = .8
        
        #get in values 
        iy        = cmds.keyTangent(aCurve, query=True, index=(index, index), iy=True)[0]/3*power #in tangent handle y position
        oy        = cmds.keyTangent(aCurve, query=True, index=(index, index), oy=True)[0]/3*power #out tangent handle y position
        
        prevVal   = keyVal[index-1]
        currVal   = keyVal[index]
        nextVal   = keyVal[index+1]
        
        
        #convert to radians if rotate
        isRotate = animMod.isAnimCurveRotate(aCurve)
        if isRotate:
            prevVal = math.radians(prevVal)
            currVal = math.radians(currVal)
            nextVal = math.radians(nextVal)
        
        
        
        difNext   = (nextVal-currVal)*power
        difPrev   = (currVal-prevVal)*power
        
        if (difNext < 0 and oy < difNext) or (difNext > 0 and oy > difNext):                            
            cmds.keyTangent(aCurve, edit=True, index=(index, index), inTangentType="auto", outTangentType="auto")
            
            cmds.keyTangent(aCurve, edit=True, index=(index, index), oy=difNext*3)
            applied = True
            
            
        if (difPrev < 0 and iy < difPrev) or (difPrev > 0 and iy > difPrev):                            
            cmds.keyTangent(aCurve, edit=True, index=(index, index), inTangentType="auto", outTangentType="auto")
            
            cmds.keyTangent(aCurve, edit=True, index=(index, index), iy=difPrev*3)
            
            #print "aplicou index:", index
            
            if index-1 in keysIndexSelN:
                cmds.keyTangent(aCurve, edit=True, index=(index-1, index-1), inTangentType="auto", outTangentType="auto")
                
                self.flowTangent(aCurve, keyVal, index-1, tangentType)
                applied = True
                
                #print "flow index:", index-1
        """    
        print "--------------------------------"
        print  "index", index
        print  "iy",iy
        print  "oy",oy
        print  "difPrev",difPrev
        print  "prevVal",prevVal
        print  "nextVal",nextVal
        print  "currVal",currVal
        """
    
        
        return applied   
    
    def fixTangentOpposite(self, aCurve, keyVal, index, tangentType, curTangType, keysIndexSelN, *args):
    
        if index == None: return
     
        currVal   = keyVal[index] 
        nextVal   = keyVal[index+1]      
        currTime  = cmds.keyframe(aCurve, query=True, index=(index,index), timeChange=True)[0]#current time value
        nextTime  = cmds.keyframe(aCurve, query=True, index=(index+1,index+1), timeChange=True)[0]#current time value
        
        power     = 2
        
         
        #get in values for next key
        ix        = cmds.keyTangent(aCurve, query=True, index=(index+1,index+1), ix=True)[0] #in tangent handle x position
        iy        = cmds.keyTangent(aCurve, query=True, index=(index+1,index+1), iy=True)[0] #in tangent handle y position
     
        #get out values
        ox        = cmds.keyTangent(aCurve, query=True, index=(index,index), ox=True)[0] #out tangent handle x position
        oy        = cmds.keyTangent(aCurve, query=True, index=(index,index), oy=True)[0] #out tangent handle y position
        
        
        
        
        
        #curve position at handle
        valIn     = nextVal - cmds.keyframe(aCurve, query=True, eval=True, time=(nextTime-ix/.125,nextTime-ix/.125), valueChange=True)[0]
        valOut    = cmds.keyframe(aCurve, query=True, eval=True, time=(currTime+ox/.125,currTime+ox/.125), valueChange=True)[0] - currVal
        
        #convert to radians if rotate
        isRotate = animMod.isAnimCurveRotate(aCurve)
        if isRotate:
            currVal = math.radians(currVal)
            nextVal = math.radians(nextVal)
            valIn   = math.radians(valIn)
            valOut  = math.radians(valOut) 
        
        #difference btw val and y
        difIn     = iy/3 - valIn
        difOut    = oy/3 - valOut
        
        
        
        
        #detect 
        if (difIn > 0 and difOut > 0) or (difIn < 0 and difOut < 0):        
            
            if abs(difIn) > abs(difOut):               
                inOut = "in"
                
            else:            
                inOut = "out"
                
                
            for x in range(5):   
                currVal   = keyVal[index] 
                nextVal   = keyVal[index+1]      
                #get in values for next key
                ix        = cmds.keyTangent(aCurve, query=True, index=(index+1,index+1), ix=True)[0] #in tangent handle x position
                iy        = cmds.keyTangent(aCurve, query=True, index=(index+1,index+1), iy=True)[0] #in tangent handle y position
             
                #get out values
                ox        = cmds.keyTangent(aCurve, query=True, index=(index,index), ox=True)[0] #out tangent handle x position
                oy        = cmds.keyTangent(aCurve, query=True, index=(index,index), oy=True)[0] #out tangent handle y position
                
                #curve position at handle
                valIn     = nextVal - cmds.keyframe(aCurve, query=True, eval=True, time=(nextTime-ix/.125,nextTime-ix/.125), valueChange=True)[0]
                valOut    = cmds.keyframe(aCurve, query=True, eval=True, time=(currTime+ox/.125,currTime+ox/.125), valueChange=True)[0] - currVal
                
                #convert to radians if rotate
                isRotate = animMod.isAnimCurveRotate(aCurve)
                if isRotate:
                    currVal = math.radians(currVal)
                    nextVal = math.radians(nextVal)
                    valIn   = math.radians(valIn)
                    valOut  = math.radians(valOut) 
                
                #difference btw val and y
                difIn     = iy/3 - valIn
                difOut    = oy/3 - valOut         
                
                if inOut == "in":
                    #print"IN"
                    
                    #if next key is is array
                    if index+1 in keysIndexSelN:
                    
                        newY = (iy/3) + (valOut-(oy/3))*power
                        cmds.keyTangent(aCurve, edit=True, index=(index+1, index+1), iy=newY*3, oy=newY*3, ox=ix)
                                              
                
                else:
                    #print"OUT"
                    newY = (oy/3) + (valIn-(iy/3))*power
                    cmds.keyTangent(aCurve, edit=True, index=(index, index), iy=newY*3, oy=newY*3, ix=ox)
                
    
        
            """
            print "index",index
            print "difIn",difIn
            print "difOut",difOut
            print "iy",iy
            print "oy",oy
            print "iy/3",iy/3
            print "oy/3",oy/3
            print "valIn",valIn
            print "valOut",valOut
            print "currVal",currVal
            print "nextVal",nextVal
            print "------------------------------"
            """
    
    def averageTangent(self, aCurve, keyVal, index, tangentType, curTangType, keysIndexSelN, keyTimes, *args):
        # average 
        
        cmds.keyTangent(aCurve, edit=True, index=(index, index), inTangentType="linear", outTangentType="linear")
        
        if tangentType == "flow": 
            if curTangType == "Zero":
                mAngle    = 0 
            else:
                mAngle    = self.getAverageAngle(keyVal, keyTimes, index)
            
            if index == 0:
                cmds.keyTangent(aCurve, edit=True, index=(index, index), outTangentType="linear")
                return
            if index == len(keyVal)-1:
                cmds.keyTangent(aCurve, edit=True, index=(index, index), inTangentType="linear")
                return
                
            cmds.keyTangent(aCurve, edit=True, index=(index, index), inAngle=mAngle, outAngle=mAngle) 
            
            
        #if tangentType == "bounce": 
            #cmds.keyTangent(aCurve, edit=True, index=(index, index), inTangentType="linear", outTangentType="linear")
    
    def flowTangent(self, aCurve, keyVal, index, tangentType, curTangType, *args):
        
        if curTangType == "Zero" and tangentType == "flow": return
        
        if index == None: return
        
        #is it first or last key?
        keyLocation = self.getKeyLocation(keyVal, index)
            
        if keyLocation != "mid" and tangentType != "bounce": return
    
        currVal   = keyVal[index]      
        currTime  = cmds.keyframe(aCurve, query=True, index=(index,index), timeChange=True)[0]#current time value
        
        #get in values 
        ix        = cmds.keyTangent(aCurve, query=True, index=(index,index), ix=True)[0] #in tangent handle x position
        iy        = cmds.keyTangent(aCurve, query=True, index=(index,index), iy=True)[0] #in tangent handle y position
     
        #get out values
        ox        = cmds.keyTangent(aCurve, query=True, index=(index,index), ox=True)[0] #out tangent handle x position
        oy        = cmds.keyTangent(aCurve, query=True, index=(index,index), oy=True)[0] #out tangent handle y position
        
        cmds.undoInfo(stateWithoutFlush=False) 
        cmds.keyTangent(aCurve, index=(index,index), lock=False) 
        cmds.undoInfo(stateWithoutFlush=True) 
        if tangentType == "flow":
            if ox>ix:
                ox = ix
                oy = iy
                cmds.keyTangent(aCurve, edit=True, index=(index, index), ox=ox, oy=oy)
            else:
                ix = ox
                iy = oy
                cmds.keyTangent(aCurve, edit=True, index=(index, index), ix=ix, iy=iy)
        
            
        #curve position at handle
        valIn     = cmds.keyframe(aCurve, query=True, eval=True, time=(currTime-ix/.125,currTime-ix/.125), valueChange=True)[0] 
        valOut    = cmds.keyframe(aCurve, query=True, eval=True, time=(currTime+ox/.125,currTime+ox/.125), valueChange=True)[0]
    
        
        #if the anim curve is rotate, convert to radians     
        isRotate = animMod.isAnimCurveRotate(aCurve)
        if isRotate:
            currVal = math.radians(currVal)
            valIn   = math.radians(valIn)
            valOut  = math.radians(valOut)   
            #print "isrotate"     
        
        #distance between the curve position and the key value   
        distValueIn    = (valIn-currVal)
        distValueOut   = (valOut-currVal)    
        
        #distance between the curve position and the tangent y position   
        distTangIn    = distValueIn+(iy/3)
        distTangOut   = distValueOut-(oy/3) 
        
        
        if tangentType == "flow":
            
            # calculate the difference btween the distances between the curve position and the tangent y position 
            dif = (distTangIn-distTangOut)   
            
            newOy     = (oy/3)-dif
            
            #newIy     = (iy/3)-dif
            newIy     = newOy
                    
            #print "newIy",newIy,"(iy/3)",(iy/3),"(oy/3)",(oy/3),"currVal",currVal,"valOut",valOut,"distIn",distTangIn,"distOut",distTangOut,"dif",dif,"distValueIn",distValueIn,"distValueOut",distValueOut
         
        elif tangentType == "bounce":        
            newIy  = -distValueIn+(-distValueIn-(iy/3))
            newOy  = distValueOut+(distValueOut-(oy/3))
            
            """
            print "---------------------------"
            print "newIy",newIy
            print "newOy",newOy
            print "(iy/3)",(iy/3)
            print "(oy/3)",(oy/3)
            print "currVal",currVal
            print "valOut",valOut
            print "distIn",distTangIn
            print "distOut",distTangOut
            print "distValueIn",distValueIn
            print "distValueOut",distValueOut
            """
        
        #apply
        
        cmds.keyTangent(aCurve, edit=True, index=(index, index), iy=newIy*3, oy=newOy*3)
          