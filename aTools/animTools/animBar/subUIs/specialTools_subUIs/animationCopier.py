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
from aTools.commonMods import aToolsMod


   
class AnimationCopier(object):    
    
    def popupMenu(self):
        cmds.popupMenu()
        cmds.menuItem(                          label="Copy All Animation",   command=lambda *args: self.copyAnimation(range="all"))
        cmds.menuItem( divider=True )
        cmds.menuItem("onlySelectedNodesMenu",  label="Paste To Selected", checkBox=False)
        cmds.menuItem(                          label="Paste Animation in Place",   command=lambda *args: self.pasteAnimation(pasteInPlace=True))
        cmds.menuItem(                          label="Paste Original Animation",   command=lambda *args: self.pasteAnimation(pasteInPlace=False))
        cmds.menuItem( divider=True )
        cmds.menuItem(  label="Paste To Another Character",           command=self.remapNamespaces)
    
        
    def copyAnimation(self, range="selected", *args):    
        cmds.waitCursor(state=True)
        
        if range == "all":
                        
            getCurves    = animMod.getAnimCurves()
            animCurves   = getCurves[0]
            animData = animMod.getAnimData(animCurves, showProgress=True)
        else:
            animData = animMod.getAnimData(showProgress=True)
            
        aToolsMod.saveInfoWithUser("copyPasteAnim", "animData", animData)  

        if cmds.window("remapNamespacesWindow", query=True, exists=True): self.remapNamespaces()
        
        cmds.waitCursor(state=False)  
    
    def pasteAnimation(self, animData=None, pasteInPlace=True, onlySelectedNodes=None, *args):  
        cmds.waitCursor(state=True)   
        
        if not onlySelectedNodes:   onlySelectedNodes = cmds.menuItem("onlySelectedNodesMenu", query=True, checkBox=True)
        if not animData:            animData = aToolsMod.loadInfoWithUser("copyPasteAnim", "animData")    
        animMod.applyAnimData(animData, pasteInPlace, onlySelectedNodes, showProgress=True)
        
        cmds.waitCursor(state=False)
    
    def remapNamespaces(self, *args):
        winName = "remapNamespacesWindow"
        if cmds.window(winName, query=True, exists=True): cmds.deleteUI(winName)
        window = cmds.window( winName, title = "Remap Namespaces")
    
        cmds.columnLayout(adjustableColumn=True)
        cmds.rowColumnLayout( numberOfColumns=3)
        
        animData            = aToolsMod.loadInfoWithUser("copyPasteAnim", "animData")
        inputNameSpaces     = list(set(utilMod.getNameSpace(animData["objects"])[0]))
        outputNameSpaces    = utilMod.listAllNamespaces()
        
        for loopNameSpace in inputNameSpaces:  
            
            nameSpace = loopNameSpace[:-1]
            
            eval("cmds.text('input%s', align='right', w=150, h=26, label='%s:   ')"%(nameSpace, nameSpace))
            eval("cmds.textField('output%s', w=150, h=26, text='%s')"%(nameSpace, nameSpace))
            eval("cmds.button('output%s', w=26, h=26, label='...')"%(nameSpace))
            if outputNameSpaces:
                cmds.popupMenu(button=1)
                for loopOutput in outputNameSpaces:
                    cmds.menuItem       ("menu%s"%loopOutput, label=str(loopOutput), command=lambda x, loopOutput=loopOutput, nameSpace=nameSpace, *args: self.setOutputValue(loopOutput, nameSpace))    
        
        cmds.setParent( '..' )
        
        
        cmds.button(label="Paste Animation in Place",     command=lambda *args: self.remapAndPasteAnimation(animData, inputNameSpaces, pasteInPlace=True))
        cmds.button(label="Paste Original Animation",     command=lambda *args: self.remapAndPasteAnimation(animData, inputNameSpaces, pasteInPlace=False))
        
        cmds.showWindow( window )
    
    def setOutputValue(self, output, nameSpace):
        cmds.textField('output%s'%nameSpace, edit=True, text=str(output))
    
    def remapAndPasteAnimation(self, animData, nameSpaces, pasteInPlace):
        
        
        separator = ":"
        
        for loopNameSpace in nameSpaces:  
            
            nameSpace   = loopNameSpace[:-1]
            
            input       = nameSpace
            output      = cmds.textField('output%s'%nameSpace, query=True, text=True)
            
            animStr     = str(animData)
            animData    = eval(animStr.replace("%s%s"%(input, separator), "%s%s"%(output, separator)))
        
        self.pasteAnimation(animData, pasteInPlace)
    



