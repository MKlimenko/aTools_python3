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
from aTools.commonMods import uiMod
from aTools.commonMods import utilMod
from aTools.commonMods import animMod
from aTools.commonMods import aToolsMod


class SpaceSwitch(object):    

    def popupMenu(self):
        cmds.popupMenu(postMenuCommand=self.populateMenu, button=1)
    
    def populateMenu(self, menu, *args):
                  
        uiMod.clearMenuItems(menu)
        
        tokenCustomDivider  = False 
        selObjects          = cmds.ls(selection=True)
        
        if not selObjects: return    
        
        channels    = animMod.getAllChannels()
        channelList = {}
        tokenList   = []
               
        for n, loopObjectChannel in enumerate(channels):
            obj = selObjects[n]
            if loopObjectChannel:
                for loopChannel in loopObjectChannel:
                    tokens = animMod.getTokens(obj, loopChannel)
                    if tokens and len(tokens) > 1: 
                        if loopChannel not in channelList: channelList[loopChannel] = {"objects":[], "tokens":[]}
                        channelList[loopChannel]["objects"].append(obj)
                        channelList[loopChannel]["tokens"].append(tokens)
                        
        
        for loopChannelList in channelList:
            newMenu         = cmds.menuItem(subMenu=True, label=utilMod.toTitle(loopChannelList), parent=menu)
            objects         = channelList[loopChannelList]["objects"]
            tokens          = channelList[loopChannelList]["tokens"]
            mergedTokens    = utilMod.mergeLists(tokens)                      
            tokenDict       = []
            
            for loopMergedTokens in mergedTokens:
                tokenDict.append({"token":loopMergedTokens, "objects":[]})
                for n, loopObject in enumerate(objects):
                    t = tokens[n]
                    if loopMergedTokens in t:
                        tokenDict[-1]["objects"].append(loopObject)  
        
            cmds.radioMenuItemCollection(parent=menu)            
            
            for n, loopTokenDict in enumerate(tokenDict):
                tokenCustomDivider  = True
                token               = loopTokenDict["token"]
                objects             = loopTokenDict["objects"]
                selectedList        = [cmds.getAttr("%s.%s"%(loopObj, loopChannelList)) for loopObj in objects]                
                radioSelected       = False
                
                
                if len(set(selectedList)) == 1:
                    if selectedList[0] == n:
                        radioSelected   = True
                
                cmds.menuItem(label=utilMod.toTitle(token), radioButton=radioSelected, parent=newMenu, command=lambda x, objects=objects, channel=loopChannelList, token=token, *args:self.spaceSwitch([objects, channel, token]))
            
             
            #ALL KEYS
            cmds.menuItem( divider=True, parent=newMenu)
            newMenu = cmds.menuItem(subMenu=True, label='All Keys', parent=newMenu)
            
            cmds.radioMenuItemCollection(parent=newMenu)
            
            for n, loopTokenDict in enumerate(tokenDict):
                token           = loopTokenDict["token"]
                objects         = loopTokenDict["objects"]
                selectedList    = [cmds.getAttr("%s.%s"%(loopObj, loopChannelList)) for loopObj in objects]                
                radioSelected   = False
                
                if len(set(selectedList)) == 1:
                    if selectedList[0] == n:
                        radioSelected   = True
                
                cmds.menuItem(label=utilMod.toTitle(token), radioButton=radioSelected, parent=newMenu, command=lambda x, objects=objects, channel=loopChannelList, token=token, *args:self.spaceSwitch([objects, channel, token], all=True))

        # CUSTOM SWITCH
        allCustomSwitch     = aToolsMod.loadInfoWithUser("spaceSwitch", "customSwitch") or []
        channelboxSelObjs   = animMod.channelBoxSel()
        
        if channelboxSelObjs:
            obj            = ".".join(channelboxSelObjs[0].split(".")[:-1])
            selectedSwitch = [loopAttr.split(".")[-1] for loopAttr in channelboxSelObjs if utilMod.isDynamic(obj, loopAttr.split(".")[-1])]
            if len(selectedSwitch) > 0 and selectedSwitch not in allCustomSwitch: 
                allCustomSwitch.append(selectedSwitch)            
                aToolsMod.saveInfoWithUser("spaceSwitch", "customSwitch", allCustomSwitch)  
        
        
        # populate menu
        if len(allCustomSwitch) > 0:  
                
            divider             = False
            customSwitchesAdded = []
            customSwitchesMenu  = []
            
            for loopObj in selObjects:
                       
                for loopCustomSwitch in sorted(allCustomSwitch, key=len, reverse=True):
                    
                    if len(loopCustomSwitch) == 0: continue                    
                    
                    switchName  = utilMod.getNameSpace([loopObj])[1][0].split(".")[0]
                    exit        = False
                    
                    for loopAttr in loopCustomSwitch:
                        objAttr = "%s.%s"%(loopObj, loopAttr)
                        if not cmds.objExists(objAttr):
                            exit = True
                            break
                            
                    if exit: continue
                         
                    customSwitchesMenu.append({"objects":[loopObj], "switches":loopCustomSwitch})
                    
                    for loopMenu in customSwitchesMenu[:-1]:
                        if loopObj in loopMenu["objects"] and len(loopCustomSwitch) < len(loopMenu["switches"]) and utilMod.listIntersection(loopMenu["switches"], loopCustomSwitch) == loopCustomSwitch:
                            customSwitchesMenu.pop()
                            break
                        if loopCustomSwitch == loopMenu["switches"]:
                            loopMenu["objects"].append(loopObj)
                            customSwitchesMenu.pop()
                            break
                     
                    
            for loopSwitchMenu in customSwitchesMenu:
                
                objects     = loopSwitchMenu["objects"]
                switches    = loopSwitchMenu["switches"]
                switchName  = ", ".join(list(set(utilMod.getNameSpace(objects)[1])))
                    
                if not divider and tokenCustomDivider: divider = cmds.menuItem(divider=True, parent=menu)  
  
                cmds.radioMenuItemCollection(parent=menu)
                
                newMenu         = cmds.menuItem(subMenu=True, label=switchName, parent=menu)
                radioSelected   = []
                 
                for loopCustomSwitchAttr in switches:
                    switchAttr      = loopCustomSwitchAttr.split(".")[-1]
                    objAttr         = "%s.%s"%(objects[0], switchAttr)
                    minValue        = cmds.addAttr(objAttr, query=True, minValue=True)
                    maxValue        = cmds.addAttr(objAttr, query=True, maxValue=True)
                    currValue       = cmds.getAttr(objAttr)
                    radioSelected.append((currValue == maxValue))
                    
                    cmds.menuItem(label=switchAttr, radioButton=radioSelected[-1], parent=newMenu, command=lambda x, objects=objects, switchAttr=switchAttr, switches=switches, *args:self.spaceSwitch([objects, switchAttr, switches], mode="custom"))
                
                switchAttr      = "message"
                radioSelected   = (list(set(radioSelected)) == [False])                    
                cmds.menuItem(label="None", radioButton=radioSelected, parent=newMenu, command=lambda x, objects=objects, switchAttr=switchAttr, switches=switches, *args:self.spaceSwitch([objects, switchAttr, switches], mode="custom"))
                    
                #ALL KEYS
                
                cmds.menuItem( divider=True, parent=newMenu)
                allMenu = cmds.menuItem(subMenu=True, label='All Keys', parent=newMenu) 
                radioSelected   = []
                cmds.radioMenuItemCollection(parent=menu)
                
                
                for loopCustomSwitchAttr in switches:
                    switchAttr      = loopCustomSwitchAttr.split(".")[-1]
                    objAttr         = "%s.%s"%(objects[0], switchAttr)
                    minValue        = cmds.addAttr(objAttr, query=True, minValue=True)
                    maxValue        = cmds.addAttr(objAttr, query=True, maxValue=True)
                    currValue       = cmds.getAttr(objAttr)
                    radioSelected.append((currValue == maxValue))
                    cmds.menuItem(label=switchAttr, radioButton=radioSelected[-1], parent=allMenu, command=lambda x, objects=objects, switchAttr=switchAttr, switches=switches, *args:self.spaceSwitch([objects, switchAttr, switches], all=True, mode="custom"))
                
                switchAttr      = "message"
                radioSelected   = (list(set(radioSelected)) == [False])  
                cmds.menuItem(label="None", radioButton=radioSelected, parent=allMenu, command=lambda x, objects=objects, switchAttr=switchAttr, switches=switches, *args:self.spaceSwitch([objects, switchAttr, switches], all=True, mode="custom"))
                
                #DELETE
                
                cmds.menuItem(label="Remove", parent=newMenu, command=lambda x, switches=switches, *args:self.removeCustomSwitch(switches))
    
    def removeCustomSwitch(self, switch):
        allCustomSwitch     = aToolsMod.loadInfoWithUser("spaceSwitch", "customSwitch") or []
        
        allCustomSwitch.remove(switch)
        aToolsMod.saveInfoWithUser("spaceSwitch", "customSwitch", allCustomSwitch)
         
    def spaceSwitch(self, args, all=False, mode="token"):
        
        cmds.refresh(suspend=True)
        
        if mode == "token":    switch = self.spaceSwitchToken
        elif mode == "custom": switch = self.spaceSwitchCustom        
        
        objects     = args[0] 
        attr        = args[1]    
        currSel     = cmds.ls(selection=True)      
        currFrame   = cmds.currentTime(query=True)
        getCurves   = animMod.getAnimCurves()
        animCurves  = getCurves[0]
        getFrom     = getCurves[1]         
        
        if animCurves:
            if all: keysSel = animMod.getTarget("keyTimes", animCurves, getFrom)
            else:   keysSel = animMod.getTarget("keysSel", animCurves, getFrom)
            
            keysSel = utilMod.mergeLists(keysSel)    
            if keysSel == []:
                 keysSel = [currFrame]   
        else:
            keysSel = [currFrame]
        
        frames = keysSel
        
        for loopObj in currSel:
            if loopObj not in objects: continue
            if not cmds.objExists("%s.%s"%(loopObj, attr)):continue
        
            animMod.createDummyKey([loopObj])
            
            getCurves       = animMod.getAnimCurves(True)
            animCurves      = getCurves[0]
            
            animMod.deleteDummyKey([loopObj])     
            
            for loopFrame in frames:                   
                cmds.currentTime(loopFrame)  
                
                matrix     = cmds.xform(loopObj, query=True, ws=True, matrix=True)
                rotation    = cmds.xform(loopObj, query=True, ws=True, rotation=True)
                              
                switch(loopObj, args)                                
                cmds.xform(loopObj, ws=True, matrix=matrix)  
                cmds.xform(loopObj, ws=True, rotation=rotation)
                
                        
            animMod.eulerFilterCurve(animCurves) 
            
                   
        cmds.currentTime(currFrame)
        cmds.refresh(suspend=False)
        
    def spaceSwitchCustom(self, obj, args):
        
        objects, attr, switchAttList    = args                
        objAttr                         = "%s.%s"%(obj, attr)
                    
        for loopAttr in switchAttList:
                    
            loopObjAttr     = "%s.%s"%(obj, loopAttr)
            minValue        = cmds.addAttr(loopObjAttr, query=True, minValue=True)
            maxValue        = cmds.addAttr(loopObjAttr, query=True, maxValue=True)
            value           = minValue if objAttr != loopObjAttr else maxValue            
            
            cmds.setAttr(loopObjAttr, value)
        
    def spaceSwitchToken(self, obj, args):
        
        objects, attr, switchTo     = args       
        enumTokens                  = animMod.getTokens(obj, attr)
        value                       = 0
        switchToNum                 = None
        
        for loopToken in enumTokens:
            splitValue = loopToken.split("=")
            
            if splitValue:
                if len(splitValue) > 1:
                    loopToken = splitValue[0]
                    value     = eval(splitValue[1])
            
            
            if switchTo == loopToken:
                switchToNum = value
                break
            
            value += 1
            
            
        if switchToNum != None:  
            cmds.setAttr("%s.%s"%(obj, attr), switchToNum)     
 