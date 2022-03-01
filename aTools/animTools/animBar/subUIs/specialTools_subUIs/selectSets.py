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
from maya import OpenMaya
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod
from aTools.commonMods import aToolsMod

class SelectSets(object):
    
    def __init__(self):      
        
        G.deferredManager.removeFromQueue("SS")
        
        self.toolbar        = "aTools_Select_Sets_Bar"
        self.allWin         = [self.toolbar]
        self.barOffset      = 0
        self.defaultSetName = "aToolsSet_"
        self.height         = 50
        self.buttonHeight   = self.height -10
        self.defaultColor   = "purple"
        self.colors         = [{"name":"purple",   "value":(0.640,0.215,0.995)}, 
                               {"name":"red",      "value":(1,0.4,0.4)},  
                               {"name":"orange",   "value":(1,0.6,0.4)},  
                               {"name":"yellow",   "value":(1,0.97,0.4)}, 
                               {"name":"green",    "value":(0.44,1,0.53)},
                               {"name":"blue",     "value":(0.28,0.6,1)}, 
                               {"name":"gray",     "value":(0.5,0.5,0.5)}
                              ]
        
        self.createRenameLayoutW    = (len(self.colors)+1)*15
        self.setToRename            = None
        self.selSetButtonWidth      = {}
              
        
        G.SS_messages       = G.SS_messages or {"anim":[], "node":[], "scene":[]}
        G.SS_showColors     = G.SS_showColors or [loopColor["name"] for loopColor in self.colors]   
        G.SS_setsAndNodes   = {}
        G.SS_lastColorUsed  = G.SS_lastColorUsed or self.defaultColor 
        #G.SS_messages      = G.SS_messages or {"node":{}}
        
        self.delWindows() # delete if open
        self.saveSelectSetsDict()
        self.addSceneMessages()
        
        
    def popupMenu(self, *args):
        cmds.popupMenu()
        cmds.menuItem(subMenu=True, label='Show' , tearOff=True, postMenuCommand=self.updateshowColorsMenu)
        
        for loopColor in self.colors:
            colorName  = loopColor["name"]
            cmds.menuItem('colorMenu_%s'%colorName, label=utilMod.toTitle(colorName),   checkBox=False,  command=lambda x, colorName=colorName, *args: self.switchColor(colorName))
        
        cmds.menuItem( divider=True )
        cmds.menuItem(subMenu=True, label="Show Only")
        for loopColor in self.colors:
            colorName  = loopColor["name"]
            cmds.menuItem(label=utilMod.toTitle(colorName),   command=lambda x, colorName=colorName, *args: self.isolateColor(colorName))
        
        cmds.setParent( '..', menu=True ) 
        cmds.menuItem('colorMenuShowAll', label="Show All Colors", command=self.showAllColors)
 
        cmds.setParent( '..', menu=True )   
        cmds.menuItem(                          label="Import Select Sets",                      command=self.importSets)
        cmds.menuItem(                          label="Export Select Sets",                      command=self.exportSets)
        cmds.menuItem(                          label="Delete All",                             command=self.deleteAllSets)
        
    
    def createWin(self):     
        
        self.aToolsSets     = self.getaToolsSets() 
        self.mainWin        = cmds.window(sizeable=True)
    
        cmds.frameLayout(labelVisible=False, borderVisible=False, w=10)
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach=([2, 'right', self.barOffset]))
        cmds.text(label="")
        self.mainLayout     = cmds.rowLayout(numberOfColumns=5)
        self.limboLayout    = cmds.rowLayout(parent=self.mainLayout, w=1)
        
        self.populateSelSetsButtons()
        cmds.toolBar(self.toolbar, area='bottom', content=self.mainWin, allowedArea=['bottom'], height=self.height)
        
        self.allWin.extend([self.mainWin, self.mainLayout])
        self.highlightSelectedButtons()
        G.deferredManager.sendToQueue(self.toggleSelSetsButtonColor, 1, "SS")
        G.deferredManager.sendToQueue(self.adjustButtonsWidth, 1, "SS")
        self.addScriptJobs()   
        
        
    def refreshToolBar(self, *args):
        
        if not cmds.toolBar(self.toolbar, query=True, exists=True): return
        
        self.saveSelectSetsDict()
        G.deferredManager.sendToQueue(self.delWindows, 1, "SS")        
        if cmds.toolBar(self.toolbar, query=True, visible=True): G.deferredManager.sendToQueue(self.createWin, 1, "SS")
        


    def toggleToolbar(self, forceOff=None):
        visible = True
        
        if cmds.toolBar(self.toolbar, query=True, exists=True):
            visible = (False if forceOff else not cmds.toolBar(self.toolbar, query=True, visible=True))
            cmds.toolBar(self.toolbar, edit=True, visible=visible)
            if visible: self.adjustButtonsWidth()
        else:
            self.createWin()
            
        if visible and len(self.aToolsSets) == 0: self.turnOnCreateNewSetField() 
        
        if cmds.iconTextButton("selectSetsBtn", query=True, exists=True):
            if visible: cmds.iconTextButton("selectSetsBtn", edit=True, image=uiMod.getImagePath("specialTools_select_sets_active"), highlightImage= uiMod.getImagePath("specialTools_select_sets_active"))
            else:       cmds.iconTextButton("selectSetsBtn", edit=True, image=uiMod.getImagePath("specialTools_select_sets"), highlightImage= uiMod.getImagePath("specialTools_select_sets copy"))
    
    def saveSelectSetsDict(self):
        self.aToolsSets     = self.getaToolsSets()
        self.aToolsSetsDict = {}
        
        for loopSet in self.aToolsSets: self.aToolsSetsDict[loopSet] = cmds.sets(loopSet, query=True, nodesOnly=True)
                           
    def beforeSave(self, *args):
        self.rebuildAllSelectSets()
        
    
    def rebuildAllSelectSets(self, selSetsSel=[]):
        
        selSetsSel.extend(self.getSelectedSets())
          
        for loopSet in list(self.aToolsSetsDict.keys()):
            newSelSet = self.createSelSetIfInexistent(loopSet, self.aToolsSetsDict[loopSet])
            
            if not newSelSet: continue            
            
            self.aToolsSetsDict[newSelSet]  = self.aToolsSetsDict[loopSet]
            existentNodes                   = sorted([loopNode for loopNode in self.aToolsSetsDict[loopSet] if cmds.objExists(loopNode)])
            
            if newSelSet != loopSet: self.aToolsSetsDict.pop(loopSet, None)
            cmds.sets(existentNodes, edit=True, addElement=newSelSet)

        selSetsSel = [loopSel for loopSel in selSetsSel if cmds.objExists(loopSel)]
        #if len(selSetsSel) > 0: cmds.select(selSetsSel)#NEED FIX
        self.highlightSelectedButtons()
    
    def createSelSetIfInexistent(self, selSet, nodes):
        if not cmds.objExists(selSet):
            existentNodes = [loopNode for loopNode in nodes if cmds.objExists(loopNode)]
            if len(existentNodes) > 0: return cmds.sets(existentNodes, name=selSet, text="gCharacterSet")
            else: return
        
        return selSet
    
            
    def checkIfElementsDeleted(self, selSet):
        
        #print "checkIfElementsDeleted"
        
        if selSet not in self.aToolsSetsDict: return
        
        selSetContents  = cmds.sets(selSet, query=True, nodesOnly=True)
        dictContents    = self.aToolsSetsDict[selSet]    
        
        
        #print "selSetContents != dictContents"    , (selSetContents != dictContents)
                
        if selSetContents != dictContents: self.rebuildAllSelectSets()
            

    
    def addScriptJobs(self):
        self.clearScriptJobs() 
        
        #G.selectSetsScriptJobs.append(cmds.scriptJob(runOnce = True,  killWithScene = False, event =('PostSceneRead', self.refreshToolBar )))
        G.selectSetsScriptJobs.append(cmds.scriptJob(runOnce = True,  killWithScene = False, event =('NewSceneOpened', self.refreshToolBar )))
        G.selectSetsScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('SelectionChanged', self.highlightSelectedButtons )))
    
    def addSceneMessages(self):
        
        self.removeMessages()      
        #SCENE MESSAGES
        G.SS_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kBeforeSave, self.beforeSave))
        #G.SS_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kAfterSave, self.afterSave))
        G.SS_messages["scene"].append(OpenMaya.MSceneMessage.addCallback( OpenMaya.MSceneMessage.kAfterOpen, self.refreshToolBar))
        
    def removeMessages(self):  
        
        try:
            for loopId in G.SS_messages["scene"]:
                OpenMaya.MSceneMessage.removeCallback(loopId)
        except: pass        
        
        G.SS_messages["scene"] = []
    
    
    def populateSelSetsButtons(self):               
        # + button    
        self.plusBtn                = cmds.iconTextButton(style='iconAndTextVertical', h=25, w=25, 
                                                          image=uiMod.getImagePath("specialTools_select_sets_+"), 
                                                          highlightImage=uiMod.getImagePath("specialTools_select_sets_+ copy"), 
                                                          command=self.turnOnCreateNewSetField, 
                                                          annotation="Create new select set", 
                                                          parent=self.mainLayout
                                                          )
        
        self.selSetsLayout  = cmds.rowLayout(numberOfColumns=200, parent=self.mainLayout)
        
        # create UI
        fieldUI                     = self.createTextField("create", self.createNewSelectSet, self.turnOffCreateNewSetField)
        self.createNewSetLayout        = fieldUI["mainLayout"]
        self.createNewSetTextField     = fieldUI["textField"]  
        
        #rename UI
        fieldUI                     = self.createTextField("rename", self.renameSelectSet, self.turnOffRenameSetField)
        self.renameSetLayout        = fieldUI["mainLayout"]
        self.renameSetTextField     = fieldUI["textField"]  
        
        #sel sets buttons     
        for loopSet in self.aToolsSets: self.createSelSetButton(loopSet)
        
        # Show All Button
        self.showAllColorsButton    = cmds.iconTextButton(style='iconOnly', h=25, w=1, 
                                            image=uiMod.getImagePath("specialTools_select_sets_show_all"), 
                                            highlightImage=uiMod.getImagePath("specialTools_select_sets_show_all copy"), 
                                            command=self.showAllColors, annotation="Show all colors",
                                            parent=self.mainLayout,
                                            visible=False
                                            )        
        
        # X button    
        cmds.iconTextButton(style='iconOnly', h=25, w=25, 
                            image=uiMod.getImagePath("specialTools_x"), 
                            highlightImage=uiMod.getImagePath("specialTools_x copy"), 
                            command=self.toggleToolbar, annotation="Hide toolbar",
                            parent=self.mainLayout
                            )

    def createTextField(self, createRename, enterCommand, offCommand):
        
        mainLayout      = cmds.columnLayout(w=1, columnWidth=self.createRenameLayoutW, 
                                            parent=self.selSetsLayout, 
                                            visible=False
                                            )
        fistRowLayout   = cmds.rowLayout(numberOfColumns=3, parent=mainLayout)
        textField       = cmds.textField(height=20, width=self.createRenameLayoutW-21, 
                                             alwaysInvokeEnterCommandOnReturn=True,
                                             parent=fistRowLayout,
                                             enterCommand=enterCommand
                                             )
        # X button text field 
        cmds.iconTextButton(style='iconOnly', h=18, w=18, 
                            image=uiMod.getImagePath("specialTools_x"), 
                            highlightImage=uiMod.getImagePath("specialTools_x copy"), 
                            command=offCommand, annotation="Cancel",
                            parent=fistRowLayout
                            )
        
        cmds.rowLayout(numberOfColumns=len(self.colors)+1, parent=mainLayout)
        for loopColor in self.colors:
            colorName  = loopColor["name"]
            colorValue = loopColor["value"]
            cmds.iconTextButton("colorButton%s%s"%(createRename, colorName),
                                style='iconOnly', 
                                bgc=colorValue, 
                                height=15, width=15, 
                                command=lambda colorName=colorName, *args: enterCommand(colorName=colorName)
                                ) 
            
        return {"mainLayout":mainLayout, "textField":textField}     
        
    def guessNewSetName(self):
        return ""
    
    def turnOnCreateNewSetField(self):
        
        cmds.iconTextButton (self.plusBtn, edit=True, visible=False, w=1)
        cmds.columnLayout(self.createNewSetLayout, edit=True, visible=True, w=self.createRenameLayoutW) 
        self.turnOffRenameSetField()
        cmds.textField(self.createNewSetTextField, edit=True, text=self.guessNewSetName())
        self.highlightColorSelection()
        cmds.setFocus(self.createNewSetTextField)  
        self.adjustButtonsWidth() 
    
    def turnOffCreateNewSetField(self):
        
        if not cmds.columnLayout(self.createNewSetLayout, query=True, visible=True): return
        
        cmds.iconTextButton (self.plusBtn, edit=True, visible=True, w=25)
        cmds.columnLayout(self.createNewSetLayout, edit=True, visible=False, w=1) 
        viewports = [view for view in cmds.getPanel(type='modelPanel') if view in cmds.getPanel(visiblePanels=True)]
        if len(viewports) > 0: cmds.setFocus(viewports[0])
        self.adjustButtonsWidth() 

 

    def turnOnRenameSetField(self, renameSet):
                
        extracted           = self.extractInfoFromSelSet(renameSet)
        selSetName          = extracted["selSetName"]
        colorName           = extracted["colorName"]
        G.SS_lastColorUsed  = colorName
        self.setToRename    = renameSet
        
        cmds.columnLayout(self.renameSetLayout, edit=True, visible=True, w=self.createRenameLayoutW)
        self.turnOffCreateNewSetField()
        cmds.textField(self.renameSetTextField, edit=True, text=selSetName)
        self.sortSelSetButtons(renameSet=renameSet)
        cmds.setFocus(self.renameSetTextField)    
        self.adjustButtonsWidth() 
        self.highlightColorSelection()    
  
  
    def turnOffRenameSetField(self):
        
        if not cmds.columnLayout(self.renameSetLayout, query=True, visible=True): return
        
        self.sortSelSetButtons()

        viewports           = [view for view in cmds.getPanel(type='modelPanel') if view in cmds.getPanel(visiblePanels=True)]            
        self.setToRename    = None   
        
        cmds.columnLayout   (self.renameSetLayout, edit=True, visible=False, w=1) 
        if len(viewports) > 0:  cmds.setFocus(viewports[0])   
        self.adjustButtonsWidth() 


    def createNewSelectSet(self, setName=None, colorName=None):
        
        if colorName: 
            G.SS_lastColorUsed  = colorName
            setName             = cmds.textField(self.createNewSetTextField, query=True, text=True)
            self.highlightColorSelection()
        
        tmpSetName  = setName.replace(" ", "")
        if tmpSetName == "": return
        
        sel        = cmds.ls(selection=True)
        
        if len(sel) == 0: 
            cmds.warning("Please select some objects.")
            return
         
        if not self.testRepeated(sel):              
            newSelSetName  = "%s%s_%s"%(self.defaultSetName, G.SS_lastColorUsed, utilMod.toTitle(setName))
            with G.aToolsBar.createAToolsNode: newSelSet      = cmds.sets(sel, name=newSelSetName, text="gCharacterSet")
            
            self.showColor(G.SS_lastColorUsed)
            self.turnOffCreateNewSetField()
            self.aToolsSets.append(newSelSet)
            self.aToolsSets = sorted(self.aToolsSets)
            self.createSelSetButton(newSelSet)
            self.aToolsSetsDict[newSelSet] = sel
            self.sortSelSetButtons(newSelSet)
            self.blinkButton(newSelSet, 3)            
            self.highlightSelectedButtons(newSelSet)
   
    
    def renameSelectSet(self, setName=None, colorName=None):
        
        if not cmds.objExists(self.setToRename): 
            self.deleteSets([self.setToRename])
            self.turnOffRenameSetField()
            return
                
        if colorName: 
            G.SS_lastColorUsed  = colorName
            if not setName:
                setName             = cmds.textField(self.renameSetTextField, query=True, text=True)
                self.highlightColorSelection()
                
        tmpSetName      = setName.replace(" ", "")
        if tmpSetName == "": self.turnOffRenameSetField(); return
        
        newSelSetName   = "%s%s_%s"%(self.defaultSetName, G.SS_lastColorUsed, setName)
        
        if self.setToRename == newSelSetName: self.turnOffRenameSetField(); return
        
        renamedSet      = cmds.rename(self.setToRename, newSelSetName)        
        b               = 'aToolsSetBtn_%s'%self.setToRename                 
        
        if cmds.iconTextButton(b, query=True, exists=True): 
            function = lambda *args:cmds.deleteUI(b, control=True)
            G.deferredManager.sendToQueue(function, 1, "SS")
        
        
        
        self.showColor(colorName)
        self.aToolsSets.remove(self.setToRename)
        self.aToolsSets.append(renamedSet)
        self.aToolsSets = sorted(self.aToolsSets)
        
        self.aToolsSetsDict.pop(self.setToRename, None)
        self.aToolsSetsDict[renamedSet] = cmds.sets(renamedSet, query=True, nodesOnly=True)
        self.createSelSetButton(renamedSet)
        self.sortSelSetButtons(renamedSet)
        self.blinkButton(renamedSet, 3)            
        self.highlightSelectedButtons(renamedSet) 
        self.turnOffRenameSetField()
        
        
        

    
    
    def highlightColorSelection(self):
        
        fields = ["create", "rename"]
        
        for loopColor in self.colors:
            loopColorName   = loopColor["name"]
            
            if loopColorName == G.SS_lastColorUsed: 
                for loopField in fields: cmds.iconTextButton("colorButton%s%s"%(loopField, loopColorName), edit=True, image=uiMod.getImagePath('specialTools_gray_dot_c'), style='iconOnly')
            else:                                   
                for loopField in fields: cmds.iconTextButton("colorButton%s%s"%(loopField, loopColorName), edit=True, style='textOnly')
                         
    
    def createSelSetButton(self, selSet):    
        extracted   = self.extractInfoFromSelSet(selSet)
        selSetName  = extracted["selSetName"]
        colorName   = extracted["colorName"]
        colorValue  = extracted["colorValue"]
        
        cmds.iconTextButton('aToolsSetBtn_%s'%selSet, 
                            label=' %s '%selSetName, 
                            image=uiMod.getImagePath('specialTools_select_sets_img'), 
                            highlightImage=uiMod.getImagePath('specialTools_select_sets_highlight_img'), 
                            height=self.buttonHeight, 
                            bgc=colorValue, 
                            command=lambda selSet=selSet, *args: self.selectSet(selSet), 
                            dragCallback=lambda *args: self.turnOnRenameSetField(selSet), 
                            ann='%s\n\nLeft click: select\nShift+click: add selection\nCtrl+click: subtract selection\nMiddle click: rename set\nCtrl+Shift+click: delete set\n\nRight click for options'%selSetName, 
                            parent=self.selSetsLayout
                            )
        self.selSetButtonPopUp(selSet)
        
        G.deferredManager.sendToQueue(lambda *args: self.saveButtonWidth(selSet), 1, "SS")
        G.deferredManager.sendToQueue(self.adjustButtonsWidth, 1, "SS")
        
        
        
    def saveButtonWidth(self, selSet):
        self.selSetButtonWidth[selSet] = cmds.iconTextButton('aToolsSetBtn_%s'%selSet, query=True, w=True)
        
        
    def selSetButtonPopUp(self, selSet):       
        menu = cmds.popupMenu()
        cmds.popupMenu(menu, edit=True, postMenuCommand=lambda *args: self.populateSelSetButtonsMenu(menu, selSet), postMenuCommandOnce=True)
       
                
    def populateSelSetButtonsMenu(self, menu, selSet, *args):
        
        extracted   = self.extractInfoFromSelSet(selSet)
        colorName   = extracted["colorName"]

        cmds.radioMenuItemCollection(parent=menu)
        
        for loopColor in self.colors:
            loopColorName  = loopColor["name"]
            radioSelected = (colorName == loopColorName)
            cmds.menuItem(label=utilMod.toTitle(loopColorName),   radioButton=radioSelected,        command=lambda x, selSet=selSet, loopColorName=loopColorName, *args: self.renameSelectSetColor([selSet], loopColorName),  parent=menu)
            
         
        cmds.menuItem(divider=True,  parent=menu)
        cmds.menuItem(label='Add Selection',    command=lambda *args: self.addSelection(selSet),  parent=menu)
        cmds.menuItem(label='Remove Selection', command=lambda *args: self.removeSelection(selSet),  parent=menu)
        cmds.menuItem(label='Update Selection', command=lambda *args: self.updateSelection(selSet),  parent=menu)
        cmds.menuItem(divider=True,  parent=menu)
        cmds.menuItem(label='Rename',           command=lambda *args: self.turnOnRenameSetField(selSet),  parent=menu)
        cmds.menuItem(label='Delete',           command=lambda *args: self.deleteSets([selSet]),  parent=menu)
        cmds.menuItem(label='Delete All %s'%utilMod.toTitle(colorName),    command=lambda *args: self.deleteAllColorSet(colorName),  parent=menu)
        cmds.menuItem(divider=True,  parent=menu)
        
        duplicateToOtherMenu = cmds.menuItem(subMenu=True, label='Duplicate To Other Character', parent=menu, postMenuCommandOnce=True)
        cmds.menuItem(duplicateToOtherMenu, edit=True,  postMenuCommand=lambda *args:self.populateDuplicateToOtherMenu(duplicateToOtherMenu, selSet))
        cmds.setParent( '..', menu=True ) 
               
        
        cmds.menuItem(label='Show Only %s'%utilMod.toTitle(colorName),  command=lambda *args: self.isolateColor(colorName),  parent=menu)
        cmds.menuItem(label='Hide %s'%utilMod.toTitle(colorName),       command=lambda *args: self.hideColor(colorName),  parent=menu)
   
    
    def sortSelSetButtons(self, fromSelSet=None, renameSet=None):
        
        if not fromSelSet:  index = 0 
        else:               index = self.aToolsSets.index(fromSelSet)
    
    
        cmds.columnLayout(self.renameSetLayout, edit=True, parent=self.limboLayout)
    
        for loopSet in self.aToolsSets[index:]:  
            
            extracted   = self.extractInfoFromSelSet(loopSet)
            colorName   = extracted["colorName"]
            if colorName not in G.SS_showColors:                 
                cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, parent=self.limboLayout, visible=False)
                continue
            
            if loopSet == renameSet:
                cmds.columnLayout(self.renameSetLayout, edit=True, parent=self.selSetsLayout)
                cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, visible=False, w=1)
                continue
        
               
            cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, parent=self.limboLayout)
            cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, parent=self.selSetsLayout, visible=True) 
            
            if loopSet in self.selSetButtonWidth: cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, w=self.selSetButtonWidth[loopSet]) 
                
        
    def adjustButtonsWidth(self):    
        buttonSets          = [loopSet for loopSet in self.aToolsSets if not self.isHidden(loopSet)]
        
        self.resetButtonsWidth(buttonSets)
        
        function = lambda *args:self.stretchButtonsWidth(buttonSets)
        G.deferredManager.sendToQueue(function, 1, "SS")
        
    
    def resetButtonsWidth(self, buttonSets):        
        
        for n, loopSet in enumerate(buttonSets):
            if loopSet in self.selSetButtonWidth: cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, w=self.selSetButtonWidth[loopSet])
        
    def stretchButtonsWidth(self, buttonSets):
        
        if not cmds.window(self.mainWin, query=True, exists=True): return
        
        mayaWinSize    = cmds.window(self.mainWin, query=True, width=True)
        buttonsLayoutSize   = cmds.rowLayout(self.mainLayout, query=True, width=True)        
                
        if buttonsLayoutSize < mayaWinSize: return
        
        diference           = buttonsLayoutSize - mayaWinSize
        sizeChart           = [cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, query=True, w=True) for loopSet in buttonSets]
        x                   = 0
                
        while True:
            for n, loopSet in enumerate(buttonSets):
                x += 1
                if x > diference: break
                if max(sizeChart) == 1: 
                    x = diference +1
                    break
                sizeChart[sizeChart.index(max(sizeChart))] = max(sizeChart) -1 
            if x > diference: break
                
        for n, loopSet in enumerate(buttonSets):
            cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, w=sizeChart[n]) 
            
        
    def testRepeated(self, sel, warn=True):

        for loopSet in self.aToolsSets:
            if not cmds.objExists(loopSet): continue
            if cmds.sets(sel, isMember=loopSet) and len(sel) == cmds.sets(loopSet, query=True, size=True): 
                color = self.extractInfoFromSelSet(loopSet)["colorName"]
                if warn: cmds.warning("The selection is already a set: (%s) %s"%(color, loopSet[len(self.defaultSetName)+len(color)+1:]))
                return True
    
    
    def extractInfoFromSelSet(self, selSet):
        selSetSplit     = selSet[len(self.defaultSetName):].split("_")
        selSetName      = "_".join(selSetSplit[1:])
        colorName       = selSetSplit[0]
        colorValue      = None
        
        for loopColor in self.colors:
            loopColorName  = loopColor["name"]
            if colorName == loopColorName:
                colorValue = loopColor["value"]
                break
        
        if not colorValue: return

        return {"selSetName":selSetName, "colorName":colorName, "colorValue":colorValue, "selSet":selSet}  
        
     
    def getaToolsSets(self):
        
        allSelSets = [loopSet for loopSet in cmds.ls(sets=True, exactType="objectSet") if cmds.sets(loopSet, query=True, text=True) == "gCharacterSet"]
        aToolsSets = []
        
        for loopSet in allSelSets:
            if self.defaultSetName in loopSet:
                if cmds.objExists(loopSet):
                     
                    extracted   = self.extractInfoFromSelSet(loopSet)
                    
                    if not extracted: continue
                    
                    selSetName  = extracted["selSetName"]
                    colorName   = extracted["colorName"]
                    colorValue  = extracted["colorValue"]
                    selSet      = extracted["selSet"]
                    
                    for loopColor in self.colors:
                        loopColorName  = loopColor["name"]
                        
                        if self.defaultSetName in loopSet and colorName == loopColorName and cmds.sets(loopSet, query=True, text=True) == "gCharacterSet":
                            aToolsSets.append(loopSet)
                            continue
          
        return aToolsSets


    def delWindows(self):
        
        if cmds.iconTextButton("selectSetsBtn", query=True, exists=True):
            cmds.iconTextButton("selectSetsBtn", edit=True, image=uiMod.getImagePath("specialTools_select_sets"), highlightImage= uiMod.getImagePath("specialTools_select_sets copy"))

        for loopWin in self.allWin:
            if cmds.rowLayout(loopWin, query=True, exists=True): cmds.deleteUI(loopWin)
            if cmds.window(loopWin, query=True, exists=True):  cmds.deleteUI(loopWin)
            if cmds.toolBar(loopWin, query=True, exists=True): cmds.deleteUI(loopWin)
    
        self.clearScriptJobs()    
    
    def selectSet(self, selSet):  
         
        mod = uiMod.getModKeyPressed()
        
        if not cmds.objExists(selSet): 
            self.rebuildAllSelectSets([selSet])
            if mod == "ctrlShift": self.deleteSets([selSet])
            return
        
        if mod == "shift":
            cmds.select(selSet, add=True) 
        elif mod == "ctrl":
            cmds.select(selSet, deselect=True) 
        elif mod == "ctrlShift":
            self.deleteSets([selSet])
        else:
            cmds.select(selSet, replace=True)
        

        function = lambda *args: self.checkIfElementsDeleted(selSet)
        G.deferredManager.sendToQueue(function, 1, "SS")
       
    
    def deleteSets(self, selSets):  
        toRemove = []
        for loopSet in selSets:
            if cmds.objExists(loopSet):
                cmds.delete(loopSet)
                toRemove.append(loopSet)
            
            b = 'aToolsSetBtn_%s'%loopSet                
            if cmds.iconTextButton(b, query=True, exists=True): 
                function = lambda b=b, *args:cmds.deleteUI(b, control=True)
                G.deferredManager.sendToQueue(function, 1, "SS")

            self.aToolsSetsDict.pop(loopSet, None)
    
        for loopSet in toRemove: self.aToolsSets.remove(loopSet)
        self.adjustButtonsWidth()
        
   
    def deleteAllSets(self, *args):
        message         = "Delete all aTools select sets?"
        confirm         = cmds.confirmDialog( title='Confirm', message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

        if confirm != 'Yes': return
        
        self.deleteSets(self.aToolsSets)
        self.toggleToolbar(forceOff=True)
    
   
    def deleteAllColorSet(self, colorName):  
        message         = "Delete all aTool %s sets?"%colorName
        confirm         = cmds.confirmDialog( title='Confirm', message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

        if confirm != 'Yes': return
        
        delSets         = []
        
        for loopSet in self.aToolsSets:
            
            extracted       = self.extractInfoFromSelSet(loopSet)
            loopColorName   = extracted["colorName"]
            if loopColorName == colorName:
                delSets.append(loopSet)
        
        self.deleteSets(delSets)
    
    def isHidden(self, selSet):        
        
        if not cmds.iconTextButton('aToolsSetBtn_%s'%selSet, query=True, exists=True): return True 
        if not cmds.iconTextButton('aToolsSetBtn_%s'%selSet, query=True, visible=True): return True
        
    
    def getSelectedSets(self):        
        return [loopSet for loopSet in self.aToolsSets if cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, query=True, exists=True) and cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, query=True, style=True) != 'textOnly']
    
    def highlightSelectedButtons(self, onlySelSet=None):        
        
        
        aToolsSets  = [onlySelSet] if onlySelSet else self.aToolsSets 
        CurrSel     = sorted(cmds.ls(selection=True))          
        
        if len(CurrSel) > 0:
                
            smallDot    = uiMod.getImagePath("specialTools_gray_dot_a")
            bigDot      = uiMod.getImagePath("specialTools_gray_dot_c")            
            
            for loopSet in aToolsSets:
                if self.isHidden(loopSet):      continue 
                if not cmds.objExists(loopSet): continue               
                
                nodes = sorted(cmds.sets(loopSet, query=True, nodesOnly=True))
                 
                if nodes == CurrSel: 
                    cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, style='iconAndTextVertical', image=bigDot, highlightImage=bigDot)
                elif set(CurrSel).issuperset(set(nodes)):                                             
                    cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, style='iconAndTextVertical', image=smallDot, highlightImage=smallDot)
                else:          
                    cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, style='textOnly')
                   
                
        else:
            for loopSet in self.aToolsSets:
                if self.isHidden(loopSet): continue
                cmds.iconTextButton('aToolsSetBtn_%s'%loopSet, edit=True, style='textOnly')
                
    def togleBlinkButton(self, button, color):
        
        white = cmds.iconTextButton(button, query=True, bgc=True) == [1,1,1]
        
        if white:   self.setButtonColor(button, color) 
        else:       self.setButtonColor(button, (1,1,1))
        
    def blinkButton(self, selSet, xTimes):
        
        extracted   = self.extractInfoFromSelSet(selSet)
        colorValue  = extracted["colorValue"]
                
        G.aToolsBar.timeoutInterval.setTimeout((lambda *args: self.togleBlinkButton('aToolsSetBtn_%s'%selSet, colorValue)), sec=.05, xTimes=(xTimes*2))

    
    def setButtonColor(self, button, color, *args):
        if cmds.iconTextButton(button, query=True, exists=True): cmds.iconTextButton(button, edit=True, bgc=color)
    
    def clearScriptJobs(self):

        utilMod.killScriptJobs("G.selectSetsScriptJobs")
    
    
    def showAllColors(self, *args):        
        
        pass
        G.SS_showColors = self.getaToolsColors()[0]
        self.updateshowColors(refresh=True)
    
    def importSets(self, *args):
        cmds.waitCursor(state=True)   
    
        setsData = aToolsMod.loadInfoWithUser("selectSets", "setsData")    
        self.createSetsFromData(setsData)
        
        cmds.waitCursor(state=False)    
    
    
    def createSetsFromData(self, setsData):
        if not setsData: return
        
        newSets  = setsData[0]
        selArray = setsData[1]
        
        for n, loopSet in enumerate(newSets):
 
            sel = [loopSel for loopSel in selArray[n] if cmds.objExists(loopSel)]
            
            if len(sel) > 0:
                if not self.testRepeated(sel):     
                    newSelSet = cmds.sets(sel, name=loopSet, text="gCharacterSet")
                    self.aToolsSetsDict[newSelSet] = sel

        self.rebuildAllSelectSets()
        self.refreshToolBar()
        
       
    def exportSets(self, *args):
        cmds.waitCursor(state=True)
        
        #currSel         = cmds.ls(selection=True) 
        self.aToolsSets = self.getaToolsSets()
        
        setsData = self.getSetsData(self.aToolsSets)
        aToolsMod.saveInfoWithUser("selectSets", "setsData", setsData)  
        
        #if len(currSel) > 0: cmds.select(currSel)
        
        cmds.waitCursor(state=False)
        cmds.warning("Select sets export done. Hit 'Import Select Sets' to import them to another scene.")
        
        
    def getSetsData(self, sets):
        
        setData     = []
        setContents = []
        
        for loopSet in sets:
            setContents.append(cmds.sets(loopSet, query=True, nodesOnly=True))
            #cmds.select(loopSet)
            #setContents.append(cmds.ls(selection=True))
        
        setData.append(sets)
        setData.append(setContents)
        
        return setData    
    

    def populateDuplicateToOtherMenu(self, menu, selSet, *args):
        
        extracted   = self.extractInfoFromSelSet(selSet)
        selSetName  = extracted["selSetName"]
        colorName   = extracted["colorName"]
        colorValue  = extracted["colorValue"]
        selSet      = extracted["selSet"]
        
        
        allColorSets    = []
        
        for loopSet in self.aToolsSets:
            loopExtracted   = self.extractInfoFromSelSet(loopSet)    
            loopColorName   = loopExtracted["colorName"]
            
            if colorName == loopColorName: allColorSets.append(loopSet)
        
        
        newMenu             = cmds.menuItem(subMenu=True, label=selSetName,  parent=menu)
        newMenuAllColors    = cmds.menuItem(subMenu=True, label="All %s"%colorName,  parent=menu)
        
        cmds.menuItem(newMenu, edit=True,              postMenuCommand=lambda *args: self.populateDuplicateButtonMenu(newMenu, [selSet], colorName))
        cmds.menuItem(newMenuAllColors, edit=True,     postMenuCommand=lambda *args: self.populateDuplicateButtonMenu(newMenuAllColors, allColorSets, colorName))
        
        
    def populateDuplicateButtonMenu(self, menu, selSet, colorName):
        
        outputNameSpaces    = utilMod.listAllNamespaces()
                
        uiMod.clearMenuItems(menu)
        if not outputNameSpaces: return
                
        for loopNameSpace in outputNameSpaces:
            newMenu = cmds.menuItem(subMenu=True, label=loopNameSpace, parent=menu)
            for loopColor in self.colors:                
                loopColorName  = loopColor["name"]
                
                if colorName != loopColorName:
                    cmds.menuItem(label=utilMod.toTitle(loopColorName), parent=newMenu, command=lambda x, loopNameSpace=loopNameSpace, loopColorName=loopColorName, *args:self.duplicateSet(selSet,loopNameSpace,loopColorName))
    
           
    
    def duplicateSet(self, selSets, outputNameSpace, newColor):  
                      
        cmds.waitCursor(state=True)   
    
        selSetsData            = self.getSetsData(selSets) 
        selSets                = selSetsData[0]
        contents            = selSetsData[1]
        inputNameSpaces     = []
        newSelSets             = []
        
        separator = ":"
                
        for loopContents in contents:
            nameSpaces = utilMod.getNameSpace(loopContents)[0]
            for loopNameSpace in nameSpaces:
                if loopNameSpace[:-1] not in inputNameSpaces:
                    inputNameSpaces.append(loopNameSpace[:-1])        
        
        for inputNameSpace in inputNameSpaces:
                                                                                        
            selSetsStr     = str(selSetsData)
            selSetsData    = eval(selSetsStr.replace("%s%s"%(inputNameSpace, separator), "%s%s"%(outputNameSpace, separator)))            
        
        for loopSet in selSets: 
            newSelSets.append(self.getRenamedColor(loopSet, newColor))
            
        selSetsData[0] = newSelSets        
        
        self.createSetsFromData(selSetsData)        
        cmds.waitCursor(state=False)    
        
           
    def addSelection(self, selSet):    
        sel         = cmds.ls(selection=True)
        
        if len(sel) == 0: return 
        selSet = self.createSelSetIfInexistent(selSet, sel)
        cmds.sets(sel, edit=True, addElement=selSet)
        if selSet not in self.aToolsSetsDict: self.aToolsSetsDict[selSet] = []
        for loopSel in sel: 
            if loopSel not in self.aToolsSetsDict[selSet]: self.aToolsSetsDict[selSet].append(loopSel) 
        self.blinkButton(selSet, 1)
        self.highlightSelectedButtons(selSet)
        
        
    def removeSelection(self, selSet):    
        sel         = cmds.ls(selection=True)
                
        if len(sel) == 0: return 
        selSet = self.createSelSetIfInexistent(selSet, sel)
        cmds.sets(sel, edit=True, remove=selSet)   
        if selSet not in self.aToolsSetsDict: self.aToolsSetsDict[selSet] = [] 
        for loopSel in sel:
            if loopSel in self.aToolsSetsDict[selSet]: self.aToolsSetsDict[selSet].remove(loopSel)
        self.blinkButton(selSet, 1)
        self.highlightSelectedButtons(selSet)
        
    def updateSelection(self, selSet):    
        sel         = cmds.ls(selection=True)
        
        if len(sel) == 0: return       
        selSet = self.createSelSetIfInexistent(selSet, sel)  
        cmds.sets(edit=True, clear=selSet)
        cmds.sets(sel, edit=True, addElement=selSet)
        self.aToolsSetsDict[selSet] = sel
        self.blinkButton(selSet, 1)        
        self.highlightSelectedButtons(selSet)
    
    def updateshowColorsMenu(self, *args):
        
        for loopColor in self.colors:
            loopColorName  = loopColor["name"]
            checkBox = (loopColorName in G.SS_showColors)
            cmds.menuItem('colorMenu_%s'%loopColorName, edit=True, checkBox=checkBox)
        
    
    def toggleSelSetsButtonColor(self):
        
        visible = (len(G.SS_showColors) < len(self.colors)) 
        w       = 25 if visible else 1
        
        cmds.iconTextButton(self.showAllColorsButton, edit=True, visible=visible, w=w)        
        self.sortSelSetButtons()
        self.adjustButtonsWidth()


    def showAllColors(self, *args):
        
        G.SS_showColors     = [loopColor["name"] for loopColor in self.colors]
        self.toggleSelSetsButtonColor()

    
    def isolateColor(self, color):
        
        G.SS_showColors     = [color]        
        G.SS_lastColorUsed  = color
        self.toggleSelSetsButtonColor()
    
    def switchColor(self, color):        
        
        if color in G.SS_showColors: self.hideColor(color)
        else: self.showColor(color)
        self.toggleSelSetsButtonColor()
             
    
    def hideColor(self, color):                
            
        if color in G.SS_showColors: 
            G.SS_showColors.remove(color)       
            self.toggleSelSetsButtonColor()
    
    def showColor(self, color):                  
        
        if color not in G.SS_showColors: 
            G.SS_showColors.append(color)       
            self.toggleSelSetsButtonColor() 
    
    def getRenamedColor(self, selSet, newColor):         
        
        extracted       = self.extractInfoFromSelSet(selSet)
        selSetName      = extracted["selSetName"]        
        newSelSetName   = "%s%s_%s"%(self.defaultSetName, newColor, selSetName)
        
        return newSelSetName
        
    def renameSelectSetColor(self, selSets, newColor):
        
        for loopSet in selSets:
            self.setToRename    = loopSet
            extracted           = self.extractInfoFromSelSet(loopSet)
            selSetName          = extracted["selSetName"]        
            
            self.renameSelectSet(selSetName, newColor)
        
  