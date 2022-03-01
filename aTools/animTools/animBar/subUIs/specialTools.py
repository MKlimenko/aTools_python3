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
import os
from maya import cmds
from maya import mel
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod;   importlib.reload(uiMod)
from aTools.commonMods import utilMod; importlib.reload(utilMod)
from aTools.commonMods import animMod; importlib.reload(animMod)

MODULES = ["align","selectSets","mirror","spaceSwitch","tempCustomPivot","animationCopier","fakeConstrain", "microTransform", "transformAll"]

# import subUI modules
for loopMod in MODULES:
    exec("from aTools.animTools.animBar.subUIs.specialTools_subUIs import %s; importlib.reload(%s)"%(loopMod, loopMod))


class SpecialTools_Gui(uiMod.BaseSubUI):
        
    def createLayout(self):
        
        cmds.rowLayout(numberOfColumns=20, parent=self.parentLayout)
  
        #SELECTION SETS
        SelectSets = selectSets.SelectSets()
        cmds.iconTextButton("selectSetsBtn", style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_select_sets"), highlightImage= uiMod.getImagePath("specialTools_select_sets copy"), w=self.wb, h=self.hb, command=SelectSets.toggleToolbar,        annotation="Quick select set groups\nRight click for options")
        SelectSets.popupMenu()
        
        #ALIGN
        Align = align.Align()
        cmds.iconTextButton(style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_align"),          highlightImage= uiMod.getImagePath("specialTools_align copy"),          w=self.wb, h=self.hb, command=Align.alignSelection,                annotation="Align selection\nSelect the slaves and a master object\nRight click for options")
        Align.popupMenu()
         
        #MIRROR
        Mirror = mirror.Mirror()
        cmds.iconTextButton("mirrorBtn", style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_mirror"),         highlightImage= uiMod.getImagePath("specialTools_mirror copy"),         w=self.wb, h=self.hb, command=Mirror.start,               annotation="Mirror values to opposite ctrls\nHighlight the timeline for applying on a range\nRight click for options\n\nCtrl+click: Select mirror objects\nShift+click: Add mirror objects to selection")
        Mirror.popupMenu()
       
        #SPACE SWITCH
        SpaceSwitch = spaceSwitch.SpaceSwitch()
        cmds.iconTextButton(style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_space_switcher"),         highlightImage= uiMod.getImagePath("specialTools_space_switcher copy"),         w=self.wb, h=self.hb, annotation="Space switcher\nIf the constraint controller is not the same as the attribute controller, select it too")
        SpaceSwitch.popupMenu()
        
        #TEMP CUSTOM PIVOT
        TempCustomPivot = tempCustomPivot.TempCustomPivot()
        cmds.iconTextButton("TempCustomPivotBtn", style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_create_temp_custom_pivot"),         highlightImage= uiMod.getImagePath("specialTools_create_temp_custom_pivot copy"),         w=self.wb, h=self.hb, command=TempCustomPivot.create,               annotation="Temporary custom pivot\nRight click for options")
        TempCustomPivot.popupMenu()
      
        #ANIMATION COPIER
        AnimationCopier = animationCopier.AnimationCopier()
        cmds.iconTextButton(style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_copy_animation"), highlightImage= uiMod.getImagePath("specialTools_copy_animation copy"), w=self.wb, h=self.hb, command=AnimationCopier.copyAnimation,        annotation="Animation Copier\nRight click for options")
        AnimationCopier.popupMenu()                        
        
        #FAKE CONSTRAIN
        FakeConstrain = fakeConstrain.FakeConstrain()
        cmds.iconTextButton("fakeConstrainBtn", style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_fake_constrain"), highlightImage= uiMod.getImagePath("specialTools_fake_constrain copy"), w=self.wb, h=self.hb, command=FakeConstrain.copyPaste,        annotation="Fake Constrain\nClick once to copy objects position relative to the last selected\nGo to another frame or select a range and click again to paste\nChanging the current selection will flush the copy cache\n\nRight click for options")
        FakeConstrain.popupMenu()
 
        # motion trail is disabled, please use the built-in
        # #MOTION TRAIL
        # MotionTrail = motionTrail.MotionTrail()
        # MotionTrail.toolBarButton  = cmds.iconTextButton("motionTrailBtn", style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_motion_trail"),   highlightImage= uiMod.getImagePath("specialTools_motion_trail copy"),    w=self.wb, h=self.hb, command=MotionTrail.switch,          annotation="Motion trail\nRight click for options")
        # MotionTrail.popupMenu()
        # #cmds.iconTextButton("motionTrailBtnOLD", style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_motion_trail"),   highlightImage= uiMod.getImagePath("specialTools_motion_trail copy"),    w=self.wb, h=self.hb, command=self.motionTrail,          annotation="Motion trail")
        
        
        #MICRO TRANSFORM
        MicroTransform = microTransform.MicroTransform()
        cmds.iconTextButton("microTransformBtn", style='iconAndTextVertical', image= uiMod.getImagePath("specialTools_micro_transform"),         highlightImage= uiMod.getImagePath("specialTools_micro_transform copy"),         w=self.wb, h=self.hb, command=MicroTransform.switch, annotation="Enable micro transform\nRight click for options")
        MicroTransform.popupMenu()
  
       
        #TRANSFORM ALL
        TransformAll = transformAll.TransformAll()
        cmds.iconTextButton         ("transformAllBtn", style='iconAndTextVertical',     w=self.wb, h=self.hb, image= uiMod.getImagePath("specialTools_transform_all"),   highlightImage= uiMod.getImagePath("specialTools_transform_all copy"),                     command=TransformAll.switch,   annotation="Enable transform all keys\nWill affect selected range or all keys if no range is selected\nCtrl+click will toggle blend range mode")
        #TransformAll.popupMenu()
         
        

# end createLayout

    



    

