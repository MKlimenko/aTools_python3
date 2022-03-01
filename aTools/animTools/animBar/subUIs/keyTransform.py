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

import importlib
from maya import cmds
from maya import mel
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod;                    
from aTools.commonMods import utilMod;                  
from aTools.commonMods import animMod;                  
from aTools.commonMods import commandsMod;              
from aTools.commonMods import aToolsMod
from aTools.animTools.animBar.subUIs import tangents;   importlib.reload(tangents) 
from aTools.animTools.animBar.subUIs.specialTools_subUIs import mirror;   importlib.reload(mirror) 

Mirror = mirror.Mirror()

G.KT_pushClick  = False     
G.KT_sliderMode = None     



class KeyTransform_Gui(uiMod.BaseSubUI):
        
    def createLayout(self):
        keyTransform        = KeyTransform()        
        nudge               = Nudge()      
        ts                  = KeyTransformSlider_Gui()
        valueList           = [0.01, 0.05, "", 0.10, 0.20, 0.50, "", 1.00, 1.50, 2.00, 3.00, 5.00, "", 10.00, 20.00]      
        
        cmds.rowLayout(numberOfColumns=22, parent=self.parentLayout)
        
        # precision transform
        cmds.iconTextButton         (style='iconAndTextVertical', w=self.wb, h=self.hb, image= uiMod.getImagePath("keyTransform_-"), highlightImage= uiMod.getImagePath("keyTransform_- copy"), command=lambda *args: keyTransform.applyPrecise(keyTransform.getPrecisionValue()*-1),    annotation="Decrease precise transform")
        cmds.floatField             ("precisionNumber", minValue=0.01, precision=2, step=.05, value=0.5,                                                                                                                    annotation="Set precise transform value\nRight click for pre-defined values")    
        cmds.popupMenu()
        for loopValueList in valueList:
            if loopValueList == "":
                cmds.menuItem( divider=True )
            else:
                cmds.menuItem       ("menu%s"%loopValueList, label=str(loopValueList), command=lambda loopValueList=loopValueList, *args: keyTransform.setPrecisionValue(loopValueList))    
        cmds.iconTextButton         (style='iconAndTextVertical', w=self.wb, h=self.hb, image= uiMod.getImagePath("keyTransform_+"), highlightImage= uiMod.getImagePath("keyTransform_+ copy"), command=lambda *args: keyTransform.applyPrecise(keyTransform.getPrecisionValue()),       annotation="Increase precise transform")
        
        #reset
        cmds.iconTextButton         (style='iconAndTextVertical', w=self.wb, h=self.hb, image= uiMod.getImagePath("keyTransform_reset"), highlightImage= uiMod.getImagePath("keyTransform_reset copy"), command=keyTransform.resetValue,                                       annotation="Reset value to default\nRight click for options")
        cmds.popupMenu()
        cmds.menuItem               (label="Translate",         command=lambda *args: keyTransform.resetValue(["Translate"])) 
        cmds.menuItem               (label="Rotate",            command=lambda *args: keyTransform.resetValue(["Rotate"])) 
        cmds.menuItem               (label="Scale",             command=lambda *args: keyTransform.resetValue(["Scale"]))   
        cmds.menuItem( divider=True )
        cmds.menuItem               (label="Translate, Rotate and Scale",             command=lambda *args: keyTransform.resetValue(["Translate", "Rotate", "Scale"]))  
        #key
        cmds.iconTextButton         (style='iconAndTextVertical', w=self.wb, h=self.hb, image= uiMod.getImagePath("keyTransform_keykey"), highlightImage= uiMod.getImagePath("keyTransform_keykey copy"), command=keyTransform.shareEachOtherKeys,                            annotation="Share each other keys\nRight click for options")
        cmds.popupMenu()
        cmds.menuItem               (label="All Keys",          command=lambda *args: keyTransform.shareEachOtherKeys("all"))
       
        #nudge
        cmds.iconTextButton         (style='iconAndTextVertical', w=self.wb, h=self.hb, image= uiMod.getImagePath("keyTransform_nudge_left"), highlightImage= uiMod.getImagePath("keyTransform_nudge_left copy"), command=lambda *args: nudge.nudgeKey(-1),          annotation="Nudge key left\nRight click for options")
        nudge.popupMenu("left")
        cmds.floatField             ("nudgeEnterField", minValue=1, precision=0, step=1, value=10, annotation="Set precise nudge value", visible=False, w=1)    
        cmds.popupMenu()
        cmds.menuItem   (label="Hide",          command=lambda *args:nudge.toggleEnterField(False)) 
        cmds.iconTextButton         (style='iconAndTextVertical', w=self.wb, h=self.hb, image= uiMod.getImagePath("keyTransform_nudge_right"), highlightImage= uiMod.getImagePath("keyTransform_nudge_right copy"), command=lambda *args: nudge.nudgeKey(1),         annotation="Nudge key right\nRight click for options")
        nudge.popupMenu("right")
              
        #slider      
        cmds.text( label=' ', h=1 )
        ts.populateSlider()          
        cmds.text( label=' ', h=1 )


        ts.setSliderMode(ts.getSliderMode()) # set the saved slider mode
        ts.delWindows() # delete if open
        
        # end createLayout
        

class KeyTransformSlider_Gui(object):
    
    def __init__(self):
        self.winName            = "keyTransformSliderWin"
        self.toolbarName        = "keyTransformSliderToolbar"
        self.allWin             = [self.winName, self.toolbarName]
        self.barOffset          = 0
        self.height             = 60
        self.defaultValues      = {}
        self.optimizedValues    = {}
        self.invertRules        = None
        self.maxSelObjs         = 1
        self.blendToFramelabelA         = '  A      '
        self.blendToFramelabelB         = '      B  '
        self.blendToFrameValuesA        = []
        self.blendToFrameValuesB        = []
        self.blendToFrameCurrentValueA  = None
        self.blendToFrameCurrentValueB  = None
        self.defaultMode                = "blendToFrame"
        self.defaultModifiers           = {"shift"          :"blendToNeighbors",
                                           "ctrl"           :"scaleFromNeighborLeft",
                                           "alt"            :"scaleFromNeighborRight",
                                           "ctrlShift"      :"blendToDefault",
                                           "altShift"       :"pullPush",
                                           "altCtrl"        :"easeInOut",
                                           "altCtrlShift"   :"blendToMirror"
                                           }
        self.modifiers                   = self.getModifiers()
        
        
        
        self.modeDividers                = [3, 7]
        self.modesDict = [   {  
                        "mode":     "pullPush",
                        "icon":     "pp",
                        "function": "setPushValues"
                        },{
                        "mode":     "noise",
                        "icon":     "no",
                        "function": "setNoiseValues"
                        },{
                        "mode":     "easeInOut",
                        "icon":     "ea",
                        "function": "setEaseInOut"
                        },{
                        "mode":     "blendToDefault",
                        "icon":     "bd",
                        "function": "setBlendScaleValues"
                        },{
                        "mode":     "blendToNeighbors",
                        "icon":     "bn",
                        "function": "setBlendScaleValues"
                        },{
                        "mode":     "blendToMirror",
                        "icon":     "bm",
                        "function": "setBlendScaleValues"
                        },{
                        "mode":     "blendToFrame",
                        "icon":     "bf",
                        "function": "setBlendScaleValues"
                        },{
                        "mode":     "scaleFromDefault",
                        "icon":     "sd",
                        "function": "setBlendScaleValues"
                        },{
                        "mode":     "scaleFromAverage",
                        "icon":     "sa",
                        "function": "setBlendScaleValues"
                        },{
                        "mode":     "scaleFromNeighborLeft",
                        "icon":     "sl",
                        "function": "setBlendScaleValues"
                        },{
                        "mode":     "scaleFromNeighborRight",
                        "icon":     "sr",
                        "function": "setBlendScaleValues"
                        }
                     ]
        
        
        
    
    def createWin(self):
        
        self.mainWin        = cmds.window(self.winName, sizeable=True)
        self.buttonHeight   = self.height -10
    
        # Main frame
        cmds.frameLayout("mainFrameLayout", labelVisible=False, w=10, borderVisible=False)
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach=([2, 'right', self.barOffset]))
        cmds.text(label="")
        cmds.rowLayout("keyTransformSliderParentLayout", numberOfColumns=100)
        
        self.populateButtons()
           
        # shows toolbar
        cmds.toolBar(self.toolbarName, area='bottom', content=self.mainWin, allowedArea=['bottom'], height=self.height)
    
    
    def populateSlider(self, mode="default"):
        keySliderW          = 137 if mode=="default" else 111
        imageW              = 30 
        buttPerc            = ((imageW/2)/(keySliderW/100.)) 
        blendToFrameTxtA    = None
        blendToFrameAnn     = "Left click: pick current frame\nRight click: pick from history or current objects keys"
        labelA = self.blendToFramelabelA
        labelB = self.blendToFramelabelB
        if self.blendToFrameCurrentValueA: labelA = " %s"%self.blendToFrameCurrentValueA
        if self.blendToFrameCurrentValueB: labelB = "%s "%self.blendToFrameCurrentValueB
        
        
        cmds.formLayout             ("keyTransformSliderFormLayout%s"%mode, h=32, w=keySliderW)
        
        if mode == "default":   textValue   = cmds.text("keyTransformSliderText", label="100", visible=False)
        else:                   textValue   = cmds.text("keyTransformSliderText_%s"%mode, label="100", visible=False)
        
        slider      = cmds.floatSlider      ('keyTransformSlider%s'%mode, w=keySliderW-1, min=0, max=2, value=1, dragCommand=lambda x, mode=mode, *args: self.applyKeyTransform('keyTransformSlider%s'%mode, mode),   changeCommand=lambda x, mode=mode, *args: self.releaseKeyTransform('keyTransformSlider%s'%mode, mode))
          
        if mode == "default":
            modeButton = cmds.iconTextButton    ("keyTransformSliderButton", style='iconAndTextVertical', w=imageW, h=16, annotation="Key Transform Slider Mode")
            self.popUpModes()
            
            blendToFrameTxtA   = cmds.iconTextButton("keyTransformSliderBlendToFrameA", font="smallPlainLabelFont", style='iconAndTextCentered',  w=45, label=labelA, align="left", command=lambda *args:self.blendToFrameSet('A'), ann=blendToFrameAnn); self.blendToFramePopUp('A')
            blendToFrameTxtB   = cmds.iconTextButton("keyTransformSliderBlendToFrameB", font="smallPlainLabelFont", style='iconAndTextCentered',  w=45, label=labelB, align="right", command=lambda *args:self.blendToFrameSet('B'), ann=blendToFrameAnn); self.blendToFramePopUp('B')
        
        else:
            icon        = self.getIcon(mode)
            modeButton  = cmds.iconTextButton("keyTransformSliderButton_%s"%mode, style='iconAndTextVertical', w=imageW, h=16, image= uiMod.getImagePath("keyTransform_%s"%icon), highlightImage= uiMod.getImagePath("keyTransform_%s copy"%icon), command=lambda mode=mode, *args:self.setSliderMode(mode), annotation="Set this mode in the main toolbar")
             
            if mode == "blendToFrame": 
                blendToFrameTxtA   = cmds.iconTextButton("keyTransformSliderBlendToFrameToolbarA", font="smallPlainLabelFont", style='iconAndTextCentered',  w=45, label=labelA, align="left", command=lambda *args:self.blendToFrameSet('A'), ann=blendToFrameAnn); self.blendToFramePopUp('A')
                blendToFrameTxtB   = cmds.iconTextButton("keyTransformSliderBlendToFrameToolbarB", font="smallPlainLabelFont", style='iconAndTextCentered',  w=45, label=labelB, align="right", command=lambda *args:self.blendToFrameSet('B'), ann=blendToFrameAnn); self.blendToFramePopUp('B')
       
        
        #pre set buttons
        preSetDict      = {"values":[1., .50, .15, .05], "buttonPositions":[0,10,20,30]}
        topPos          = 60 if mode == "default" else 35
        for n, loopValue in enumerate(preSetDict["values"]):
            value           = loopValue
            buttonPosition  = preSetDict["buttonPositions"][n]
            b = cmds.iconTextButton(style='iconAndTextVertical',  w=13, h=13, command=lambda value=value, mode=mode, slider=slider, *args: self.tickKeyTransform(slider, mode, (1.+(value*-1))), ann=int(value*100), image= uiMod.getImagePath('keyTransform_dot_a'), highlightImage= uiMod.getImagePath('keyTransform_dot_a copy'))
            cmds.formLayout    ("keyTransformSliderFormLayout%s"%mode, edit=True, attachPosition=[(b, 'top', 0, topPos), (b, 'left', 0, buttonPosition)])
            b = cmds.iconTextButton(style='iconAndTextVertical',  w=13, h=13, command=lambda value=value, mode=mode, slider=slider, *args: self.tickKeyTransform(slider, mode, (1.+value)),      ann=int(value*100), image= uiMod.getImagePath('keyTransform_dot_a'), highlightImage= uiMod.getImagePath('keyTransform_dot_a copy'))
            cmds.formLayout    ("keyTransformSliderFormLayout%s"%mode, edit=True, attachPosition=[(b, 'top', 0, topPos), (b, 'right', 0, 100-buttonPosition)])
        
        
        cmds.formLayout             ("keyTransformSliderFormLayout%s"%mode, edit=True, 
                                    attachPosition=[
                                                     (modeButton, 'left', 0, 50-buttPerc), 
                                                     (modeButton, 'right', 0, 100-(50-buttPerc)), 
                                                     (modeButton, 'top', -5, 0), 
                                                     (textValue, 'left', 0, 50-buttPerc), 
                                                     (textValue, 'right', 0, 100-(50-buttPerc)), 
                                                     (textValue, 'top', 21, 0), 
                                                     (slider, 'top', -4, 45)
                                                    ])

            

        # blend to frame
        if blendToFrameTxtA:
            cmds.formLayout         ("keyTransformSliderFormLayout%s"%mode, edit=True, 
                                    attachPosition=[
                                                     (blendToFrameTxtA, 'left', 0, 0),
                                                     (blendToFrameTxtB, 'right', 0, 100),
                                                     (blendToFrameTxtA, 'top', 0, 0), 
                                                     (blendToFrameTxtB, 'top', 0, 0)
                                                    ])
        
        #ALT SHIFT CTRL 
        if mode != "default":
            label       = utilMod.toTitle(mode).replace("Right", "R").replace("Left", "L")           
            t1          = cmds.text( label=label, align='center', font="smallPlainLabelFont")
            modButton   = cmds.iconTextButton("keyTransformSliderModButton_%s"%mode, style='textOnly', font="smallObliqueLabelFont", label="                         ", align="center") 
            self.popUpModifiers(mode)    
            
            cmds.formLayout             ("keyTransformSliderFormLayout%s"%mode, edit=True, h=65, attachPosition=[
                                                                                                                 (t1, 'left', 0, 0),
                                                                                                                 (t1, 'right', 0, 100), 
                                                                                                                 (t1, 'bottom', 15, 100), 
                                                                                                                 (modButton, 'left', 0, 0),
                                                                                                                 (modButton, 'right', 0, 100),
                                                                                                                 (modButton, 'bottom', -5, 100), 
                                                                                                                 (slider, 'top', 0, 18)
                                                                                                                 ])
        
        
        cmds.setParent('..')
    
    def populateButtons(self):
        
        for n, loopMode in enumerate(self.modesDict):            
            mode    = loopMode["mode"]
            divider = n in self.modeDividers            
            
            if divider: cmds.image(image=uiMod.getImagePath("keyTransform_divider"))
            cmds.text( label=' ', h=1 )
            self.populateSlider(mode)
            cmds.text( label=' ', h=1 )
        
        self.refreshModifiersButtons()
        
        cmds.iconTextButton(style='iconOnly', h=25, w=25, image=uiMod.getImagePath("keyTransform_x"), highlightImage=uiMod.getImagePath("keyTransform_x copy"), command=self.toggleAllModesToolbar, annotation="Hide toolbar")
                        
    def delWindows(self):        
        
        for loopWin in self.allWin:
            if cmds.window(loopWin, query=True, exists=True):  cmds.deleteUI(loopWin)
            if cmds.toolBar(loopWin, query=True, exists=True): cmds.deleteUI(loopWin)

    def toggleAllModesToolbar(self, *args):
        if cmds.toolBar(self.toolbarName, query=True, exists=True):
            self.delWindows()
        else:
            self.createWin()
    
    #=================================
    
    def setBlendToFrameTxtVisible(self, mode, mod=False):
               
        visible     = (mode == "blendToFrame" and not mod)  
        cmds.iconTextButton("keyTransformSliderBlendToFrameA", edit=True, visible=visible)
        cmds.iconTextButton("keyTransformSliderBlendToFrameB", edit=True, visible=visible)   
        
        
    def blendToFrameSet(self, aB, frame=None):
        
        if not frame: 
            frame = int(cmds.currentTime(query=True))
        
        exec("if %s not in self.blendToFrameValues%s: self.blendToFrameValues%s.append(%s)"%(frame, aB, aB, frame))
        exec("self.blendToFrameCurrentValue%s = %s"%(aB, frame))
        
        cmds.iconTextButton("keyTransformSliderBlendToFrame%s"%aB, edit=True, label=frame)
        if cmds.iconTextButton("keyTransformSliderBlendToFrameToolbar%s"%aB, query=True, exists=True):
            cmds.iconTextButton("keyTransformSliderBlendToFrameToolbar%s"%aB, edit=True, label=frame)
     
    def blendToFrameClearHistory(self, *args):
        self.blendToFrameValuesA        = []
        self.blendToFrameValuesB        = [] 
        self.blendToFrameCurrentValueA  = None
        self.blendToFrameCurrentValueB  = None
        
        
        labelA = self.blendToFramelabelA
        labelB = self.blendToFramelabelB
        cmds.iconTextButton("keyTransformSliderBlendToFrameA", edit=True, label=labelA)
        if cmds.iconTextButton("keyTransformSliderBlendToFrameToolbarA", query=True, exists=True):
            cmds.iconTextButton("keyTransformSliderBlendToFrameToolbarA", edit=True, label=labelA)
        cmds.iconTextButton("keyTransformSliderBlendToFrameB", edit=True, label=labelB)
        if cmds.iconTextButton("keyTransformSliderBlendToFrameToolbarB", query=True, exists=True):
            cmds.iconTextButton("keyTransformSliderBlendToFrameToolbarB", edit=True, label=labelB)
        
    def blendToFramePopUp(self, aB):
        menu = cmds.popupMenu()
        cmds.popupMenu(menu, edit=True, postMenuCommand=lambda *args:self.populateBlendToFrameHistory(menu, aB))
        
        
    def populateBlendToFrameHistory(self, menu, aB, *args):
        uiMod.clearMenuItems(menu)
                
        items = sorted(list(set(self.blendToFrameValuesA + self.blendToFrameValuesB)))   
        
        for loopItem in items:
            cmds.menuItem(label=loopItem, command=lambda x, aB=aB, loopItem=loopItem, *args: self.blendToFrameSet(aB, loopItem), parent=menu)
            
        
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]         
        
        if animCurves:
            keyTimes = animMod.getTarget("keyTimes", animCurves, getFrom)
            keyTimes = sorted(utilMod.mergeLists(keyTimes))  
            
            if len(keyTimes) > 0:
                cmds.menuItem(divider=True,  parent=menu)
                subMenu     = cmds.menuItem(label="Select Key", subMenu=True, command=self.blendToFrameClearHistory, parent=menu)
                divider     = None
                currFrame   = cmds.currentTime(query=True) 
                for loopItem in keyTimes:
                    loopItem = int(loopItem)
                    if not divider:
                        if loopItem == currFrame:   cmds.menuItem(divider=True,  parent=subMenu)
                        elif loopItem > currFrame: divider = cmds.menuItem(divider=True,  parent=subMenu)
                    cmds.menuItem(label=loopItem, command=lambda x, aB=aB, loopItem=loopItem, *args: self.blendToFrameSet(aB, loopItem), parent=subMenu)
            
            
                    
        if len(items) > 0:
            cmds.menuItem(divider=True,  parent=menu)
            cmds.menuItem(label="Clear History", command=self.blendToFrameClearHistory, parent=menu)
        
    #===================================================================
    
    def getIcon(self, mode):
        for loopMode in self.modesDict:
            if mode == loopMode["mode"]:
                return loopMode["icon"]

    def popUpModes(self):
        cmds.popupMenu(postMenuCommand=self.populateModes, button=1)
        cmds.popupMenu(postMenuCommand=self.populateModes, button=3)
    
    def populateModes(self, menu, *args):
        
        uiMod.clearMenuItems(menu)
        
        cmds.radioMenuItemCollection(parent=menu)
        sliderMode  = self.getSliderMode()
        
        for n, loopMode in enumerate(self.modesDict):
            mode            = loopMode["mode"]
            label           = utilMod.toTitle(mode)
            icon            = loopMode["icon"]
            radioSelected   = (sliderMode == mode)
            divider         = n in self.modeDividers
            
            if divider: cmds.menuItem(divider=True, parent=menu)
            cmds.menuItem(label=label, radioButton=radioSelected,  command=lambda x, mode=mode, *args: self.setSliderMode(mode), parent=menu)
        
        cmds.menuItem(divider=True, parent=menu)
        cmds.menuItem(label="Toggle All Modes Toolbar", command=self.toggleAllModesToolbar, parent=menu)
        
       
    def popUpModifiers(self, mode):
        menu = cmds.popupMenu(button=1)
        cmds.popupMenu(menu, edit=True, postMenuCommand=lambda menu=menu, *args:self.populateModifiers(menu, mode))
        menu = cmds.popupMenu(button=3)
        cmds.popupMenu(menu, edit=True, postMenuCommand=lambda menu=menu, *args:self.populateModifiers(menu, mode))
    
    def populateModifiers(self, menu, mode, *args):
        
        uiMod.clearMenuItems(menu)
        
        cmds.radioMenuItemCollection(parent=menu)
        
        mod             = ""
        radioSelected   = (self.getModeModifier(mode) == mod)
        cmds.menuItem(label="None", radioButton=radioSelected, command=lambda x, mode=mode, mod=mod, *args: self.setModifier(mode, mod), parent=menu)
        
        for loopKey in list(self.defaultModifiers.keys()):
            
            mod             = loopKey
            label           = utilMod.toTitle(mod).replace(" ", "+")
            radioSelected   = (self.getModeModifier(mode) == mod)
            
            cmds.menuItem(label=label, radioButton=radioSelected,  command=lambda x, mode=mode, mod=mod, *args: self.setModifier(mode, mod), parent=menu)
         
        cmds.menuItem(divider=True, parent=menu)
        cmds.menuItem(label="Load Defaults", command=self.loadDefaultModifiers, parent=menu)
                 
        
    def getSliderMode(self, *args):
        
        if not G.KT_sliderMode:
            G.KT_sliderMode = aToolsMod.loadInfoWithUser("userPrefs", "sliderMode")
            
        if not G.KT_sliderMode: 
            G.KT_sliderMode = self.defaultMode
        
        return G.KT_sliderMode
    
    def setModifier(self, mode, mod):
        
        
        for loopKey in list(self.defaultModifiers.keys()):
            if self.modifiers[loopKey] == mode:
                self.modifiers[loopKey] = ""
            
        
        self.modifiers[mod]  = mode
        
        aToolsMod.saveInfoWithUser("userPrefs", "sliderModifiers", self.modifiers)
        
        self.refreshModifiersButtons()
        
    def loadDefaultModifiers(self, *args):
        
        for loopMod in list(self.defaultModifiers.keys()):
            mode = self.defaultModifiers[loopMod]
            mod  = loopMod
            self.setModifier(mode, mod)
            

        
    def refreshModifiersButtons(self):
        
        for loopMode in self.modesDict:
            mode            = loopMode["mode"]
            label           = "(%s)"%utilMod.toTitle(self.getModeModifier(mode)).replace(" ", "+") if self.getModeModifier(mode) else "..."
            
            cmds.iconTextButton("keyTransformSliderModButton_%s"%mode, edit=True, label=label)
        
        self.setModifiersAnn()


    def getModifiers(self):
        
        modifiers = aToolsMod.loadInfoWithUser("userPrefs", "sliderModifiers")
        if not modifiers: modifiers = self.defaultModifiers
        
        return modifiers
    
    def getModeModifier(self, mode, *args):        
         
        for loopKey in list(self.defaultModifiers.keys()):
            if self.modifiers[loopKey] == mode:
                return loopKey
            
        return ""
            
    def setModifiersAnn(self):
        
        ann  = ""
        
        for loopKey in list(self.defaultModifiers.keys()):
            loopMode = self.modifiers[loopKey]
            if loopMode != "": ann += "%s: %s\n"%(utilMod.toTitle(loopKey).replace(" ", "+"), utilMod.toTitle(loopMode))            
        
        sliderAnnotation = "%s\n\n%s\nRight click for options"%(utilMod.toTitle(G.KT_sliderMode), ann)
        
        cmds.iconTextButton ("keyTransformSliderButton", edit=True, ann=sliderAnnotation)
        
    
    def getIndex(self, mode):
        for n, loopMode in enumerate(self.modesDict): 
            if mode in loopMode["mode"]:
                return n
    
    
    def setSliderMode(self, mode, *args):
        index   = self.getIndex(mode)
        
        if  not index: 
            index = 0
            mode  = self.modesDict[index]["mode"]
            
        label           = utilMod.toTitle(mode)
        icon            = self.modesDict[index]["icon"]                
        G.KT_sliderMode = mode
        
        cmds.iconTextButton ("keyTransformSliderButton", edit=True, image= uiMod.getImagePath("keyTransform_%s"%icon), highlightImage= uiMod.getImagePath("keyTransform_%s copy"%icon))
        
        self.setBlendToFrameTxtVisible(mode)
        self.setModifiersAnn()
        
        aToolsMod.saveInfoWithUser("userPrefs", "sliderMode", mode) 
            
            
    
    def getKeyTransformValue(self, slider):
        value   = cmds.floatSlider(slider, query=True, value=True)
        rValue  = 1+((value-1)*abs(value-1))
            
        return rValue
    
    def tickKeyTransform(self, slider, mode, tValue, *args):    
        
        self.applyKeyTransform(slider, mode, tValue, unselectObjects=False)     
        #G.KT_pushClick      = False  
        self.releaseKeyTransform(slider, mode)
        
            
    def delayIcon(self, mode):
        
        if mode == "default":            
            index   = self.getIndex(G.KT_sliderMode)
            icon    = self.modesDict[index]["icon"]            
            
            cmds.text ("keyTransformSliderText", edit=True, visible=False)         
            cmds.iconTextButton ("keyTransformSliderButton", edit=True, image= uiMod.getImagePath("keyTransform_%s"%icon), highlightImage= uiMod.getImagePath("keyTransform_%s copy"%icon))
              
            self.setBlendToFrameTxtVisible(G.KT_sliderMode, False)
            
        else:            
            index   = self.getIndex(mode)
            icon    = self.modesDict[index]["icon"]   
            
            cmds.text ("keyTransformSliderText_%s"%mode, edit=True, visible=False)
            cmds.iconTextButton ("keyTransformSliderButton_%s"%mode, edit=True, image= uiMod.getImagePath("keyTransform_%s"%icon))
        
    def releaseKeyTransform(self, slider, mode, *args):
        function = lambda *args:self.releaseKeyTransformDef(slider, mode)
        G.deferredManager.sendToQueue(function, 1, "KT_release")
   
    def releaseKeyTransformDef(self, slider, mode, *args):
        
        cmds.floatSlider(slider, edit=True, value=1)  
        
        mel.eval("toggleAutoLoad graphEditor1OutlineEd true;")
                 
        G.aToolsBar.timeoutInterval.setTimeout((lambda mode=mode, *args: self.delayIcon(mode)), .5)          
        
        cmds.undoInfo(stateWithoutFlush=False)
        #round flat numbers
        if G.KT_flatKeys:
            tValue = int(G.KT_lastTValue)
            G.KT_function(G.KT_gMode, G.KT_animCurves, G.KT_indexes, G.KT_keyValues, G.KT_keyTimes, G.KT_keysSel, G.KT_keyTangentsY, G.KT_keyTangentsX, tValue, G.KT_pushClick)
        
        #reset stored values
        self.optimizedValues    = {}
        G.KT_pushClick          = False
        
        if len(self.selObjs) > 0: 
            cmds.select(self.selObjs)                    
        
        #cmds.undoInfo(closeChunk=True)  
        cmds.undoInfo(stateWithoutFlush=True)

    
    def applyKeyTransform(self, slider, mode, tValue=None, unselectObjects=True, *args):
                
        tValue      = tValue if tValue is not None else self.getKeyTransformValue(slider)     

        if G.KT_pushClick:
            if tValue == 0 or tValue == 2: G.KT_lockZero = True  
            
            if G.KT_lockZero and (.97 < tValue < 1.03): 
                cmds.floatSlider(slider, edit=True, value=1)  
                tValue = 1.0000001
        
         
        showValue   = abs(round((tValue-1.)*100., 2))
        if showValue >= 1 or showValue == 0: showValue = int(round(showValue))
                
        if mode == "default":   cmds.text ("keyTransformSliderText", edit=True, label=showValue)
        else:                   cmds.text ("keyTransformSliderText_%s"%mode, edit=True, label=showValue)
        
        if not G.KT_pushClick: #first time
            
            mel.eval("toggleAutoLoad graphEditor1OutlineEd false;") 
            
            G.KT_pushClickDef   = False
            G.KT_lockZero       = False
            G.KT_openChunk      = True
            
            if mode == "default": cmds.text ("keyTransformSliderText", edit=True, visible=True)
            else:                 cmds.text ("keyTransformSliderText_%s"%mode, edit=True, visible=True)
                           
            
            mod  = uiMod.getModKeyPressed()
            
            if mode == "default": 
                mode = self.getSliderMode()
                
                if mod:
                    allModifiers = self.getModifiers()
                    modeMod = allModifiers[mod]
                    if modeMod != "": 
                        mode = modeMod
    
                        index   = self.getIndex(mode)
                        icon    = self.modesDict[index]["icon"]
         
                        cmds.iconTextButton ("keyTransformSliderButton", edit=True, image=uiMod.getImagePath("keyTransform_%s"%icon))
           
                self.setBlendToFrameTxtVisible(mode, mod)
                        
            
            G.KT_gMode          = mode
            index               = self.getIndex(mode)
            function            = self.modesDict[index]["function"]
            G.KT_function       = eval("self.%s"%function)
            G.KT_animCurves     = G.KT_indexes = G.KT_keyValues = G.KT_keyTimes = G.KT_keysSel = G.KT_keyTangentsY = G.KT_keyTangentsX = None
            
            
            
            cmds.undoInfo(openChunk=True)
          
            
            getCurves       = animMod.getAnimCurves()
            G.KT_animCurves = getCurves[0]
            getFrom         = getCurves[1]
            self.selObjs    = []
            G.KT_keysSel    = animMod.getTarget("keysSel", G.KT_animCurves, getFrom)
            
               
            if G.KT_animCurves:
                
                #create key   
                if utilMod.mergeLists(G.KT_keysSel) == []: 
                    commandsMod.setSmartKey(animCurves=G.KT_animCurves)   
                    G.KT_keysSel    = animMod.getTarget("keysSel", G.KT_animCurves, getFrom) 
                    
                
                G.KT_keyTimes     = animMod.getTarget("keyTimes", G.KT_animCurves)
                G.KT_keyValues    = animMod.getTarget("keyValues", G.KT_animCurves)                
                lists             = ["G.KT_animCurves", "G.KT_indexes", "G.KT_keyValues", "G.KT_keyTimes", "G.KT_keysSel"]
                   
                
                
                if function not in ["setBlendScaleValues", "setEaseInOut"] :
                    G.KT_keyTangentsY = animMod.getTarget("keyTangentsY", G.KT_animCurves)
                    G.KT_keyTangentsX = animMod.getTarget("keyTangentsX", G.KT_animCurves)
                    lists.extend(["G.KT_keyTangentsY", "G.KT_keyTangentsX"])
                
                
                #unselect if multiple objects (faster)
                if getFrom == "timeline":
                    self.selObjs = cmds.ls(selection=True)
                    if len(self.selObjs) > self.maxSelObjs and unselectObjects:
                        cmds.select(self.selObjs[-1])
                    else:
                        self.selObjs = []
                
                
                # add tail and head keys for values and times
                for n, loopCurve in enumerate(G.KT_animCurves):
                    
                    if len(G.KT_keyTimes[n]) == 1:
                        inOffsetTime    = 1
                        inOffsetVal     = 0  
                        outOffsetTime   = 1
                        outOffsetVal    = 0                    
                    else:                        
                        inOffsetTime    = (G.KT_keyTimes[n][1]-G.KT_keyTimes[n][0])
                        inOffsetVal     = (G.KT_keyValues[n][1]-G.KT_keyValues[n][0])
                        outOffsetTime   = (G.KT_keyTimes[n][-1]-G.KT_keyTimes[n][-2])
                        outOffsetVal    = (G.KT_keyValues[n][-1]-G.KT_keyValues[n][-2])
                    
                    #head keys    
                    G.KT_keyValues[n].insert(0, G.KT_keyValues[n][0]-inOffsetVal)
                    G.KT_keyTimes[n].insert(0, G.KT_keyTimes[n][0]-inOffsetTime)
                    G.KT_keyValues[n].insert(0, G.KT_keyValues[n][0]-inOffsetVal)
                    G.KT_keyTimes[n].insert(0, G.KT_keyTimes[n][0]-inOffsetTime)
                    
                    #tail keys                    
                    G.KT_keyValues[n].append(G.KT_keyValues[n][-1]+outOffsetVal)
                    G.KT_keyTimes[n].append(G.KT_keyTimes[n][-1]+outOffsetTime)
                    G.KT_keyValues[n].append(G.KT_keyValues[n][-1]+outOffsetVal)
                    G.KT_keyTimes[n].append(G.KT_keyTimes[n][-1]+outOffsetTime)
                
                
                                
                 
                G.KT_indexes = []
                keysSelTmp = list(G.KT_keysSel)
                for i, loopCurves in enumerate(G.KT_animCurves):
                    G.KT_indexes.append([])
                    firstTime = True
                    keysSelTmp[i] = list(G.KT_keysSel[i])
                    for n, loopkeyTimes in enumerate(G.KT_keyTimes[i]):
                        for loopKeySel in keysSelTmp[i]:
                            if keysSelTmp[i][0] == loopkeyTimes:
                                if firstTime:
                                    G.KT_indexes[i].append([])
                                    firstTime = False
                                G.KT_indexes[i][-1].append(n)
                                keysSelTmp[i].pop(0)
                                break
                            else:
                                firstTime = True
                                
                                
                
                #add head and tail for G.KT_indexes
                for i, loopA in enumerate(G.KT_indexes):#each curve
                    for ii, loopB in enumerate(loopA):#each segment
                        G.KT_indexes[i][ii].insert(0, ((G.KT_indexes[i][ii][0])-1))
                        G.KT_indexes[i][ii].append((G.KT_indexes[i][ii][-1])+1)
                        
                        
                
                
                

                #===OPTIMIZATION=====                
                #optimize filter keys sel   
                """
                if not mode in ["blendToDefault", "scaleFromDefault", "blendToMirror", "blendToFrame"]:  
                    for n, loopCurve in enumerate(G.KT_animCurves):
                        for s, segment in enumerate(G.KT_indexes[n]):
                            
                            fi = G.KT_indexes[n][s][0]
                            li = G.KT_indexes[n][s][-1]
                            ti = li - fi
                            
                            fv = G.KT_keyValues[n][fi]
                            lv = G.KT_keyValues[n][li]                          
                            
                            for x in xrange(ti-2, -1, -1):                            
                                v = G.KT_keyValues[n][fi+x+1]
                                if v == fv == lv:
                                    del G.KT_keysSel[n][x]
                               
                
                #delete empty G.KT_animCurves based on G.KT_keysSel
                indexToDelete   = []
                keysSelTmp      = list(G.KT_keysSel)
                for n, loopKeysSel in enumerate(keysSelTmp):
                    if len(loopKeysSel) == 0: indexToDelete.append(n)

                for loopList in lists:
                    for loopIndex in sorted(indexToDelete, reverse=True):
                        exec("del %s[%s]"%(loopList, loopIndex))
                    
                #===============================
                """
                
            
        if G.KT_animCurves:
            G.KT_pushClick  = True
            function        = lambda *args:self.defApply(G.KT_function, [G.KT_gMode, G.KT_animCurves, G.KT_indexes, G.KT_keyValues, G.KT_keyTimes, G.KT_keysSel, G.KT_keyTangentsY, G.KT_keyTangentsX, tValue, G.KT_pushClickDef])
            
            G.deferredManager.removeFromQueue("KT")
            G.deferredManager.sendToQueue(function, 1, "KT")
            
            
            
        
            
    def defApply(self, function, args):        
        functionStr    = "function(" 
        
        for n, loopArg in enumerate(args):
            functionStr += "args[%s]"%n
            if n == len(args)-1: functionStr += ")"
            else:                functionStr += ", "     
        
        if not G.KT_openChunk: cmds.undoInfo(stateWithoutFlush=False)
        exec(functionStr)
        if G.KT_openChunk: 
            cmds.undoInfo(closeChunk=True)
            #cmds.undoInfo(stateWithoutFlush=False)
            G.KT_openChunk = False
        else: cmds.undoInfo(stateWithoutFlush=True)
            
        
        G.KT_pushClickDef = True
        
                       
    
    def setPushValues(self, mode, animCurves, indexes, keyValues, keyTimes, keysSel, keyTangentsY, keyTangentsX, tValue, pushClick):
        
        # set values
        for n, loopCurve in enumerate(animCurves):
            for s, segment in enumerate(indexes[n]):
                
                fv = keyValues[n][indexes[n][s][0]]
                lv = keyValues[n][indexes[n][s][-1]]                
                tv = lv - fv
                ff = keyTimes[n][indexes[n][s][0]]
                lf = keyTimes[n][indexes[n][s][-1]]
                tf = lf - ff
                
                # angle when the slider value is 0
                angle   = animMod.getAngle(ff, lf, fv, lv)
                p       = tValue
    
                    
                for i, loopKeySel in enumerate(indexes[n][s]):
                    if 1 <= i <= len(indexes[n][s])-2:
                        index = indexes[n][s][i]-2
                        
                        #key
                        v  = keyValues[n][index+2]  
                        
                        #optimization
                        #if fv == lv == v: continue
                        
                        
                        f  = keyTimes[n][index+2]
                        a  = ((tv/tf)*(f-ff))+fv
                        nv = ((v-a)*p)+a
                        
                        #tangent
                        iy = keyTangentsY[n][(index)*2] 
                        oy = keyTangentsY[n][((index)*2)+1]
                        ix = keyTangentsX[n][(index)*2] 
                        ox = keyTangentsX[n][((index)*2)+1]
                        
                        inTangentType  = cmds.keyTangent(loopCurve, query=True, index=(index, index), inTangentType=True)[0]
                        outTangentType = cmds.keyTangent(loopCurve, query=True, index=(index, index), outTangentType=True)[0]
                        
                        if inTangentType  == "fixed": cmds.keyTangent(loopCurve, index=(index, index), inAngle=angle)
                        if outTangentType == "fixed": cmds.keyTangent(loopCurve, index=(index, index), outAngle=angle)
                        
                        zeroY = cmds.keyTangent(loopCurve, query=True, index=(index, index), iy=True, oy=True)
                        ziy = zeroY[0]
                        zoy = zeroY[1]
                        zeroX = cmds.keyTangent(loopCurve, query=True, index=(index, index), ix=True, ox=True)
                        zix = zeroX[0]
                        zox = zeroX[1]  
                        
                        if p <= 1:
                            niy = ziy + (iy * p) - (ziy * p)
                            noy = zoy + (oy * p) - (zoy * p)
                            nix = zix + (ix * p) - (zix * p)
                            nox = zox + (ox * p) - (zox * p)
                        else:
                            niy = iy * p
                            noy = oy * p
                            nix = ix 
                            nox = ox
                       
                        # apply
                        cmds.keyframe(loopCurve, index=(index, index), valueChange=nv)
                        if inTangentType  == "fixed": cmds.keyTangent(loopCurve, index=(index, index), iy=niy, ix=nix)
                        if outTangentType == "fixed": cmds.keyTangent(loopCurve, index=(index, index), oy=noy, ox=nox)
 
       
        
                    
    def setNoiseValues(self, mode, animCurves, indexes, keyValues, keyTimes, keysSel, keyTangentsY, keyTangentsX, tValue, pushClick):
        # set values
        for n, loopCurve in enumerate(animCurves):
            for s, segment in enumerate(indexes[n]):
                
                
                p       = tValue
                if p <=1: p=.5+(p/2)
    
                    
                for i, loopKeySel in enumerate(indexes[n][s]):
                    
                    if 1 <= i <= len(indexes[n][s])-2:
                        index = indexes[n][s][i]-2
                        
                        if index < len(keyValues[n])-4:
                    
                            fv = keyValues[n][index+1]
                            lv = keyValues[n][index+3]                
                            tv = lv - fv
                            ff = keyTimes[n][index+1]
                            lf = keyTimes[n][index+3]
                            tf = lf - ff
                            
                            #key
                            v  = keyValues[n][index+2]  
                            f  = keyTimes[n][index+2]
                            a  = ((tv/tf)*(f-ff))+fv
                            newv = ((v-a)*p)+a
                            
                            #calculate previous and next key
                        
                            pfv = keyValues[n][index-1]
                            plv = keyValues[n][index+2-1]                
                            ptv = plv - pfv
                            pff = keyTimes[n][index-1]
                            plf = keyTimes[n][index+2-1]
                            ptf = plf - pff
                            #key
                            pv  = keyValues[n][index+2-1]  
                            pf  = keyTimes[n][index+2-1]
                            pa  = ((ptv/ptf)*(pf-pff))+pfv
                            pnv = ((pv-pa)*.5)+pa
                            
                            nfv = keyValues[n][index+1]
                            nlv = keyValues[n][index+2+1]                
                            ntv = nlv - nfv
                            nff = keyTimes[n][index+1]
                            nlf = keyTimes[n][index+2+1]
                            ntf = nlf - nff
                            #key
                            nv  = keyValues[n][index+2+1]  
                            nf  = keyTimes[n][index+2+1]
                            na  = ((ntv/ntf)*(nf-nff))+nfv
                            nnv = ((nv-na)*.5)+na
                            
                         
                            # angle when the slider value is 0
                            angle   = animMod.getAngle(pf, nf, pnv, nnv)
                            
                            
                            #tangent
                            iy = keyTangentsY[n][(index)*2] 
                            oy = keyTangentsY[n][((index)*2)+1]
                            ix = keyTangentsX[n][(index)*2] 
                            ox = keyTangentsX[n][((index)*2)+1]
                            
                            inTangentType  = cmds.keyTangent(loopCurve, query=True, index=(index, index), inTangentType=True)[0]
                            outTangentType = cmds.keyTangent(loopCurve, query=True, index=(index, index), outTangentType=True)[0]
                            
                            #if pushClick: cmds.undoInfo(stateWithoutFlushG.KT_pushClick                           if inTangentType  == "fixed": cmds.keyTangent(loopCurve, index=(index, index), inAngle=angle)
                            if outTangentType == "fixed": cmds.keyTangent(loopCurve, index=(index, index), outAngle=angle)
                            #if pushClick: cmds.undoInfo(stateWithoutFlush=True) 
                            
                            zeroY = cmds.keyTangent(loopCurve, query=True, index=(index, index), iy=True, oy=True)
                            ziy = zeroY[0]
                            zoy = zeroY[1]
                            zeroX = cmds.keyTangent(loopCurve, query=True, index=(index, index), ix=True, ox=True)
                            zix = zeroX[0]
                            zox = zeroX[1]  
                            
                            if p <= 1:
                                niy = ziy + (iy * tValue) - (ziy * tValue)
                                noy = zoy + (oy * tValue) - (zoy * tValue)
                                nix = zix + (ix * tValue) - (zix * tValue)
                                nox = zox + (ox * tValue) - (zox * tValue)
                            else:
                                niy = iy * p
                                noy = oy * p
                                nix = ix 
                                nox = ox
                           
                            # apply
                            #if pushClick: cmds.undoInfo(stateWithoutFlush=False)
                            cmds.keyframe(loopCurve, index=(index, index), valueChange=newv)
                            if inTangentType  == "fixed": cmds.keyTangent(loopCurve, index=(index, index), iy=niy, ix=nix)
                            if outTangentType == "fixed": cmds.keyTangent(loopCurve, index=(index, index), oy=noy, ox=nox)
                            
                            
                            
           
                    
    def setBlendScaleValues(self, mode, animCurves, indexes, keyValues, keyTimes, keysSel, keyTangentsY, keyTangentsX, tValue, pushClick):
        # set values
        
        if pushClick: # avoid losing the middle point value            
            if G.KT_lastTValue > 1 and tValue < 1:
                self.setBlendScaleValues(mode, animCurves, indexes, keyValues, keyTimes, keysSel, keyTangentsY, keyTangentsX, 1.0000001, pushClick)
            elif G.KT_lastTValue < 1 and tValue > 1:            
                self.setBlendScaleValues(mode, animCurves, indexes, keyValues, keyTimes, keysSel, keyTangentsY, keyTangentsX, 1, pushClick)
                
        
        if mode == "default": mode  = self.getSliderMode()
        p                           = tValue*2-1
                
        if mode == "blendToMirror": 
            mirrorCurves    = animMod.getMirrorObjs(animCurves)
            if not pushClick: self.invertRules     = Mirror.getInvertRules()   
            
        if mode == "blendToFrame": 
            if tValue <=1: 
                if not self.blendToFrameCurrentValueA:
                    if tValue <=.97: cmds.warning("You need to select a frame first. Please go to some frame and hit the button A")
                    return
            else: 
                if not self.blendToFrameCurrentValueB:
                    if tValue >=1.03: cmds.warning("You need to select a frame first. Please go to some frame and hit the button B")
                    return   
            

            
        if "blend" in mode:
            if tValue <=1: p = tValue
            else:          p = 2-tValue  
             
        if p == 0 and not G.KT_flatKeys:     
            p = 0.0000001
            G.KT_flatKeys = True
        else:
            G.KT_flatKeys = False
                        
        if pushClick: # second time on
            if G.KT_lastValue == 0: G.KT_scaleValue = p
            else:                   G.KT_scaleValue = 1/G.KT_lastValue*p
        else: #just first time
            G.KT_scaleValue = p    
                    
        for n, loopCurve in enumerate(animCurves):
            
            if mode == "blendToFrame": 
                if tValue <=1:  f = self.blendToFrameCurrentValueA
                else:           f = self.blendToFrameCurrentValueB
                
                if loopCurve not in self.optimizedValues: self.optimizedValues[loopCurve] = {}                                
                if f not in self.optimizedValues[loopCurve]:
                    self.optimizedValues[loopCurve][f] = cmds.keyframe(loopCurve, query=True, eval=True, time=(f,f), valueChange=True)[0]
                pivot = self.optimizedValues[loopCurve][f]
            
            if mode == "blendToDefault":
                if loopCurve not in self.defaultValues:
                    pivot                       = animMod.getDefaultValue(loopCurve)
                    self.defaultValues[loopCurve]  = pivot
                else:
                    pivot = self.defaultValues[loopCurve]
                    
            if mode == "blendToMirror":
                mCurve              = mirrorCurves[n] 
                isCenterCurve       = (mCurve == None) 
                if isCenterCurve: mCurve = loopCurve
                if not cmds.objExists(mCurve): continue
                
                if not pushClick:                
                    mirrorInvertValue           = Mirror.mirrorInvert(loopCurve, isCenterCurve, self.invertRules)
                  
            if mode == "scaleFromDefault": 
                if loopCurve not in self.defaultValues:
                    pivot                       = animMod.getDefaultValue(loopCurve)
                    self.defaultValues[loopCurve]  = pivot
                else:
                    pivot = self.defaultValues[loopCurve]
            
            
            for s, segment in enumerate(indexes[n]):
         
                if mode == "blendToNeighbors":
                    fv = keyValues[n][indexes[n][s][0]]
                    lv = keyValues[n][indexes[n][s][-1]] 
                
                if mode == "scaleFromAverage": 
                    segValues = []
                    for loopIndex in indexes[n][s]:
                        segValues.append(keyValues[n][loopIndex])
                    segValues.pop(0)
                    segValues.remove(segValues[-1])
                    maxV    = max(segValues)
                    minV    = min(segValues)
                    pivot   = (maxV+minV)/2
                    
                if mode == "scaleFromNeighborLeft":
                    fv = keyValues[n][indexes[n][s][0]]                    
                    pivot = fv
                    
                if mode == "scaleFromNeighborRight":
                    lv = keyValues[n][indexes[n][s][-1]]
                    pivot = lv
                
                   
                for i, loopKeySel in enumerate(indexes[n][s]):
                    if 1 <= i <= len(indexes[n][s])-2:
                        index   = indexes[n][s][i]-2
                        v       = keyValues[n][index+2]  
                        
                        if mode == "blendToNeighbors": 
                            if tValue <=1: pivot = fv
                            else:          pivot = lv
                            
                        
                        if mode == "blendToMirror":
                            f  = keyTimes[n][index+2]
                            
                            if not pushClick:
                                if isCenterCurve:                   pivot = v * mirrorInvertValue
                                else:                               pivot = cmds.keyframe(mCurve, query=True, eval=True, time=(f,f), valueChange=True)[0] * mirrorInvertValue
                                if mCurve not in self.optimizedValues: self.optimizedValues[mCurve] = {}                                
                                self.optimizedValues[mCurve][f]        = pivot                            
                            else:
                                pivot = self.optimizedValues[mCurve][f]
                        
                        #optimization
                        #if v == pivot: continue
                        
                        # apply===============================================
                        cmds.scaleKey(loopCurve, index=(index, index), valuePivot=pivot, valueScale=G.KT_scaleValue)                    
                        
         
        G.KT_lastValue  = p  
        G.KT_lastTValue = tValue  
        
        
    
    def setEaseInOut(self, mode, animCurves, indexes, keyValues, keyTimes, keysSel, keyTangentsY, keyTangentsX, tValue, pushClick):
        
        for n, loopCurve in enumerate(animCurves):
            for s, segment in enumerate(indexes[n]):
                
                fv = keyValues[n][indexes[n][s][0]]
                lv = keyValues[n][indexes[n][s][-1]]                
                tv = lv - fv
                ff = keyTimes[n][indexes[n][s][0]]
                lf = keyTimes[n][indexes[n][s][-1]]
                tf = lf - ff
                
                strenght = (tValue-1)*100
                
                for i, loopKeySel in enumerate(indexes[n][s]):
                    if 1 <= i <= len(indexes[n][s])-2:
                        index = indexes[n][s][i]-2
                
                        
                        currTime    = keyTimes[n][index+2] - ff
                        timePos     = currTime/tf
                        maxStr      = 10.
                        str         = (abs(strenght)/100.)*(maxStr-1)+1
    
                        
                        outValue    = tv*(((abs(timePos-1))**str)*-1 + 1) + fv
                        inValue     = tv*(timePos**str) + fv
                        
                        if strenght > 0:    value = outValue
                        else:               value = inValue
                    
                    
                        # apply
                        #if pushClick: cmds.undoInfo(stateWithoutFlush=False)
                        cmds.keyframe(loopCurve ,edit=True, index=(index, index), valueChange=value)
                        #if pushClick: cmds.undoInfo(stateWithoutFlush=True)  
                
                        
    

#==========================================================================

class KeyTransform(object):
    
    def __init__(self):
        
        if G.aToolsBar.keyTransform: return
        G.aToolsBar.keyTransform = self

    def setPrecisionValue(self, n, *args):
        cmds.floatField("precisionNumber", edit=True, value=n)    
    
    def getPrecisionValue(self, *args):
        return cmds.floatField("precisionNumber", query=True, value=True)
        
    def applyPrecise(self, tValue, *args):
        
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]
        
        keysSel     = animMod.getTarget("keysSel", animCurves, getFrom)
        keyTimes    = animMod.getTarget("keyTimes", animCurves)
    
        if animCurves:
            for n, loopCurve in enumerate(animCurves):
                if getFrom == "timeline":
                    time = [animMod.getTimelineTime()]
            
                else:
                    time = [(loopTime,loopTime) for loopTime in keysSel[n]]
                                
                for loopTime in time:            
                    cmds.setKeyframe(loopCurve, time=loopTime, insert=True)
                    value = cmds.keyframe(loopCurve, query=True, time=loopTime, valueChange=True)[0]    
                    cmds.keyframe(loopCurve, edit=True, time=loopTime, valueChange=value+tValue)
    
    def resetValue(self, trs=[], *args):
            
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]
            
        if animCurves:
            
            keysSel     = animMod.getTarget("keysSel", animCurves, getFrom)
            
            for n, loopCurve in enumerate(animCurves):
                
                if trs != []:
                    apply = False
                    for loopTrs in trs:
                        if eval("animMod.isAnimCurve%s(loopCurve)"%loopTrs): 
                            apply = True
                            break
                    if not apply: continue
                    
                
                time    = [(loopTime,loopTime) for loopTime in keysSel[n]]
                value   = animMod.getDefaultValue(loopCurve) 
                
                if getFrom == "timeline" and len(time) ==0:
                    time = [animMod.getTimelineTime()]
                                
                for loopTime in time:            
                    cmds.setKeyframe(loopCurve, time=loopTime, insert=False) 
                    cmds.keyframe(loopCurve, edit=True, time=loopTime, valueChange=value)
                    
                    tangType = cmds.keyTangent(loopCurve, query=True, time=loopTime, inTangentType=True, outTangentType=True)
                    if tangType[1] != "step":
                        cmds.keyTangent(loopCurve, time=loopTime, inTangentType="auto", outTangentType="auto")
                        
                        
        else:
            objects = animMod.getObjsSel()
            if objects:
                
                channelboxSelObjs = animMod.channelBoxSel()
                if channelboxSelObjs:
    
                    for loopObjAttr in channelboxSelObjs:
                        value   = animMod.getDefaultValue(loopObjAttr) 
                        cmds.setAttr(loopObjAttr, value)
                          
                else:                
                    allChannels = animMod.getAllChannels(objects)
                    for n, loopObj in enumerate(allChannels):
                        if not loopObj or len(loopObj) == 0: continue
                        for loopAttr in loopObj:
                            objAttr = "%s.%s"%(objects[n], loopAttr)
                            if not cmds.objExists(objAttr):continue
                            if not cmds.getAttr(objAttr, settable=True): continue
                            value   = animMod.getDefaultValue(objAttr) 
                            cmds.setAttr(objAttr, value)
            
              
     
    
    def shareEachOtherKeys(self, keys="selected", *args):
        
        cmds.waitCursor(state=True)    
        
        getCurves       = animMod.getAnimCurves()
        animCurves      = getCurves[0]
        getFrom         = getCurves[1]  
    
        if keys == "selected":
            keysSel     = animMod.getTarget("keysSel", animCurves, getFrom)
        else:        
            keysSel     = animMod.getTarget("keyTimes", animCurves, getFrom)
        
        blendKeys = utilMod.mergeLists(keysSel) 
        
        animMod.createDummyKey(select=True)
        
        getCurves       = animMod.getAnimCurves(True)
        animCurves      = getCurves[0]
         
        #key
        for loopKey in blendKeys:
            if animCurves:
                time = (loopKey, loopKey)
                cmds.setKeyframe(animCurves, time=time, insert=True)
                
                
        animMod.deleteDummyKey()
    
        cmds.waitCursor(state=False)        
        
    def inbetween(self, value, mode="add", *args):
            
        getCurves       = animMod.getAnimCurves()
        animCurves      = getCurves[0]
        getFrom         = getCurves[1]
        
        keysIndexSel    = animMod.getTarget("keysIndexSel", animCurves, getFrom)
        keyIndexTimes   = animMod.getTarget("keyIndexTimes", animCurves)
        currentTime     = cmds.currentTime(query=True)
        
        if animCurves:
            
            for n, loopCurve in enumerate(animCurves):
                maxIndex = max([max(key) for key in keyIndexTimes])
                
                if len(keysIndexSel[n]) == 0:#no keys selected
                    prevKey   = cmds.findKeyframe(loopCurve, time=(currentTime, currentTime), which="previous")
                    prevIndex = cmds.keyframe(loopCurve, query=True, time=(prevKey, prevKey), indexValue=True)[0]
                    keysIndexSel[n].append(prevIndex)
                
                tailIndex = keysIndexSel[n][-1]+1
                
                if tailIndex <= maxIndex and len(keysIndexSel[n]) == 1: keysIndexSel[n].append(tailIndex)
                keysIndexSel[n].remove(keysIndexSel[n][0])
                
                for loopIndex in keysIndexSel[n]:
                    seqIndex = (loopIndex, maxIndex)
                    if mode=="add":
                        #check intersection
                        
                        cmds.keyframe(loopCurve, option="over", relative=True, index=seqIndex, timeChange=value)
                    elif mode=="set":
                        index = (loopIndex-1, loopIndex-1)
                        curKey    = cmds.keyframe(loopCurve, query=True, index=index, timeChange=True)[0]
                        nextKey   = cmds.findKeyframe(loopCurve, time=(curKey,curKey), which="next")
                        setValue  = value-(nextKey-curKey)
                        cmds.keyframe(loopCurve, option="over", relative=True, index=seqIndex, timeChange=setValue)
                        
                        
    def inbetweenUI(self, *args):
        windowName = "setInbetweenWin"
        widthHeight = (90, 90)
        if cmds.window(windowName, query=True, exists=True): cmds.deleteUI(windowName)
        window = cmds.window(windowName, title="Set Inbetween", widthHeight=widthHeight)
        cmds.gridLayout(numberOfColumns=3, cellWidthHeight=(30, 30))
        
        for n in range(9):
            num = n+1
            cmds.button(label=str(num), command=lambda num=num, *args: self.inbetween(num, "set"))
            
        cmds.showWindow(window)
        cmds.window(window, edit=True, widthHeight=widthHeight)
  
    
class Nudge(object):
    
    def __init__(self):
        
        if G.aToolsBar.nudge: return
        G.aToolsBar.nudge       = self
        self.applyToEverything  = False

    def popupMenu(self, leftRight):
        cmds.popupMenu(postMenuCommand=lambda *args:self.populateMenu(leftRight, args))
        
    def populateMenu(self, leftRight, *args):
        menu = args[0][0]
        
        uiMod.clearMenuItems(menu)  
        
        values = [2,4,10,20,50,100]
        for loopValue in values:
            if leftRight == "left": loopValue = loopValue*-1
            cmds.menuItem   (label=abs(loopValue),          command=lambda x, loopValue=loopValue, *args: self.nudgeKey(loopValue), parent=menu)  
      
        cmds.menuItem   (label="Custom",          command=lambda *args: self.toggleEnterField(True), parent=menu) 
        cmds.menuItem(divider=True, parent=menu )
        cmds.menuItem   (label="Nudge Everything in the Scene",   checkBox=self.applyToEverything,       command=lambda *args: self.toggleEnterField(True, args), parent=menu) 
    
    def toggleEnterField(self, onOff=True, *args):        
        
        self.applyToEverything = False
        
        if len(args) > 0: 
            onOff = args[0][0]
            self.applyToEverything = onOff
            
        if onOff:
            cmds.floatField     ("nudgeEnterField", edit=True, visible=True, w=50) 
            return
        
        
        cmds.floatField         ("nudgeEnterField", edit=True, visible=False, w=1)  
    
    
                                             
    def nudgeKey(self, value, *args):
        
        if cmds.floatField             ("nudgeEnterField", query=True, visible=True):
            if abs(value) == 1: value = cmds.floatField ("nudgeEnterField", query=True, value=True) * value
            
            if self.applyToEverything: 
                self.nudgeEverything(value)
                return
            
        
            
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]
        keyExists   = None
        
        keysSel     = animMod.getTarget("keysSel", animCurves, getFrom)
        
        if animCurves:
            if getFrom == "timeline":
                
                
                range       = animMod.getTimelineRange()            
                time        = (range[0], range[1])
                prevKey     = cmds.findKeyframe(time=(range[0],range[0]), which="previous")
                nextKey     = cmds.findKeyframe(time=(range[1]-1,range[1]-1), which="next")
                currentTime = cmds.currentTime(query=True)
                
                # prevents first and last keys bug
                if prevKey >= time[0]: prevKey -=2
                if nextKey <= time[1]: nextKey +=2
                
                #check if keySel has something
                for loopArray in keysSel:
                    if len(loopArray) > 0:
                        keyExists = True
                        break
                        
                if keyExists:  
                    if time[0]+value > prevKey and time[1]+value < nextKey:
                        cmds.keyframe(animCurves, option="over", relative=True, time=time, timeChange=value)
                        cmds.currentTime(currentTime+value)
                else:
                    if value > 0:
                        time        = (prevKey, prevKey)
                        value       = currentTime
                        
                    else:
                        time        = (nextKey, nextKey)
                        value       = currentTime
                    
                    cmds.keyframe(animCurves, option="over", relative=False, time=time, timeChange=value)
                
            else:
                cmds.keyframe(animation="keys", option="over", relative=True, timeChange=value)    
                cmds.snapKey(animation="keys")
    
            #--------
            self.toggleEnterField(False)
        
    
    def nudgeEverything(self, value):
        
        cmds.waitCursor(state=True)
        allCurvesinScene = cmds.ls(type=["animCurveTA","animCurveTL","animCurveTT","animCurveTU"])
        cmds.keyframe(allCurvesinScene, option="over", relative=True, timeChange=value)
        self.toggleEnterField(False)
        cmds.waitCursor(state=False)
            
    
    
    
    
                

      
    
                
                
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            