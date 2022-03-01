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


Tumble on objects was adapted from:

''' 

from maya import cmds
from maya import mel
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import utilMod

import math

class TumbleOnObjects(object):
    
    def __init__(self):
        self.currentLocalTumble = cmds.tumbleCtx ("tumbleContext", query=True, localTumble=True)
        self.unitMultiplier = {"mm": 0.1,
                               "cm": 1.0,
                               "m" : 100.0,
                               "in": 2.54,
                               "ft": 30.48,
                               "yd": 91.44}

    def switch(self, onOff):
    
        utilMod.killScriptJobs("G.tumbleOnObjectsScriptJobs")
        
        if onOff:
            cmds.tumbleCtx ("tumbleContext", edit=True, localTumble=0)
            #scriptJob   
            G.tumbleOnObjectsScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('DragRelease', self.update )))
            G.tumbleOnObjectsScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('SelectionChanged', self.update )))
            G.tumbleOnObjectsScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('timeChanged', self.update )))
            
            self.update()
            
        else:
            cmds.tumbleCtx ("tumbleContext", edit=True, localTumble=self.currentLocalTumble)


    def update(self):
        
        sel             = cmds.ls(selection=True)        
                
        if len(sel) > 0:             
            
            sel             = sel[-1]                           
            allowedTypes    = ["transform", "joint"]
            
            if cmds.nodeType(sel) in allowedTypes :
                
                currUnit        = cmds.currentUnit(query=True, linear=True)
                unitMultiplier  = self.unitMultiplier[currUnit]
                isMesh          = cmds.listRelatives(sel, allDescendents=True, noIntermediate=True, type="mesh") != None
           
                if isMesh:  
                    bb  = cmds.xform(sel, query=True, boundingBox=True, ws=True)
                    x   = ((bb[0] + bb[3])/2.)
                    y   = ((bb[1] + bb[4])/2.)
                    z   = ((bb[2] + bb[5])/2.)
                    
                else:
                    xyz = cmds.xform(sel, query=True, ws=True, rotatePivot=True)
                    x   = xyz[0]
                    y   = xyz[1]
                    z   = xyz[2]
            
                
                x     = x * unitMultiplier
                y     = y * unitMultiplier
                z     = z * unitMultiplier
                cams  = cmds.ls(dag=True, cameras=True )
                
                """
                for loopCam in cams:
                    if math.isnan(cmds.getAttr("%s.centerOfInterest"%loopCam)):
                        print "center is NAN"
                
                if math.isnan(x) or math.isnan(y) or math.isnan(z): 
                    print "tumble returns"
                    print xyz
                    for cam in cams:
                        t = cmds.xform(cam, query=True, ws=True, rotatePivot=True)
                        print cam, t
                    return
                """
                
                cmds.undoInfo(stateWithoutFlush=False)
                                
                for loopCam in cams:
                    try:      cmds.setAttr("%s.tumblePivot"%loopCam, x, y, z)
                    except:   pass
                
                cmds.undoInfo(stateWithoutFlush=True)
                
                    
                    
                    