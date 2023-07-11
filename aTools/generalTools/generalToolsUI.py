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
import sys
import urllib.request, urllib.error, urllib.parse
import shutil
import zipfile
import os
import webbrowser

from maya import cmds
from maya import mel
from maya import OpenMaya
from maya import OpenMayaAnim
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from aTools.commonMods      import uiMod
from aTools.commonMods      import utilMod
from aTools.commonMods      import animMod
from aTools.commonMods      import commandsMod
from aTools.commonMods      import aToolsMod
from aTools                 import setup
from aTools.generalTools    import hotkeys;                     importlib.reload(hotkeys)
from aTools.generalTools    import tumbleOnObjects;             importlib.reload(tumbleOnObjects)
from aTools.animTools       import animationCrashRecovery;      importlib.reload(animationCrashRecovery)
from aTools.animTools       import framePlaybackRange;          importlib.reload(framePlaybackRange)
from aTools.animTools       import jumpToSelectedKey;           importlib.reload(jumpToSelectedKey)
    


animationCrashRecovery  = animationCrashRecovery.AnimationCrashRecovery()
tumbleOnObjects         = tumbleOnObjects.TumbleOnObjects()

versionInfoPath     = "%sversion_info.txt"%aToolsMod.getaToolsPath(inScriptsFolder=False)
versionInfoContents = utilMod.readFile(versionInfoPath)
VERSION             = versionInfoContents[0].split(" ")[-1].replace("\n", "")
WHATISNEW           = "".join(versionInfoContents[1:])
KEYSLIST            = ["Up", "Down", "Left", "Right", "", "Page_Up", "Page_Down", "Home", "End", "Insert", "", "Return", "Space", "", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
SITE_URL            = "http://camiloalan.wix.com/atoolswebsite"
ATOOLS_FOLDER       = "http://www.trickorscript.com/aTools/"
UPDATE_URL          = "%slatest_version.txt"%ATOOLS_FOLDER
DOWNLOAD_URL        = "%saTools.zip"%ATOOLS_FOLDER
lastUsedVersion     = aToolsMod.loadInfoWithUser("userPrefs", "lastUsedVersion")
HELP_URL            = "http://camiloalan.wix.com/atoolswebsite#!help/cjg9"
DONATE_URL          = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=5RQLT89A239K6"




PREFS = [{  "name":"tumbleOnObjects",
            "command":"tumbleOnObjects.switch(onOff)",
            "default":True
        },{ "name":"autoFramePlaybackRange",
            "command":"framePlaybackRange.toggleframePlaybackRange(onOff)",
            "default":False
        },{ "name":"autoJumpToSelectedKey",
            "command":"jumpToSelectedKey.togglejumpToSelectedKey(onOff)",
            "default":False
        },{ "name":"autoSmartSnapKeys",
            "command":"self.autoSmartSnapKeys.switch(onOff)",
            "default":False
        },{ "name":"animationCrashRecovery",
            "command":"animationCrashRecovery.switch(onOff)",
            "default":True
        },{ "name":"selectionCounter",
            "command":"self.selectionCounter.switch(onOff)",
            "default":True
        },{ "name":"autoSave",
            "command":"cmds.autoSave(enable=onOff)",
            "default":cmds.autoSave(query=True, enable=True)
        },{ "name":"topWaveform",
            "command":"commandsMod.topWaveform(onOff)",
            "default":True
        },{ "name":"playbackAllViews",
            "command":"onOff = 'all' if onOff else 'active'; cmds.playbackOptions(view=onOff)",
            "default":True
        },{ "name":"displayAffected",
            "command":"cmds.displayAffected(onOff)",
            "default":False
        },{ "name":"undoQueue",
            "command":"if onOff: cmds.undoInfo( state=True, infinity=False, length=300)",
            "default":True
        },{ "name":"scrubbingUndo",
            "command":"commandsMod.scrubbingUndo(onOff)",
            "default":True
        },{ "name":"zoomTowardsCenter",
            "command":"cmds.dollyCtx('dollyContext', edit=True, dollyTowardsCenter=onOff)",
            "default":cmds.dollyCtx('dollyContext', query=True, dollyTowardsCenter=True)
        },{ "name":"cycleCheck",
            "command":"cmds.cycleCheck(evaluation=onOff)",
            "default":cmds.cycleCheck(query=True, evaluation=True)
        }]    





class GeneralTools_Gui(uiMod.BaseSubUI):
        
    def createLayout(self):     
       
        mainLayout = cmds.rowLayout(numberOfColumns=6, parent=self.parentLayout)
        
        #manipulator orientation
        #cmds.iconTextButton("manipOrientButton", style='textOnly',  label='-', h=self.hb, annotation="Selected objects", command=updateManipOrient)  
        #launchManipOrient()
        
        self.autoSmartSnapKeys       = AutoSmartSnapKeys()
        self.selectionCounter        = SelectionCounter()
          
        #selection        
        cmds.iconTextButton("selectionCounterButton", style='textOnly', font="smallPlainLabelFont", label='0', h=self.hb, annotation="Selected objects")  
        cmds.popupMenu("selectionCounterButtonMenu", button=1, postMenuCommand=self.selectionCounter.populateMenu)      
        
        #animation crash recovery
        cmds.image("animationCrashRecoveryLed", w=14, h=14, annotation="Test")  
                
        #menu
        cmds.iconTextButton(style='iconOnly',   w=self.wb, h=self.hb, image= uiMod.getImagePath("aTools"), highlightImage= uiMod.getImagePath("aTools copy"), annotation="aTools Menu")
        self.popUpaToolsMenu()
         
        self.update = Update()
        self.update.about = self.about
        self.update.checkUpdates(self, mainLayout)
     
        # set default config and startup scripts
        self.setDefaultConfig() 
        
    # end createLayout
    
    def popUpaToolsMenu(self):
        cmds.popupMenu(postMenuCommand=lambda *args:self.populateaToolsMenu(args[0], 1), button=1)
        cmds.popupMenu(postMenuCommand=lambda *args:self.populateaToolsMenu(args[0], 3), button=3)
                    
    def populateaToolsMenu(self, menu, button, *args):
        
        #print menu
        #print button
        #menu = menu[0]
        
        uiMod.clearMenuItems(menu)

        subMenu = cmds.menuItem("animBotMenu", subMenu=True, label='animBot - the new aTools' , tearOff=True, parent=menu)
        cmds.menuItem("shelfButtonMenu",          label="Install animBot",    command=installAnimBot,    parent=subMenu)
        cmds.menuItem(                            label="Watch Launch Video", command=watchLaunchVideo,  parent=subMenu)
        cmds.menuItem(                            label="Join the Community", command=joinTheCommunity,  parent=subMenu)

        cmds.menuItem(divider=True, parent=menu)

        shortPrefs =    PREFS[:4]
        for loopPref in shortPrefs:
            name    = loopPref["name"]
            cmds.menuItem('%sMenu'%name, label=utilMod.toTitle(name), command=lambda x, name=name, *args: self.setPref(name), checkBox=self.getPref(name), parent=menu)
        
        #ANIMATION CRASH RECOVERY      
        animationCrashRecoveryPref =    PREFS[4]
        cmds.menuItem("animationCrashRecoveryMenu", label='Animation Crash Recovery' , command=lambda *args: self.setPref(animationCrashRecoveryPref["name"]), checkBox=self.getPref(animationCrashRecoveryPref["name"]), parent=menu)
        cmds.menuItem(optionBox=True, command=animationCrashRecovery.optionBoxWindow, parent=menu)
        
        cmds.menuItem(divider=True, parent=menu)
        
        subMenu = cmds.menuItem("prefsMenu", subMenu=True, label='Preferences' , tearOff=True, parent=menu)
        
        self.commandsAndHotkeys      = CommandsAndHotkeys()
        cmds.menuItem(label="Commands and Hotkeys",         command=self.commandsAndHotkeys.openGui, parent=subMenu)
        cmds.menuItem(divider=True, parent=subMenu)
        shortPrefs =    PREFS[5:]
        for loopPref in shortPrefs:
            name    = loopPref["name"]
            cmds.menuItem('%sMenu'%name,            label=utilMod.toTitle(name),        command=lambda x, name=name, *args: self.setPref(name), checkBox=self.getPref(name), parent=subMenu)
        
        cmds.menuItem(divider=True, parent=subMenu)
        cmds.menuItem("loadDefaultsMenu",          label="Load Defaults",     command=self.loadDefaultPrefs, parent=subMenu)
        
        cmds.menuItem("shelfButtonMenu",          label="Create Toggle on Shelf",           command=shelfButton, parent=menu)
        cmds.menuItem(                            label="Refresh", command=refreshATools, parent=menu)
        cmds.menuItem(                            label="Uninstall", command=self.uninstall, parent=menu)
        cmds.menuItem( divider=True )
        cmds.menuItem(                            label="Help", command=self.help, parent=menu)
        cmds.menuItem(                            label="About", command=self.about, parent=menu)
        

    def setPref(self, pref, init=False, default=False):
        
        for loopPref in PREFS:
            name    = loopPref["name"]
            if pref == name:
                command = loopPref["command"]
                if init: 
                    onOff   = self.getPref(pref)
                elif default:
                    onOff   = self.getDefPref(pref)
                    cmds.menuItem("%sMenu"%name, edit=True, checkBox=onOff)
                    aToolsMod.saveInfoWithUser("userPrefs", name, "", True) 
                else:
                    onOff   = cmds.menuItem("%sMenu"%name, query=True, checkBox=True)
                    aToolsMod.saveInfoWithUser("userPrefs", pref, onOff)
                    
                exec(command)
            
                
    
       
    
    def getPref(self, pref):
        r = aToolsMod.loadInfoWithUser("userPrefs", pref)
        if r == None: 
            default = self.getDefPref(pref)
            r = default 
            
        return r
    
    
    def getDefPref(self, pref):
        for loopPref in PREFS:
            name    = loopPref["name"]
            if pref == name:
                default = loopPref["default"]
                return default
    
    def loadDefaultPrefs(self, *args):
        for loopPref in PREFS:
            name    = loopPref["name"]
            self.setPref(name, False, True)     
        
    def setDefaultConfig(self):
        
        #STATIC PREFS
        # tumble config
        #cmds.tumbleCtx( 'tumbleContext', edit=True, alternateContext=True, tumbleScale=1.0, localTumble=0, autoOrthoConstrain=False, orthoLock=False)
        cmds.tumbleCtx( 'tumbleContext', edit=True, alternateContext=True, tumbleScale=1.0, localTumble=0)
        cmds.dollyCtx( 'dollyContext', edit=True, alternateContext=True, scale=1.0, localDolly=True, centerOfInterestDolly=False)
        #timeline ticks display
        G.playBackSliderPython  = G.playBackSliderPython or mel.eval('$aTools_playBackSliderPython=$gPlayBackSlider')
        cmds.timeControl(G.playBackSliderPython, edit=True, showKeys="mainChannelBox", showKeysCombined=True, animLayerFilterOptions="active") 
        #tickDrawSpecial Color
        # seems to fail on maya 2024
        # cmds.displayRGBColor('timeSliderTickDrawSpecial',1,1,.4)
        
        
        
        #CUSTOMIZABLE PREFS
        for loopPref in PREFS:
            name    = loopPref["name"]
            self.setPref(name, True)
    
    def uninstall(self, *args):
        message = "Are you sure you want to uninstall aTools?"
        confirm = cmds.confirmDialog( title='Confirm', message=message, button=['Yes','No'], defaultButton='No', cancelButton='No', dismissString='No' )
    
        if confirm == 'Yes':      
        
            from aTools.animTools.animBar import animBarUI; importlib.reload(animBarUI)
            #aToolsPath          = aToolsMod.getaToolsPath(2) 
            aToolsFolder        = aToolsMod.getaToolsPath() 
             
            #if aToolsPath in sys.path: sys.path.remove(aToolsPath)
            
            G.deferredManager.sendToQueue(G.aToolsBar.delWindows, 1, "uninstall_delWindows") 
            G.deferredManager.sendToQueue(lambda *args:setup.install('', True), 1, "uninstall_install")
             
            #delete files
            if os.path.isdir(aToolsFolder): shutil.rmtree(aToolsFolder)
            
            cmds.warning("Uninstall complete! If you want to install aTools in the future, go to %s."%SITE_URL)
    
    
    def help(self, *args):
        webbrowser.open_new_tab(HELP_URL)
        
    def about(self, warnUpdate=None, *args):
        
        winName     = "aboutWindow"
        title       = "About" if not warnUpdate else "aTools has been updated!"
        if cmds.window(winName, query=True, exists=True): cmds.deleteUI(winName)
        window      = cmds.window( winName, title=title)
        form        = cmds.formLayout(numberOfDivisions=100)
        pos         = 10
        minWidth    = 300.0
        
        # Creating Elements
        object = cmds.image(image= uiMod.getImagePath("aTools_big"))
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        object = cmds.text( label="aTools - Version %s"%VERSION, font="boldLabelFont")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 80)] )
        #=========================================
        pos += 30
        object = cmds.text( label="More info:")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 80)] )
        #=========================================
        object = cmds.text( label="<a href=\"%s\">aTools website</a>"%SITE_URL, hyperlink=True)
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 220)] )
        #=========================================
        pos += 15
        object = cmds.text( label="Author: Alan Camilo")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 80)] )
        #=========================================
        object = cmds.text( label="<a href=\"http://www.alancamilo.com/\">www.alancamilo.com</a>", hyperlink=True)
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 220)] )
        #=========================================        pos += 15
        pos += 15
        object = cmds.text( label="Adaped: Michael Klimenko")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 80)] )
        #=========================================
        object = cmds.text( label="<a href=\"https://github.com/MKlimenko/\">My GitHub</a>", hyperlink=True)
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 220)] )
        #=========================================
        
        
        minWidth    = 550.0
        w           = 210
        object      = cmds.text( label="Do you like aTools?", w=w)
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos-50), ( object, 'right', 10)] )
        #=========================================        
        object = cmds.iconTextButton(label="Buy Me a Beer!", style="iconAndTextVertical", bgc=(.3,.3,.3), h=45, w=w, command=lambda *args: webbrowser.open_new_tab(DONATE_URL), image= uiMod.getImagePath("beer"), highlightImage= uiMod.getImagePath("beer copy"))
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos-30), ( object, 'right', 10)] )
        object = cmds.text( label="I really appreciate\nthe support!", w=w)
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos+20), ( object, 'right', 10)] )
        

        if warnUpdate:
            pos += 40
            object = cmds.text( label="aTools has been updated to version %s. What is new?"%VERSION, align="left")
            cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
            pos -= 20

            # open bit link - next big thing
            #webbrowser.open('http://bit.ly/2inAinL', new=0, autoraise=True)

        #=========================================
        pos += 40
        object = cmds.text( label=WHATISNEW, align="left")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        #=========================================
        
        for x in range(WHATISNEW.count("\n")):
            pos += 13
        pos += 25
        
        
        
        cmds.setParent( '..' )
        cmds.showWindow( window )
        
        whatsNewWidth   = cmds.text(object, query=True, width=True) + 15
        
        wid = whatsNewWidth if whatsNewWidth > minWidth else minWidth 
        cmds.window( winName, edit=True, widthHeight=(wid, pos))
        


    
    

class Update(object):
    
    def __init__(self):
        G.GT_wasUpdated     = G.GT_wasUpdated or None

        
    def tryUpdate(self):
        return True   

    def checkUpdates(self, gui, layout, *args):        

        if self.tryUpdate():     
                        
            if not G.GT_wasUpdated:                
                hasUpdate = self.hasUpdate()
                if hasUpdate != False:
                    cmds.iconTextButton(label="Updating...", style='textOnly', h=gui.hb, parent=layout)
                    cmds.progressBar("aToolsProgressBar", maxValue=100, width=50, parent=layout)
                    
                    if hasUpdate == "offline_update":
                        offlinePath     = aToolsMod.loadInfoWithUser("userPrefs", "offlinePath") 
                        offlineFolder   = offlinePath[0]
                        offlineFilePath = "%s%saTools.zip"%(offlineFolder, os.sep)
                        downloadUrl     = "file:///%s%saTools.zip"%(offlineFolder, os.sep)
                        fileModTime     = os.path.getmtime(offlineFilePath)
                        offline         = [offlineFilePath, fileModTime]
                    else:
                        downloadUrl     = DOWNLOAD_URL
                        offline         = None
            
                    function            = lambda *args:self.updateaTools(downloadUrl, offline)
                    G.deferredManager.sendToQueue(function, 1, "checkUpdates")
                    return                                              

        self.warnUpdate()
        self.warnAnimBot()

    
    def updateaTools(self, downloadUrl, offline=None, *args):
        
        aToolsPath      = aToolsMod.getaToolsPath(2)
        aToolsFolder    = aToolsMod.getaToolsPath()
        oldaToolsFolder = "%saTools.old"%aToolsPath
        tmpZipFile      = "%stmp.zip"%aToolsPath    
            
        #delete temp
        if os.path.isfile(tmpZipFile):     os.remove(tmpZipFile)
        if os.path.isdir(oldaToolsFolder): shutil.rmtree(oldaToolsFolder)  
        
        output = utilMod.download("aToolsProgressBar", downloadUrl, tmpZipFile)
        
        if not output:
            cmds.warning("Atools - Update failed.")
            return
        
        #rename aTools to old
        if os.path.isdir(aToolsFolder): os.rename(aToolsFolder, oldaToolsFolder)
        #uncompress file
        zfobj = zipfile.ZipFile(tmpZipFile)
        for name in zfobj.namelist():
            uncompressed = zfobj.read(name)        
            # save uncompressed data to disk
            filename  = utilMod.formatPath("%s%s"%(aToolsPath, name))
            
            d         = os.path.dirname(filename)
            
            if not os.path.exists(d): os.makedirs(d)
            if filename.endswith(os.sep): continue
            
            output = open(filename,'wb')
            output.write(uncompressed)
            output.close()
            
        #delete temp
        zfobj.close()
        if os.path.isfile(tmpZipFile):     os.remove(tmpZipFile)
        if os.path.isdir(oldaToolsFolder): shutil.rmtree(oldaToolsFolder)
        
        setup.install(offline=offline)

        #refresh
        G.GT_wasUpdated = True
        refreshATools()
    
       
    def hasUpdate(self):
        return False
    
    def warnUpdate(self):
            
        if G.GT_wasUpdated:
            G.GT_wasUpdated  = None            
        
        if lastUsedVersion != VERSION:
            aToolsMod.saveInfoWithUser("userPrefs", "lastUsedVersion", VERSION)  
            G.deferredManager.sendToQueue(lambda *args:self.about(warnUpdate=True), 50, "warnUpdate")     

    def warnAnimBot(self):

        try:
            import animBot
        except ImportError:
            pref = aToolsMod.loadInfoWithUser("userPrefs", "dontShowAnimBotWarningAgain")
            if not pref:
                G.deferredManager.sendToQueue(self.atoolsIsRetiring, 50, "warnAnimBot")

    def dontShowAgain(self, onOff):

        aToolsMod.saveInfoWithUser("userPrefs", "dontShowAnimBotWarningAgain", onOff)

    def atoolsIsRetiring(self):

        winName     = "atoolsIsRetiringWindow"
        title       = "aTools is Retiring..."

        if cmds.window(winName, query=True, exists=True):
            cmds.deleteUI(winName)

        window      = cmds.window( winName, title=title)
        form        = cmds.formLayout(numberOfDivisions=100)
        pos         = 10
        minWidth    = 300.0


        # Creating Elements
        object = cmds.text( label="aTools is giving place to animBot, a more robust,\nsmart and intuitive toolset. ", align="left")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 15

        object = cmds.image(image=uiMod.getImagePath("atools_animbot"))
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 100

        object = cmds.text( label="Three Steps for Full Awesomeness:", fn="boldLabelFont")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 20

        object = cmds.button(label="1) Install animBot and have fun!", bgc=(.3,.3,.3), h=45, w=280, command=installAnimBot)
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 45

        object = cmds.button(label="2) Watch the launch video.", bgc=(.3,.3,.3), h=45, w=280, command=lambda *args:webbrowser.open_new_tab("https://youtu.be/DezLHqXrDao"))
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 45

        object = cmds.button(label="3) Join the community.", bgc=(.3,.3,.3), h=45, w=280, command=lambda *args:webbrowser.open_new_tab("https://www.facebook.com/groups/1589262684419439"))
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 65

        object = cmds.text(align="left", label="The upgrade will be optional and although aTools\nwon't get feature updates, it will be available forever.\nPlease check the community for information about\nanimBot development progress.")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 80

        object = cmds.text( label="Enjoy!")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 20

        object = cmds.text( label="-Alan")
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 20

        object = cmds.checkBox(label="Don't show this again", value=False, changeCommand=self.dontShowAgain)
        cmds.formLayout( form, edit=True, attachForm=[( object, 'top', pos), ( object, 'left', 10)] )
        pos += 20


        pos += 10
        cmds.setParent( '..' )
        cmds.showWindow( window )

        cmds.window( winName, edit=True, widthHeight=(minWidth, pos))


class SelectionCounter(object):
    
    def __init__(self):
        self.defaultWidth   = 25
  
    def update(self):
        selectionCount = len(cmds.ls(selection=True))
        
        cmds.iconTextButton("selectionCounterButton", edit=True, label="%s"%selectionCount)
        cmds.iconTextButton("selectionCounterButton", edit=True, w=self.defaultWidth)
            
            
    def populateMenu(self, parent, *args):
        
        menuItens = cmds.popupMenu(parent, query=True, itemArray=True)
        
        if menuItens:
            for loopMenu in menuItens:
                if cmds.menuItem(loopMenu, query=True, exists=True): cmds.deleteUI(loopMenu)
        
        selection = cmds.ls(selection=True)
        selection.sort()
        
        for loopSel in selection:
            cmds.menuItem('%sMenu'%loopSel, label=loopSel, parent=parent, command=lambda x, loopSel=loopSel, *args: self.selectFromMenu(loopSel))
                    
    def selectFromMenu(self, selection):    
        cmds.select(selection)
                
    
    def switch(self, onOff):
           
        utilMod.killScriptJobs("G.selectionCounterScriptJobs")
        cmds.iconTextButton("selectionCounterButton", edit=True, visible=False)
    
        if onOff:
            cmds.iconTextButton("selectionCounterButton", edit=True, visible=True)
            
            G.selectionCounterScriptJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('SelectionChanged', self.update )))
        
        self.update()
    


class AutoSmartSnapKeys(object):
    
    def __init__(self):        
        utilMod.killScriptJobs("G.autoSmartSnapKeysJobs")               
    
    def switch(self, onOff):
        
        utilMod.killScriptJobs("G.autoSmartSnapKeysJobs")
                
        if onOff:
            G.autoSmartSnapKeysJobs.append(cmds.scriptJob(runOnce = False, killWithScene = False, event =('timeChanged', self.smartSnapKeys )))
    
    
    def smartSnapKeys(self):
        
        rangeVisible            = cmds.timeControl( G.playBackSliderPython, query=True, rangeVisible=True )
        
        if not rangeVisible: return        
        
        cmds.undoInfo(stateWithoutFlush=False)
        commandsMod.smartSnapKeys()
        cmds.undoInfo(stateWithoutFlush=True)

    
class CommandsAndHotkeys(object): 
    
    def __init__(self):
        
        self.allColors   = ["yellow", "green", "blue", "purple", "red", "orange", "gray"] 
        self.colorValues = {"yellow":(1,0.97,0.4), 
                            "green" :(0.44,1,0.53), 
                            "blue"  :(0.28,0.6,1), 
                            "purple":(0.640,0.215,0.995), 
                            "red"   :(1,0.4,0.4), 
                            "orange":(1,0.6,0.4), 
                            "gray"  :(0.5,0.5,0.5)}   

        self.reassignCommandsAtStartup()

    def openGui(self, *args):
        
        winName     = "commandsWindow"
        height      = 26
        commands    = []
        names       = [] 
        hotkeysDict = [[]]
        allHotkeys  = hotkeys.getHotkeys()
        totalItems  = sum(len(x) for x in allHotkeys)
        itemsCount  = 0
        aB          = 0
        totalColums = 2
        
        for n, loopHotkey in enumerate(allHotkeys):  
            if itemsCount > (totalItems/totalColums) * (aB+1): 
                aB += 1
                hotkeysDict.append([])        
            itemsCount += len(loopHotkey)
            for loopItem in loopHotkey:
                hotkeysDict[aB].append(loopItem)
                hotkeysDict[aB][-1]["colorValue"] = self.colorValues[self.allColors[n]]
                
        if cmds.window(winName, query=True, exists=True): cmds.deleteUI(winName)
        
        window          = cmds.window( winName, title = "Commands and Hotkeys")    
        mainLayout      = cmds.columnLayout(adjustableColumn=True)
        columnsLayout   = cmds.rowColumnLayout(numberOfColumns=totalColums)
        
        for loopColumn in range(totalColums):
        
            parent = cmds.rowColumnLayout(numberOfColumns=7, columnSpacing=([2,5], [3,3], [4,3], [5,1], [6,5], [7,5]), parent=columnsLayout)
              
            cmds.text(label='Command', h=height)
            cmds.text(label='Ctl', h=height)
            cmds.text(label='Alt', h=height)
            cmds.text(label='Key', h=height)
            cmds.text(label='', h=height)
            cmds.text(label='Set Hotkey', h=height)
            cmds.text(label='Assigned to', align="left", h=height)
        
            for loopIndex, loopCommand in enumerate(hotkeysDict[loopColumn]):  
                
                          
                command = loopCommand["command"]
                name    = loopCommand["name"] 
                key     = loopCommand["hotkey"]
                alt     = loopCommand["alt"]
                ctl     = loopCommand["ctl"]  
                toolTip = loopCommand["toolTip"]  
                color   = loopCommand["colorValue"]
                
                hotkeyData = aToolsMod.loadInfoWithUser("hotkeys", name) 
                if hotkeyData != None: 
                    key     = hotkeyData[0]
                    alt     = hotkeyData[1]
                    ctl     = hotkeyData[2]
                
                cmds.button("command%s"%name, label=utilMod.toTitle(name), command=command, annotation=toolTip, h=height, bgc=color, parent=parent)
                cmds.checkBox('ctl%s'%name, label='', value=ctl, changeCommand=lambda x, name=name, *args:self.updateHotkeyCheck(name), h=height, parent=parent)
                cmds.checkBox('alt%s'%name, label='', value=alt, changeCommand=lambda x, name=name, *args:self.updateHotkeyCheck(name), h=height, parent=parent)
                cmds.scrollField('key%s'%name, w=80, text=key, keyPressCommand=lambda x, name=name, *args:self.updateHotkeyCheck(name), h=height, parent=parent)
                cmds.button(label=" ", h=height, parent=parent)
                self.popSpecialHotkeys(name)
                cmds.button(label='>',           command=lambda x, name=name, command=command, *args: self.setHotkey(self.getHotkeyDict([name], [command])), h=height, parent=parent)
                cmds.text("query%s"%name, align="left", label=self.hotkeyCheck(key, ctl, alt), font="plainLabelFont", h=height, parent=parent)
                
                commands.append(command)
                names.append(name)
                
                #cmds.button(label="Set Hotkey", command=lambda *args: getHotkeyDict([name], [command], [key], [alt], [ctl], [cmd]))
                self.updateHotkeyCheck(name)        
                
                
        #cmds.rowLayout(numberOfColumns=2, columnAttach=([1, 'left', 0],[2, 'right', 0]), adjustableColumn=2)
        cmds.button(label="Load Defaults", command=lambda *args: self.loadHotkeys(True), parent=mainLayout)
        cmds.button(label="Set All Hotkeys", command=lambda *args: self.setHotkey(self.getHotkeyDict(names, commands)), parent=mainLayout)
        
        cmds.showWindow( window )
    
    def loadHotkeys(self, defaults=False):
        
        allHotkeys  = hotkeys.getHotkeys()
        hotkeysDict = []
        
        for n, loopHotkey in enumerate(allHotkeys):  
            for loopItem in loopHotkey:
                hotkeysDict.append(loopItem)
                
        
        for loopIndex, loopCommand in enumerate(hotkeysDict):  
            
                      
            command = loopCommand["command"]
            name    = loopCommand["name"] 
            key     = loopCommand["hotkey"]
            alt     = loopCommand["alt"]
            ctl     = loopCommand["ctl"]  
            toolTip = loopCommand["toolTip"]  
            
            if not defaults:
                hotkeyData = aToolsMod.loadInfoWithUser("hotkeys", name) 
                if hotkeyData != None: 
                    key     = hotkeyData[0]
                    alt     = hotkeyData[1]
                    ctl     = hotkeyData[2]
            
            
            cmds.checkBox('ctl%s'%name, edit=True, value=ctl)
            cmds.checkBox('alt%s'%name, edit=True, value=alt)
            cmds.scrollField('key%s'%name, edit=True, text=key)
            
            self.updateHotkeyCheck(name)
    
    
    def popSpecialHotkeys(self, name):
        cmds.popupMenu("popSpecialHotkeysMenu", button=1)
        
        
        for loopKey in KEYSLIST:
            if loopKey == "":
                cmds.menuItem( divider=True )
            else:
                cmds.menuItem       ("menu%s"%loopKey, label=str(loopKey), command=lambda x, name=name, loopKey=loopKey, *args: self.typeSpecialKey(name, loopKey))    
        
    
        cmds.setParent( '..', menu=True )
    
    def typeSpecialKey(self, name, text):
        cmds.scrollField("key%s"%name, edit=True, text=text)
        self.updateHotkeyCheck(name)
    
    def getHotkeyDict(self, names, commands):
        
        hotkeysDict = []
        
        for n, loopName in enumerate(names):
            command = commands[n]
            name    = loopName
            key     = cmds.scrollField("key%s"%loopName, query=True, text=True)
            alt     = cmds.checkBox("alt%s"%loopName, query=True, value=True)
            ctl     = cmds.checkBox("ctl%s"%loopName, query=True, value=True)
    
            if len(key) > 1: key = key[0]
            
            hotkeysDict.append({"name":"%s"%name,
                                "command":"%s"%command,
                                "hotkey":"%s"%key,
                                "alt":alt,
                                "ctl":ctl
                                })
            
            
        return hotkeysDict
    
    
    def setHotkey(self, hotkeyDict):
        message = "Are you sure?\n\n"    
        
        #format message
        for loopIndex, loopCommand in enumerate(hotkeyDict):
                
            command = loopCommand["command"]
            name    = loopCommand["name"]
            key     = loopCommand["hotkey"]
            alt     = loopCommand["alt"]
            ctl     = loopCommand["ctl"]
            q       = cmds.text("query%s"%name, query=True, label=True)
            
            commandKeys = ""
            if ctl: commandKeys += "Ctl + "
            if alt: commandKeys += "Alt + "
            
            message += "%s (%s%s)"%(name, commandKeys, key)
            if q != "": message += " is assigned to: %s"%q
            message += "\n"
            
        confirm = cmds.confirmDialog( title='Confirm', message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
    
        if confirm == 'Yes':    
            for loopIndex, loopCommand in enumerate(hotkeyDict):
                
                command = loopCommand["command"]
                name    = loopCommand["name"]
                key     = loopCommand["hotkey"]
                alt     = loopCommand["alt"]
                ctl     = loopCommand["ctl"]       
                
                cmds.nameCommand(name, command='python("%s");'%command, annotation=name)
                cmds.hotkey(k=key, alt=alt, ctl=ctl, name=name)
    
                aToolsMod.saveInfoWithUser("hotkeys", name, [key, alt, ctl]) 
                self.updateHotkeyCheck(name)
                
            cmds.savePrefs( hotkeys=True )
           
    
    def hotkeyCheck(self, key, ctl, alt):
        if key != "":
            q = cmds.hotkey(key, query=True, alt=alt, ctl=ctl, name=True)
            if q != None and "NameCom" in q: q = q[7:]
            return q
        else:
            return ""
    

    def updateHotkeyCheck(self, name):

        function = lambda name=name, *args: self.delayedUpdateHotkeyCheck(name)
        G.deferredManager.sendToQueue(function, 1, "updateHotkeyCheck")
                
        
    def delayedUpdateHotkeyCheck(self, name): 
        command = cmds.button("command%s"%name, query=True, label=True)
        key     = cmds.scrollField("key%s"%name, query=True, text=True)
        ctl     = cmds.checkBox("ctl%s"%name, query=True, value=True)
        alt     = cmds.checkBox("alt%s"%name, query=True, value=True) 
        
        
        if len(key) > 1 and key not in KEYSLIST: 
            key = key[0]
            cmds.scrollField("key%s"%name, edit=True, text=key)
        
        
        label = self.hotkeyCheck(key, ctl, alt)
        
        
        if label == None: label = ""
        
        cmds.text("query%s"%name, edit=True, label=label, font="plainLabelFont")    
        if utilMod.toTitle(label) != command: cmds.text("query%s"%name, edit=True, font="boldLabelFont")
        
    
    def reassignCommandsAtStartup(self):
        
        allHotkeys  = hotkeys.getHotkeys()
        hotkeysDict = []
        
        for n, loopHotkey in enumerate(allHotkeys):  
            for loopItem in loopHotkey:
                hotkeysDict.append(loopItem)
                
        
        for loopCommand in hotkeysDict:  
                      
            command = loopCommand["command"]
            name    = loopCommand["name"] 
            key     = loopCommand["hotkey"]
            alt     = loopCommand["alt"]
            ctl     = loopCommand["ctl"]  
            #toolTip = loopCommand["toolTip"]  
            
            label   = self.hotkeyCheck(key, ctl, alt)        
                       
            if label == name: cmds.nameCommand(name, command='python("%s");'%command, annotation=name)



    
    
        

#=========================================================



def shelfButton(*args):
    topShelf        = mel.eval('$nul = $gShelfTopLevel')
    currentShelf    = cmds.tabLayout(topShelf, q=1, st=1)
    command         = "from aTools.animTools.animBar import animBarUI; animBarUI.show('toggle')"
    
    cmds.shelfButton(parent=currentShelf, annotation='aTools ON/OFF', imageOverlayLabel="aTools", i='commandButton.xpm', command=command)
          

def refreshATools(*args): 
    G.deferredManager.sendToQueue(refreshAToolsDef, 1, "refreshATools")
    

def refreshAToolsDef():
    from aTools.animTools.animBar import animBarUI;     importlib.reload(animBarUI)
    animBarUI.show('refresh')


    # animBot

def installAnimBot(*args):
    installFileFolder = os.path.normpath(os.path.dirname(os.path.dirname(__file__)))
    installFilePath = os.path.join(installFileFolder, "animBot Drag'n Drop Install.mel").replace("\\", "/") # fix for windows
    mel.eval("source \"%s\";"%installFilePath)

def watchLaunchVideo(*args):
    webbrowser.open_new_tab("https://youtu.be/DezLHqXrDao")

def joinTheCommunity(*args):
    webbrowser.open_new_tab("https://www.facebook.com/groups/1589262684419439")
