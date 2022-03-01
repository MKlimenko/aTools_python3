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

from maya import cmds, mel
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import animMod
from aTools.commonMods import utilMod
from aTools.commonMods import aToolsMod

STORE_NODE      = "tUtilities"
CAMERA_ATTR     = "cameraSelected"
RANGE_ATTR      = "timelineRange"



G.TU_movie           = None
G.TU_audioFile       = None
G.TU_audioOffsetSec  = None

class TUtilities_Gui(uiMod.BaseSubUI):
    
        
    def createLayout(self):
        
        cmds.rowLayout(numberOfColumns=5, parent=self.parentLayout)
        
        timelineRange = TimelineRange()
        cmds.iconTextButton         (style='iconAndTextVertical',     w=self.wb, h=self.hb, image= uiMod.getImagePath("tUtilities_range"),   highlightImage= uiMod.getImagePath("tUtilities_range copy"),                     command=timelineRange.setTimelineRange,   annotation="Set timeline range\nRight click for options")
        timelineRange.popupMenu()
        
        cameraTools = CameraTools()
        cmds.iconTextButton         (style='iconAndTextVertical',     w=self.wb, h=self.hb, image= uiMod.getImagePath("tUtilities_camera"),           highlightImage= uiMod.getImagePath("tUtilities_camera copy"),           command=cameraTools.playblastCamera,    annotation="Playblast camera\nRight click to select camera")
        cameraTools.popupMenu()
        
   
    

    # end createLayout

class TimelineRange(object):
    
    def __init__(self):        
        G.playBackSliderPython  = G.playBackSliderPython or mel.eval('$aTools_playBackSliderPython=$gPlayBackSlider')
    
    def popupMenu(self, *args):            
        cmds.popupMenu("timelineRangeMenu",         postMenuCommand=self.populateMenu)
        
    def populateMenu(self, menu, *args):
        uiMod.clearMenuItems(menu)
        uiMod.clearMenuItems(menu)
        #cmds.menuItem(label="Clear motion trails", command=self.clear)
        cmds.radioMenuItemCollection(parent=menu)
        
        currRange    = [cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)]
        currRangeStr = "%s   -   %s"%(int(currRange[0]), int(currRange[1]))            
         
        #populate list
        ranges = self.getTimelineRanges()
        if ranges: ranges   = eval(ranges)
        if ranges:
            for loopRange in ranges:
                loopRangeStr    = "%s   -   %s"%(int(loopRange[0]), int(loopRange[1]-1))                                
                radioButton     = (currRangeStr == loopRangeStr)
                cmds.menuItem("menu_%s"%loopRange, radioButton=radioButton, label=loopRangeStr, parent=menu, command=lambda x, loopRange=loopRange, *args: self.setTimelineRange(loopRange))
            cmds.menuItem( divider=True, parent=menu)   
            newMenu = cmds.menuItem(subMenu=True, label='Delete', parent=menu) 
            cmds.menuItem( divider=True, parent=menu)  
            for loopRange in ranges:
                loopRangeStr = "%s   -   %s"%(int(loopRange[0]), int(loopRange[1]-1))
                cmds.menuItem("menu_%s"%loopRange, label=loopRangeStr, parent=newMenu, command=lambda x, loopRange=loopRange, *args: self.deleteTimelineRange(loopRange))
            cmds.menuItem( divider=True, parent=newMenu)       
            cmds.menuItem("menu_deleteAll", label="Delete All", parent=newMenu, command=self.deleteAllTimelineRange)
        cmds.menuItem("toggleLipSyncModeMenu", label='Lip Sync Mode', checkBox=self.isLipSyncMode(), command=self.toggleLipSyncMode, parent=menu) 
 
        

    def getTimelineRanges(self):
        return aToolsMod.loadInfoWithScene(STORE_NODE, RANGE_ATTR)
    
    
    def setTimelineRange(self, range=None, *args):  
           
        rangeVisible            = cmds.timeControl( G.playBackSliderPython, query=True, rangeVisible=True )
        
        if not rangeVisible and not range:
            range = [cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)+1]
        
        if range or rangeVisible:
      
            if not range: range = animMod.getTimelineRange(float=False)
            rFrom   = range[0]
            rTo     = range[1]-1
            
            cmds.playbackOptions(minTime=rFrom, maxTime=rTo)
            
            
            if self.getTimelineRanges() != None: 
                ranges = eval(self.getTimelineRanges()) 
            else: 
                ranges = []
            if not range in ranges:
                ranges.append(range)     
                aToolsMod.saveInfoWithScene(STORE_NODE, RANGE_ATTR, ranges) 
                
        
        utilMod.deselectTimelineRange()
            
            
    def deleteTimelineRange(self, range=None, *args):  
        
        ranges = eval(self.getTimelineRanges()) 
        if not ranges: ranges = []
        if range in ranges: ranges.remove(range)    
        aToolsMod.saveInfoWithScene(STORE_NODE, RANGE_ATTR, ranges) 
           
    def deleteAllTimelineRange(self, *args):
        aToolsMod.saveInfoWithScene(STORE_NODE, RANGE_ATTR, [])
    
    
    def toggleLipSyncMode(self, *args):
    
        if self.isLipSyncMode():
            cmds.timeControl(G.playBackSliderPython, edit=True, height=28) 
        else:
            cmds.timeControl(G.playBackSliderPython, edit=True, height=200) 
    
    def isLipSyncMode(self, *args):
        timelineHeight = cmds.timeControl(G.playBackSliderPython, query=True, height=True) 
        
        return timelineHeight > 28 
    

class CameraTools(object):
    
    
    def __init__(self):
        animMod.getShotCamera()        
        G.playBackSliderPython  = G.playBackSliderPython or mel.eval('$aTools_playBackSliderPython=$gPlayBackSlider')


    def popupMenu(self):
        cmds.popupMenu(postMenuCommand=self.populateMenu)
    
    def populateMenu(self, menu, *args):
                    
        uiMod.clearMenuItems(menu)
        
        cmds.radioMenuItemCollection(parent=menu)
        
        #populate list
        for loopCamera in utilMod.getAllCameras():
            radioSelected = (animMod.getShotCamera() == loopCamera)
            cameraName = cmds.listRelatives(loopCamera, allParents=True)[0]
            cmds.menuItem("menu_%s"%loopCamera, label=str(cameraName), radioButton=radioSelected, parent=menu, command=lambda x, loopCamera=loopCamera, *args: aToolsMod.saveInfoWithScene(STORE_NODE, CAMERA_ATTR, loopCamera))
    
        # last playblast menu
        cmds.menuItem(divider=True, parent=menu)
        checkBoxSelected = aToolsMod.getUserPref("saveAfterPlayblasting", default=True)
        cmds.menuItem("saveAfterPlayblastingMenu", label='Save Maya File After Playblasting', checkBox=checkBoxSelected, command=self.setSaveAfterPlayblastingPref, parent=menu) 
        cmds.menuItem(divider=True, parent=menu)
        cmds.menuItem               (label="Duplicate Selected Camera", command=self.duplicateCamera,   parent=menu)
        cmds.menuItem               (label="Playblast Viewport",        command=self.playblastViewport, parent=menu)
        cmds.menuItem               (label="Play Last Playblast",       command=self.playLastPlayblast, parent=menu)
    
    def setSaveAfterPlayblastingPref(self, onOff):
        self.setPref("saveAfterPlayblasting", onOff)
    
    def setPref(self, pref, onOff):
        aToolsMod.setUserPref(pref, onOff)      

               
    def playblastViewport(self, *args):
        currCamera = utilMod.getCurrentCamera()
        if currCamera: 
            self.doPlayblast(currCamera)
        else:
            cmds.warning( "Please set focus on a viewport" )
             
    def playblastCamera(self, *args): 
        camera = animMod.getShotCamera()
        if camera: self.doPlayblast(camera)
               
    def doPlayblast(self, camera):
        
        G.TU_movie              = None
        G.TU_audioFile          = None
        G.TU_audioOffsetSec     = None        
        winName                 = 'playblastWindow'
        overscan                = cmds.getAttr("%s.overscan"%camera)   
        audioTrack              = cmds.timeControl(G.playBackSliderPython, query=True, sound=True)
        rangeVisible            = cmds.timeControl(G.playBackSliderPython, query=True, rangeVisible=True )  
        widthHeight             = utilMod.getRenderResolution()  
        
        if cmds.window(winName, query=True, exists=True): cmds.deleteUI(winName)
        
        window                  = cmds.window(winName, widthHeight=widthHeight)
        form                    = cmds.formLayout()
        editor                  = cmds.modelEditor()
        column                  = cmds.columnLayout('true')
        
        cmds.formLayout( form, edit=True, attachForm=[(column, 'top', 0), (column, 'left', 0), (editor, 'top', 0), (editor, 'bottom', 0), (editor, 'right', 0)], attachNone=[(column, 'bottom'), (column, 'right')], attachControl=(editor, 'left', 0, column))
        cmds.modelEditor(editor, edit=True, camera=camera, activeView=True)
        cmds.showWindow( window )
        cmds.window( winName, edit=True, topLeftCorner=(0, 0), widthHeight=[200,200])        
        utilMod.cameraViewMode(editor)        
        cmds.setAttr("%s.overscan"%camera, 1)
        
        
        if rangeVisible:
            range = animMod.getTimelineRange(float=False)
            rFrom   = range[0]
            rTo     = range[1]-1
        else:
            rFrom = cmds.playbackOptions(query=True, minTime=True)
            rTo   = cmds.playbackOptions(query=True, maxTime=True)
        

        if G.currentStudio == None:
            G.TU_movie = cmds.playblast(format="qt", sound=audioTrack, startTime=rFrom ,endTime=rTo , viewer=1, showOrnaments=0, offScreen=True, fp=4, percent=50, compression="png", quality=70, widthHeight=widthHeight, clearCache=True)
            
        else:
            
            fps             = mel.eval("currentTimeUnitToFPS") 
            if audioTrack:
                G.TU_audioFile      = cmds.sound(audioTrack, query=True, file=True)
                audioOffset         = cmds.sound(audioTrack, query=True, offset=True)
                G.TU_audioOffsetSec = str((rFrom - audioOffset)/-fps)
                
            movieName       = cmds.playblast(format="image", startTime=rFrom ,endTime=rTo , viewer=0, showOrnaments=0, offScreen=True, fp=4, percent=50, compression="jpg", quality=70, widthHeight=widthHeight, clearCache=True)
            if movieName: 
                G.TU_movie           = "%s.%s-%s#.jpg"%(movieName.split(".")[0], int(rFrom), int(rTo))
                if audioTrack:  G.TU_audioOffsetSec = audioOffset
                self.playMovie(G.TU_movie, G.TU_audioFile, G.TU_audioOffsetSec)
            
        if cmds.window(winName, query=True, exists=True): cmds.deleteUI(winName)
        
        cmds.setAttr("%s.overscan"%camera, overscan)
        
        if not G.TU_movie: return
        save = aToolsMod.getUserPref("saveAfterPlayblasting", default=True)
        if save and not rangeVisible: cmds.file(save=True)
            
                
    def playMovie(self, movie, audioFile, audioOffsetSec):     
        
        
        if not movie: 
            cmds.warning( "No movie to play." )
            return
        
            

        
        
        
    def playLastPlayblast(self, *args):   
    
        self.playMovie(G.TU_movie, G.TU_audioFile, G.TU_audioOffsetSec)
                
    def duplicateCamera(self, *args):
        sel         = cmds.ls(selection=True)
        camNode     = utilMod.getCamFromSelection(sel)
        
        if camNode:           
            dupCamNode          = cmds.camera()            
            camTransformNode    = camNode[0]
            camShapeNode        = camNode[1] 
            dupCamTransformNode = dupCamNode[0]
            dupCamShapeNode     = dupCamNode[1] 

            utilMod.transferAttributes(camTransformNode, dupCamTransformNode)
            utilMod.transferAttributes(camShapeNode, dupCamShapeNode)
            G.aToolsBar.align.align([dupCamTransformNode], camTransformNode)
            cmds.select(dupCamTransformNode) 
            
            return
                        
        cmds.warning("No camera was created.")
                        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    