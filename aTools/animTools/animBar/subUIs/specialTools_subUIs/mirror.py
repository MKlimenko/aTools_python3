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
from maya import mel
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod
from aTools.commonMods import aToolsMod


class Mirror(object):    
    

    utilMod.killScriptJobs("G.mirrorScriptJobs")
        
    
    def __init__(self):
        
        self.INVERT_RULES_PREFS =       [{  "name":"invertRulesMirrorObjsTranslateX",
                                            "default":True
                                        },{ "name":"invertRulesMirrorObjsTranslateY",
                                            "default":False
                                        },{ "name":"invertRulesMirrorObjsTranslateZ",
                                            "default":False
                                        },{ "name":"invertRulesMirrorObjsRotateX",
                                            "default":False
                                        },{ "name":"invertRulesMirrorObjsRotateY",
                                            "default":False
                                        },{ "name":"invertRulesMirrorObjsRotateZ",
                                            "default":False
                                        },{  "name":"invertRulesCenterObjsTranslateX",
                                            "default":True
                                        },{ "name":"invertRulesCenterObjsTranslateY",
                                            "default":False
                                        },{ "name":"invertRulesCenterObjsTranslateZ",
                                            "default":False
                                        },{ "name":"invertRulesCenterObjsRotateX",
                                            "default":False
                                        },{ "name":"invertRulesCenterObjsRotateY",
                                            "default":True
                                        },{ "name":"invertRulesCenterObjsRotateZ",
                                            "default":True
                                        }] 

    def start(self):
        mod = uiMod.getModKeyPressed()
            
        if mod == "shift":
            self.selectMirrorObjs(True) 
        elif mod == "ctrl":
            self.selectMirrorObjs(False)
        else:
            sel = cmds.ls(selection=True)
            if sel: self.applyMirror()
            else:   self.toggleAutoSelectMirrorObjects()
    
    
    def popupMenu(self):
        cmds.popupMenu()
        cmds.menuItem("autoSelectMirrorObjectsMenu", label='Auto Select Mirror Objects' , checkBox=False, command=self.toggleAutoSelectMirrorObjects)
        cmds.menuItem("invertRulesMenu", subMenu=True, label='Invert Rules' , tearOff=True)
        for n, loopPref in enumerate(self.INVERT_RULES_PREFS):
            name    = loopPref["name"]
            if n == 6: cmds.menuItem( divider=True )
                
            cmds.menuItem('%sMenu'%name,            label=utilMod.toTitle(name[11:]),        command=lambda x, name=name, *args: aToolsMod.setPref(name, self.INVERT_RULES_PREFS), checkBox=aToolsMod.getPref(name, self.INVERT_RULES_PREFS))
        
        cmds.menuItem( divider=True )
        cmds.menuItem("loadDefaultsInvertRulesMenu",          label="Load Defaults",     command=lambda *args:utilMod.loadDefaultPrefs(self.INVERT_RULES_PREFS))
        cmds.setParent( '..', menu=True )
        cmds.menuItem( divider=True )        
        cmds.menuItem(label="Unselect Right",  command=lambda *args: self.unselectMirrorObjs("right"))
        cmds.menuItem(label="Unselect Left",   command=lambda *args: self.unselectMirrorObjs("left"))
        cmds.menuItem(label="Unselect Center", command=lambda *args: self.unselectMirrorObjs("center"))
        cmds.menuItem( divider=True )
        cmds.menuItem(label="Paste And Invert Cycle",   command=lambda *args: self.applyMirror(pasteAndCycle=True))
    
    
    def toggleAutoSelectMirrorObjects(self, *args):
        
        onOff = not cmds.menuItem("autoSelectMirrorObjectsMenu", query=True , checkBox=True)
        if args: onOff = not onOff #if checkbox pressed
        
        if onOff:   cmds.iconTextButton("mirrorBtn", edit=True, image=uiMod.getImagePath("specialTools_mirror_active"), highlightImage= uiMod.getImagePath("specialTools_mirror_active"))
        else:       cmds.iconTextButton("mirrorBtn", edit=True, image=uiMod.getImagePath("specialTools_mirror"), highlightImage= uiMod.getImagePath("specialTools_mirror copy"))
       
        self.setAutoSelectMirrorObjects(onOff)
        if not args:cmds.menuItem("autoSelectMirrorObjectsMenu", edit=True , checkBox=onOff)
        
       
    def setAutoSelectMirrorObjects(self, onOff):
        
        utilMod.killScriptJobs("G.mirrorScriptJobs")
                
        if onOff:
            self.autoSelectMirrorObjects()   
            G.mirrorScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('SelectionChanged', self.autoSelectMirrorObjects )))  

           
        
        
    def autoSelectMirrorObjects(self):
        sel = cmds.ls(selection=True)
        if sel: self.selectMirrorObjs(add=True, lastObj=sel[-1])
    
    def getInvertRules(self):
        
        invertRules = []
        
        for loopPref in self.INVERT_RULES_PREFS:
            name    = loopPref["name"]
            pref    = aToolsMod.getPref(name, self.INVERT_RULES_PREFS)
            mode    = name[11:]
            
            if pref: invertRules.append(mode)
    
        
        return   invertRules
    
    def mirrorInvert(self, aCurve, isCenterCurve, invertRules):
        
        transRot    =["Translate", "Rotate"] 
        modes       = ["x", "y", "z"]       
        value       = 1
        
        if isCenterCurve:
            objType = "Center"
        else:
            objType = "Mirror"
            
        for loopRule in invertRules:
            for loopMode in modes:
                for loopTransRot in transRot:
                    rule = "%sObjs%s%s"%(objType, loopTransRot, loopMode.title())            
                                    
                    if loopRule == rule:                    
                        if eval("animMod.isNode%s('%s', '%s')"%(loopTransRot, aCurve, loopMode)):
                            value = -1
        
                
        return value
    
    def unselectMirrorObjs(self, side):
        objects     = animMod.getObjsSel()
        
        if side == "center":
            objs  =   animMod.getMirrorObjs(objects, side="left")
            objects.extend(objs)
            objs.extend(animMod.getMirrorObjs(objects, side="right")) 
            objects.extend(objs)
            objs.extend(animMod.getMirrorObjs(objects, side="left")) 
            
            centerObjs = [loopObj for loopObj in objects if loopObj not in objs and loopObj and cmds.objExists(loopObj)]

            if len(centerObjs) >0: cmds.select(centerObjs, deselect=True)
        else:
            if side == "left": side = "right"
            elif side == "right": side = "left"
            objs = animMod.getMirrorObjs(objects, side=side) 
            objs = [loopObj for loopObj in objs if loopObj and cmds.objExists(loopObj)]
        
            if len(objs) > 0: cmds.select(objs, deselect=True)
    
    def selectMirrorObjs(self, add, lastObj=None):   
        objects     = animMod.getObjsSel()
        mirrorObjs  = animMod.getMirrorObjs(objects)     
        sel         = []
        
        if mirrorObjs: 
            for n, loopObj in enumerate(mirrorObjs):
                if loopObj:
                    if cmds.objExists(loopObj): sel.append(loopObj)
                else:
                    #central controller
                    sel.append(objects[n])
        
        if len(sel) >0:
        
            if lastObj:
                cmds.select(sel, addFirst=add)
            else:
                cmds.select(sel, add=add)
                    
        
        
        
        
    def applyMirror(self, pasteAndCycle=False):
    
        cmds.waitCursor(state=True) 
        
        range       = animMod.getTimelineRange()
        range[1]    = int(range[1])
        total       = range[1]-range[0]
        
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1] 
        
        invertRules = self.getInvertRules()
        
        if animCurves:
            status          = "aTools - Applying mirror..."
            utilMod.startProgressBar(status)
            totalSteps      = len(animCurves)           
            firstStep       = 0
            thisStep        = 0
            estimatedTime   = None
            startChrono     = None
            
            mirrorCurves        = animMod.getMirrorObjs(animCurves)
            keyValues           = animMod.getTarget("keyValues", animCurves, getFrom)
            keyTimes            = animMod.getTarget("keyTimes", animCurves, getFrom)
            currValues          = animMod.getTarget("currValues", animCurves, getFrom)
            keysIndexSel        = animMod.getTarget("keysIndexSel", animCurves, getFrom)
            keyTangentsAngle    = animMod.getTarget("keyTangentsAngle", animCurves, getFrom)
            keyTangentsType     = animMod.getTarget("keyTangentsType", animCurves, getFrom)
            currTime            = cmds.currentTime(query=True)
            
            
            
            if keysIndexSel:
                
                #create dummy key
                #objects     = animMod.getObjsSel()
                #mirrorObjs  = animMod.getMirrorObjs(objects)
                #animMod.createDummyKey(mirrorObjs)
                                
                for thisStep, aCurve in enumerate(animCurves):
                    
                    startChrono     = utilMod.chronoStart(startChrono, firstStep, thisStep, totalSteps, estimatedTime, status)
                    
                    mCurve              = mirrorCurves[thisStep]
                    isCenterCurve       = (mCurve == None)                
                    mirrorInvertValue   = self.mirrorInvert(aCurve, isCenterCurve, invertRules)
                    if mCurve and cmds.objExists(mCurve):
                        tCurve = mCurve
                    else:
                        tCurve = aCurve
                        
                    if not cmds.objExists(tCurve): continue
                           
                    
                    animMod.createDummyKey([tCurve])
                    
                    if len(keysIndexSel[thisStep]) > 0:
                        #delete keys
                        cmds.cutKey(tCurve, time=(keyTimes[thisStep][keysIndexSel[thisStep][0]],keyTimes[thisStep][keysIndexSel[thisStep][-1]]), clear=True) 
                    
                        for key in keysIndexSel[thisStep]:
                            keyValue            = keyValues[thisStep][key] * mirrorInvertValue
                            inTangAngleValue    = keyTangentsAngle[thisStep][key][0] * mirrorInvertValue
                            outTangAngleValue   = keyTangentsAngle[thisStep][key][1] * mirrorInvertValue
                               
                            
                            #apply keys
                            if pasteAndCycle:
                                t = keyTimes[thisStep][key] + (total/2.)
                                
                                if t == range[1]:
                                    #repeat key at first frame
                                    t1 = t-total
                                    time = (t1,t1)
                                    cmds.setKeyframe(tCurve, time=time, value=keyValue)
                                    cmds.keyTangent(tCurve,  time=time, inAngle=inTangAngleValue, outAngle=outTangAngleValue)
                                    cmds.keyTangent(tCurve,  time=time, inTangentType=keyTangentsType[thisStep][key][0], outTangentType=keyTangentsType[thisStep][key][1])
                                               
                                elif t > range[1]:
                                    #fist half
                                    t -= total
                                
                                time        = (t,t)
                                
                                
                                
                            else:
                                time        = (keyTimes[thisStep][key],keyTimes[thisStep][key])
                                
                            
                                
                            cmds.setKeyframe(tCurve, time=time, value=keyValue)
                            cmds.keyTangent(tCurve,  time=time, inAngle=inTangAngleValue, outAngle=outTangAngleValue)
                            cmds.keyTangent(tCurve,  time=time, inTangentType=keyTangentsType[thisStep][key][0], outTangentType=keyTangentsType[thisStep][key][1])
                    else: #no keys#invert translate x
                        keyValue = currValues[thisStep] * mirrorInvertValue
                           
                        
                        #apply keys
                        cmds.setKeyframe(tCurve, time=(currTime,currTime), value=keyValue)
                        
                    animMod.deleteDummyKey([tCurve]) 
                    
                    estimatedTime = utilMod.chronoEnd(startChrono, firstStep, thisStep, totalSteps)        
                    
                        
                #delete dummy key
                #animMod.deleteDummyKey(mirrorObjs)
            
            self.selectMirrorObjs(False)
            utilMod.setProgressBar(endProgress=True)
                           
        animMod.refresh()
        cmds.waitCursor(state=False) 
        

