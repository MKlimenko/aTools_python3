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
from aTools.commonMods import commandsMod
from aTools.commonMods import aToolsMod



G.TM_coloredKeys        = None
G.TM_lastTweenCommand   = G.TM_lastTweenCommand or None

class TweenMachine_Gui(uiMod.BaseSubUI):
        
    def createLayout(self):
        tweenMachine    = TweenMachine()
        
        cmds.rowColumnLayout(numberOfColumns=100, parent=self.parentLayout)
                 
        #linear          
        cmds.text( label='   ', h=1 )
        cmds.iconTextButton(style='iconOnly',     marginWidth=0,     w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_left"),  highlightImage= uiMod.getImagePath("tweenMachine_left copy"),     command=lambda *args: tweenMachine.setTween("linear_prev"), annotation="Overshoot linear tween")
        cmds.iconTextButton(style='iconOnly',     marginWidth=0,     w=self.ws, h=self.hb, image= uiMod.getImagePath("tweenMachine_L"),     highlightImage= uiMod.getImagePath("tweenMachine_L copy"),       command=lambda *args: tweenMachine.setTween("linear"),      annotation="Linear tween")
        cmds.iconTextButton(style='iconOnly',     marginWidth=0,     w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_right"), highlightImage= uiMod.getImagePath("tweenMachine_right copy"),     command=lambda *args: tweenMachine.setTween("linear_next"), annotation="Overshoot linear tween")
             
        #tween
        cmds.text( label='   ', h=1 )
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_left"), highlightImage= uiMod.getImagePath("tweenMachine_left copy"),   command=lambda *args: tweenMachine.setTween(-50),           annotation="Overshoot 50% with previous key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(-30),           annotation="Overshoot 30% with previous key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(-10),            annotation="Overshoot 10% with previous key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hb, image= uiMod.getImagePath("tweenMachine_key"),  highlightImage= uiMod.getImagePath("tweenMachine_key copy"),       command=lambda *args: tweenMachine.setTween(0),             annotation="Copy previous key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(10),            annotation="Tween 90% with previous key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(20),            annotation="Tween 80% with previous key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(33),            annotation="Tween 66% with previous key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hb, image= uiMod.getImagePath("tweenMachine_T"),    highlightImage= uiMod.getImagePath("tweenMachine_T copy"),       command=lambda *args: tweenMachine.setTween(50),            annotation="Tween 50%"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(66),            annotation="Tween 66% with next key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(80),            annotation="Tween 80% with next key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(90),            annotation="Tween 90% with next key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hb, image= uiMod.getImagePath("tweenMachine_key"),  highlightImage= uiMod.getImagePath("tweenMachine_key copy"),       command=lambda *args: tweenMachine.setTween(100),           annotation="Copy next key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(110),           annotation="Overshoot 10% with next key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_mid"),  highlightImage= uiMod.getImagePath("tweenMachine_mid copy"),   command=lambda *args: tweenMachine.setTween(130),           annotation="Overshoot 30% with next key"); tweenMachine.popUpColor()
        cmds.iconTextButton(style='iconOnly',     marginWidth=0, w=self.ws, h=self.hs, image= uiMod.getImagePath("tweenMachine_right"),highlightImage= uiMod.getImagePath("tweenMachine_right copy"),   command=lambda *args: tweenMachine.setTween(150),           annotation="Overshoot 50% with next key"); tweenMachine.popUpColor()
       
        
class TweenMachine(object):
    
    def __init__(self):
        
        if G.aToolsBar.tweenMachine: return
        G.aToolsBar.tweenMachine = self        
         
    # end createLayout
    def popUpColor(self):
        cmds.popupMenu(postMenuCommand=self.populateColorMenu, postMenuCommandOnce=True)
        
    def populateColorMenu(self, parent, *args):
    
        cmds.menuItem(label="Color Keyframes", checkBox=self.getColoredKeys(), command=self.setColoredKeys, parent=parent)
        cmds.menuItem(divider=True, parent=parent )   
        cmds.menuItem(label="Apply Special Key Color", command=lambda *args:self.applyTickColor(True), parent=parent)
        cmds.menuItem(label="Apply Default Key Color", command=lambda *args:self.applyTickColor(False), parent=parent)
    
     
    def getColoredKeys(self):
    
        if not G.TM_coloredKeys:
            r = aToolsMod.loadInfoWithUser("userPrefs", "coloredKeys")
        else:
            r = G.TM_coloredKeys
            
        if r == None: 
            default = True
            r = default 
        
        G.TM_coloredKeys = r
        
        return r        
    
    def setColoredKeys(self, onOff):
        onOff = not self.getColoredKeys()
        
        G.TM_coloredKeys = onOff
        
        aToolsMod.saveInfoWithUser("userPrefs", "coloredKeys", onOff)
        
        
    def repeatLastCommand(self):
        if G.TM_lastTweenCommand:  eval(G.TM_lastTweenCommand)
        
        
    def setTween(self, percent, *args):
        
        #utilMod.timer("s")
        
        
        G.TM_lastTweenCommand = "self.setTween(%s)"%percent
            
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]
        
        if animCurves:
            status          = "aTools - Tween Machine..."
            utilMod.startProgressBar(status)
            totalSteps      = len(animCurves)           
            firstStep       = 0
            thisStep        = 0
            estimatedTime   = None
            startChrono     = None
            
            cmds.waitCursor(state=True)
            cmds.refresh(suspend=True)        
            
            
            keysSel         = animMod.getTarget("keysSel", animCurves, getFrom)
            keyTimes        = animMod.getTarget("keyTimes", animCurves)
            timelineTime    = None
            #keysSelMerged   = utilMod.mergeLists(keysSel)
            
            if isinstance(percent, int):
                # reverse order to get ease in and out smoothly
                if 0 < percent <= 50 or percent == 100: 
                    for loopVal in keysSel:
                        loopVal.reverse()
                    
            #utilMod.timer()
            
            """
            if len(keysSelMerged) == 0: 
                if not timelineTime: timelineTime = [animMod.getTimelineTime()]
                cmds.setKeyframe(animCurves, time=timelineTime[0])
            elif len(keysSelMerged) == 1: 
                cmds.setKeyframe(animCurves, time=keysSelMerged[0])
            """
            
            
            for thisStep, loopCurve in enumerate(animCurves):
                
                if cmds.progressBar(G.progBar, query=True, isCancelled=True ):  
                    utilMod.setProgressBar(endProgress=True)
                    break
                
                startChrono     = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)
                
                if not keysSel[thisStep]:
                    if not timelineTime: timelineTime = [animMod.getTimelineTime()]
                    time = timelineTime
                else:
                    time = [(loopTime,loopTime) for loopTime in keysSel[thisStep]]
                    # if all keys selected, use timeline time instead
                    if len(time) == len(keyTimes[thisStep]):                    
                        if not timelineTime: timelineTime = [animMod.getTimelineTime()]
                        time = timelineTime
                
                
                    
                for loopTime in time:
                    
                    
                    prevKeyTime    = cmds.findKeyframe(loopCurve, time=loopTime, which="previous")
                    nextKeyTime    = cmds.findKeyframe(loopCurve, time=loopTime, which="next")
                    
                    if prevKeyTime == nextKeyTime and prevKeyTime != loopTime[0] and percent != "linear_next" and percent != "linear_prev": # if there is no previous or next key and at least one key
                        cmds.setKeyframe(loopCurve, time=loopTime)                
                    
                    elif prevKeyTime != time[0]:                    
                        
                        if percent == "linear_prev":
                            
                            prevKeyTime     = nextKeyTime
                            nextKeyTime     = cmds.findKeyframe(loopCurve, time=(prevKeyTime,prevKeyTime), which="next")
                            prevKeyVal      = cmds.keyframe(loopCurve, query=True, time=(prevKeyTime, prevKeyTime), valueChange=True)[0]
                            nextKeyVal      = cmds.keyframe(loopCurve, query=True, time=(nextKeyTime, nextKeyTime), valueChange=True)[0]
    
                            if nextKeyTime == prevKeyTime: 
                                value       = prevKeyVal
                            else:                        
                                value       = prevKeyVal + ((nextKeyVal - prevKeyVal)/(nextKeyTime - prevKeyTime)*(loopTime[0] - prevKeyTime))
                            
                        elif percent == "linear_next":
                            
                            nextKeyTime     = prevKeyTime
                            prevKeyTime     = cmds.findKeyframe(loopCurve, time=(nextKeyTime,nextKeyTime), which="previous")
                            prevKeyVal      = cmds.keyframe(loopCurve, query=True, time=(prevKeyTime, prevKeyTime), valueChange=True)[0]
                            nextKeyVal      = cmds.keyframe(loopCurve, query=True, time=(nextKeyTime, nextKeyTime), valueChange=True)[0]
                            
                            if nextKeyTime == prevKeyTime: 
                                value       = prevKeyVal
                            else:
                                value       = prevKeyVal + ((nextKeyVal - prevKeyVal)/(nextKeyTime - prevKeyTime)*(loopTime[0] - prevKeyTime))
                            
                        else:
                            
                            animMod.eulerFilterCurve([loopCurve]) 
                            
                            prevKeyVal = cmds.keyframe(loopCurve, query=True, time=(prevKeyTime, prevKeyTime), valueChange=True)[0]
                            nextKeyVal = cmds.keyframe(loopCurve, query=True, time=(nextKeyTime, nextKeyTime), valueChange=True)[0]
                        
                            #print "prevKeyVal", prevKeyVal, nextKeyVal
                        
                            #if prevKeyVal == nextKeyVal: 
                                #if not time[0] in keysSel[thisStep]: cmds.setKeyframe(loopCurve, time=loopTime)
                                #continue
                            
                        
                            if percent == "linear": value  = prevKeyVal + ((nextKeyVal - prevKeyVal)/(nextKeyTime - prevKeyTime)*(loopTime[0] - prevKeyTime))
                            else:                   value  = ((nextKeyVal-prevKeyVal)/100.*percent)+prevKeyVal
        
                        
                        tangentType     = cmds.keyTangent(loopCurve, query=True, outTangentType=True, time=(prevKeyTime,prevKeyTime))[0]
                        inTangentType   = tangentType.replace("fixed", "auto").replace("step", "auto")
                        outTangentType  = tangentType.replace("fixed", "auto")
                        
                        if not time[0] in keysSel[thisStep]: cmds.setKeyframe(loopCurve, time=loopTime)
                        
                        cmds.keyframe(loopCurve, edit=True, time=loopTime, valueChange=value)
                        cmds.keyTangent(loopCurve, edit=True, time=loopTime, inTangentType=inTangentType, outTangentType=outTangentType)
                        #keycolor
                        if (isinstance(percent, int) and (1 <= percent <= 99)) or percent == "linear": cmds.keyframe(loopCurve ,edit=True,time=loopTime, tickDrawSpecial=self.getColoredKeys())
                    
    
                    
                    if getFrom == "graphEditor":   
                        #curvesToSelect.append([loopCurve, loopTime])
                        cmds.selectKey(loopCurve, addTo=True, time=loopTime)
                        
                        
                estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)
            
            #utilMod.timer()
            """
            #APPLY        
            if len(curvesToKey) > 0: cmds.setKeyframe(curvesToKey)
            
            for loopVar in curvesToValue: 
                cmds.keyframe(loopVar[0], edit=True, time=loopVar[1], valueChange=loopVar[2])
                cmds.keyTangent(loopVar[0], edit=True, time=loopVar[1], inTangentType=loopVar[3], outTangentType=loopVar[4])
                      
            for loopVar in curvesToColor:  cmds.keyframe(loopVar[0], edit=True, time=loopVar[1], tickDrawSpecial=self.getColoredKeys())        
            for loopVar in curvesToSelect: cmds.selectKey(loopVar[0], addTo=True, time=loopVar[1])
            """
               
            
            cmds.refresh(suspend=False)
            cmds.waitCursor(state=False)
            utilMod.setProgressBar(endProgress=True)
            
            #utilMod.timer("e", "tween")
    #end tweenValue    
    
        
        
    def applyTickColor(self, special=True, *args):
        
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]
        
        keysSel     = animMod.getTarget("keysSel", animCurves, getFrom)
        
        if animCurves:
            
             for n, loopCurve in enumerate(animCurves):
                time = [(loopTime,loopTime) for loopTime in keysSel[n]]
                    
                for loopTime in time:
                    #keycolor
                    cmds.keyframe(loopCurve ,edit=True,time=loopTime, tickDrawSpecial=special)

