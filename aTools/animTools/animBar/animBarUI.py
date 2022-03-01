'''
========================================================================================================================
Author: Alan Camilo
www.alancamilo.com
Modified: Michael Klimenko

Requirements: aTools Package

------------------------------------------------------------------------------------------------------------------------
To install aTools, please follow the instructions in the file how_to_install.txt, located in the folder aTools

------------------------------------------------------------------------------------------------------------------------
To unistall aTools, go to menu (the last button on the right), Uninstall

========================================================================================================================
''' 

# maya modulesspecialTools
import importlib
from maya import cmds
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.generalTools        import aToolsClasses;               importlib.reload(aToolsClasses)
from aTools.commonMods          import animMod;                     importlib.reload(animMod)
from aTools.generalTools        import generalToolsUI;              importlib.reload(generalToolsUI)
from aTools.commonMods          import utilMod;                     importlib.reload(utilMod)
from aTools.commonMods          import commandsMod;                 importlib.reload(commandsMod)
from aTools.commonMods          import aToolsMod;                   importlib.reload(aToolsMod)
from aTools                     import setup;                       importlib.reload(setup)        

# constants
SUB_UI_MODS   = ["tweenMachine", "keyTransform", "tangents", "specialTools", "tUtilities"]

# import subUI modules
for loopMod in SUB_UI_MODS:
    exec("import aTools.animTools.animBar.subUIs.%s as %s; importlib.reload(%s)"%(loopMod, loopMod, loopMod))


def show(mode="show"):
    
    G.aToolsBar     = G.aToolsBar or AnimationBar_Gui()  
    
    if mode == False: mode = "show"
    if mode == True:  mode = "toggle"
    
    if mode == "launch":        
        lastState = aToolsMod.loadInfoWithUser("userPrefs", "animationBarLastState")
        if lastState: show()
        return
    
    
    if mode == "show" or mode == "hide":
        if cmds.toolBar("aTools_Animation_Bar", query=True, exists=True): 
            visible = (mode == "show")
            cmds.toolBar("aTools_Animation_Bar", edit=True, visible=visible)
            G.aToolsBar.saveLastState(visible)          
            return
        elif mode == "show":    
            G.aToolsBar.start()
            G.aToolsBar.saveLastState()
            return
    
        
    if mode == "toggle":
        if cmds.toolBar("aTools_Animation_Bar", query=True, exists=True): 
            state   = cmds.toolBar("aTools_Animation_Bar", query=True, visible=True)
            visible = (not state)
            G.aToolsBar.toggleToolbars(visible)
            cmds.toolBar("aTools_Animation_Bar", edit=True, visible=visible)
            G.aToolsBar.saveLastState(visible)
            return
        else:
            show()
            return
            
    if mode == "refresh":
        G.aToolsBar = AnimationBar_Gui() 
        G.aToolsBar.start()
        G.aToolsBar.saveLastState()
           

  
class AnimationBar_Gui(object):
    
    def __init__(self):
        self.winName        = "aAnimationBarWin"
        self.toolbarName    = "aTools_Animation_Bar"
        self.allWin         = [self.winName, self.toolbarName]
        self.buttonSize     = {"small":[15, 20], "big":[25, 25]}
        self.barOffset      = 0        
        self.barHotkeys     = {}
        G.aToolsUIs         = {"toolbars":[
                               
                               ],
                               "windows":[
                                          
                              ]}
        
        # [ SUBUIs ]
        self.uiList         = None
        self.subUIs         = None
    
    def __getattr__(self, attr):
        return None     
       
    def start(self):
        
        from aTools.generalTools import aToolsClasses;  importlib.reload(aToolsClasses)
        self.startUpFunctions()
        self.delWindows()
        self.createWin()
        
    def startUpFunctions(self):
        #wait cursor state
        n = 0    
        while True:
            if not cmds.waitCursor(query=True, state=True) or n > 100: break
            cmds.waitCursor(state=False)
            n += 1
            
        #refresh state    
        cmds.refresh(suspend=False)
        #undo state
        if not cmds.undoInfo(query=True, stateWithoutFlush=True): cmds.undoInfo(stateWithoutFlush=True)
        #progress bar state        
        utilMod.setProgressBar(status=None, progress=None, endProgress=True)
        
    
    def saveLastState(self, state=True):    
        aToolsMod.saveInfoWithUser("userPrefs", "animationBarLastState", state) 

    def createWin(self):

        # Creates window
        self.mainWin = cmds.window(self.winName, sizeable=True)

        # Main frame
        cmds.frameLayout("mainFrameLayout", labelVisible=False, borderVisible=False, w=10, marginHeight=0, marginWidth=0, labelIndent=0, collapsable=False)
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach=([2, 'right', self.barOffset]),  h=37)
        cmds.text(label="")
        self.subUIsLayout = cmds.rowLayout("mainLayout", numberOfColumns=len(SUB_UI_MODS)+2)
        
        # subUIs
        self.uiList   = [eval("%s.%s%s_Gui"%(loopUi, loopUi[0].upper(), loopUi[1:])) for loopUi in SUB_UI_MODS]
        # append general tools ui
        self.uiList.append(generalToolsUI.GeneralTools_Gui)
        # define subUis
        self.subUIs   = [loopUi(self.subUIsLayout, self.buttonSize) for loopUi in self.uiList]

        self.addSubUIs()
        
        # shows toolbar
        cmds.toolBar(self.toolbarName, area='bottom', content=self.mainWin, allowedArea=['bottom'])
        
    # end method createWin
    #---------------------------------------------------------------------
    def addSubUIs(self):
        # parent subUis to the main layout
        for loopIndex, loopSubUI in enumerate(self.subUIs):
            loopSubUI.createLayout()
            # space
            if loopIndex < len(self.subUIs) -1: 
                cmds.rowLayout(numberOfColumns=2)
                cmds.text( label='   ', h=1 )

        # end for
        
    def toggleToolbars(self, visible):
        pass
    
    def delWindows(self, onOff=True, forceOff=False):        
        for loopWin in self.allWin:
            if cmds.window(loopWin, query=True, exists=True): cmds.deleteUI(loopWin)
            if cmds.toolBar(loopWin, query=True, exists=True): 
                cmds.deleteUI(loopWin)



