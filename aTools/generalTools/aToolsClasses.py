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
from aTools.generalTools.aToolsGlobals import aToolsGlobals as G
from maya import OpenMaya, OpenMayaAnim, OpenMayaUI
    
class DeferredManager(object):
    
    def __init__(self):
                        
        if G.deferredManager: self.queue = G.deferredManager.queue
        else:                 self.queue = {} 
        
        #self.queue = {}#temp
         
            
        G.deferredManager   = self        
        self.running        = False
        self.nextId         = None
        
        
        #test
        
        """
        self.sendToQueue((lambda *args:self.printe('functionHigh1')), 1)
        self.sendToQueue((lambda *args:self.printe('functionLow1')), 100)
        self.sendToQueue((lambda *args:self.printe('functionHigh2')), 1)
        self.sendToQueue((lambda *args:self.printe('functionMedium1')), 50, "id1")
        self.sendToQueue((lambda *args:self.printe('functionMedium2')), 50, "id1")
        self.sendToQueue((lambda *args:self.printe('functionMedium3')), 50, "id1")
        self.sendToQueue((lambda *args:self.printe('functionLow2')), 100)
        self.sendToQueue((lambda *args:self.printe('functionLow3')), 100)
        self.sendToQueue((lambda *args:self.printe('functionLow4')), 100)
        self.sendToQueue((lambda *args:self.printe('functionLow5')), 100)
        self.sendToQueue((lambda *args:self.printe('functionMedium4')), 50, "id2")
        self.sendToQueue((lambda *args:self.printe('functionHigh3')), 1)
        self.sendToQueue((lambda *args:self.printe('functionLow6')), 100)
        self.sendToQueue((lambda *args:self.printe('functionLow7')), 100)
        self.sendToQueue((lambda *args:self.printe('functionLow8')), 100)
        self.sendToQueue((lambda *args:self.printe('functionLow9')), 100)
        self.sendToQueue((lambda *args:self.printe('functionMedium5')), 50, "id2")
        self.sendToQueue((lambda *args:self.printe('functionMedium6')), 50, "id2")
        self.sendToQueue((lambda *args:self.printe('functionMedium10')), 50)
        self.sendToQueue((lambda *args:self.printe('functionMedium11')), 50)
        self.sendToQueue((lambda *args:self.printe('functionLow10')), 100)
        self.sendToQueue((lambda *args:self.printe('functionLow11')), 100)
        self.sendToQueue((lambda *args:self.printe('functionLow12')), 100)
        self.sendToQueue((lambda *args:self.printe('functionMedium7')), 50, "id1")
        self.sendToQueue((lambda *args:self.printe('functionMedium8')), 50, "id1")
        self.sendToQueue((lambda *args:self.printe('functionMedium9')), 50, "id1")
        """
        return
        self.runQueue()
        
    def printe(self, what):
        #pass
        print(what)   
    
    def sendToQueue(self, function, priority=1, id="default"):            

        if priority not in self.queue:      self.queue[priority] = {}
        if id not in self.queue[priority]:  self.queue[priority][id] = []            
        self.queue[priority][id].append(function) 
            
        
        if not self.running: 
            self.running = True
            cmds.evalDeferred(self.runQueue)
    
   
        
    def runQueue(self): 
        
        if len(self.queue) == 0: return       
        
        
        self.running    = True
        priority        = sorted(self.queue)[0]
        
        if len(self.queue[priority]) > 0:
            keys        = list(self.queue[priority].keys())
            id          = self.nextId or keys[0]
            if id not in self.queue[priority]: id = keys[0]
            function    = self.queue[priority][id].pop(0)
            
            
            try: function()
            except: print(("aTools Deferred Manager Error#%s/%s: %s"%(priority, id, function)))
            
            self.nextId = keys[0]            
            
            if id in keys:
                index = keys.index(id)
                if index < len(keys)-1: self.nextId = keys[index+1]
                else:                   self.nextId = keys[0] 
                    
            if id in self.queue[priority] and len(self.queue[priority][id]) == 0: self.queue[priority].pop(id, None)
        
        if len(self.queue[priority]) == 0: self.queue.pop(priority, None)

            

 
                
        if len(self.queue) > 0:
            cmds.evalDeferred(self.runQueue)
            return       
                
        
        self.running = False
        
    def removeFromQueue(self, id):
        
        for loopChunk in self.queue:
            chunk = self.queue[loopChunk]
        
            if id in chunk: chunk.pop(id, None) 
        
        
        
    def inQueue(self, id):        
        
        results = 0
        
        for loopChunk in self.queue:
            chunk = self.queue[loopChunk]
            
            if id in chunk: results += len(chunk[id])
            
            
        return results
    
         
  
DeferredManager()
    
class TimeoutInterval(object):
        
    def __init__(self):
        
        if not G.aToolsBar: return
        G.aToolsBar.timeoutInterval = self               
        G.deferredManager.removeFromQueue("timeoutInterval")
        self.queue                  = []
        
    def setTimeout(self, function, sec, offset=0, xTimes=1, id=None, interval=None):
        
        timeNow     = cmds.timerX()
        timeToExec  = timeNow + sec + offset
        
        self.queue.append([function, timeToExec, sec, xTimes, id, interval])    
        self.runQueue()
    
    def runQueue(self):        
        
        if len(self.queue) > 0:
            timeNow = cmds.timerX()
            for loopQueue in self.queue:
                timeToExec = loopQueue[1] 
                if timeToExec <= timeNow:
                    function    = loopQueue[0]
                    sec         = loopQueue[2]
                    xTimes      = loopQueue[3]
                    id          = loopQueue[4]
                    interval    = loopQueue[5]
                    timeToExec  = timeNow + sec
                    xTimes      -= 1
                    
                    function() 
                    if loopQueue in self.queue: self.queue.remove(loopQueue)
                    if xTimes > 0 or interval: self.queue.append([function, timeToExec, sec, xTimes, id, interval])
                            
        if len(self.queue) > 0:
            priority = 1
            for loopQueue in self.queue:
                interval    = loopQueue[5]
                id          = loopQueue[4]
                if interval: 
                    priority = 50
                    break
      
            
            G.deferredManager.sendToQueue(self.runQueue, priority, "timeoutInterval")
    
    def setInterval(self, function, sec, offset=0, id="general"):
        self.setTimeout(function, sec, offset, id=id, interval=True)
        
    def stopInterval(self, idToStop):
        
        for loopQueue in self.queue:
            id          = loopQueue[4]
            if id == idToStop: self.queue.remove(loopQueue)  
            
    def removeFromQueue(self, id):
        
        toRemove = []
        
        for loopQueue in self.queue:
            loopId          = loopQueue[4]            
            if id == loopId: toRemove.append(loopQueue)
            
        for loopRemove in toRemove: self.queue.remove(loopRemove)
            
    
TimeoutInterval()

class CreateAToolsNode(object):
    
    def __init__(self):    
        if not G.aToolsBar: return
        G.aToolsBar.createAToolsNode = self  
        
    def __enter__(self):
        #print "enter"
        G.animationCrashRecovery.checkNodeCreated = False
    
    def __exit__(self, type, value, traceback):
        #print "exit"
        G.animationCrashRecovery.checkNodeCreated = True

CreateAToolsNode()


class CallbackManager(object):
    
    def __init__(self):
        
            
        if G.callbackManager: self.queue = G.callbackManager.queue
        else:                 self.queue = {} 
        
        G.callbackManager   = self
        
        self.clearQueue()
    
    def __del__(self):
        #print "CallbackManager deleted"
        self.clearQueue()    
        
    def sendToQueue(self, job, type, id):
        
        #print "sendToQueue", job, type, id
        newQueue = {"job":job, "type":type}
        
        if id not in self.queue: self.queue[id] = []
        
        self.queue[id].append(newQueue)
        
      
    def removeFromQueue(self, id):
        
        if id not in self.queue: return
        
        toRemove = []
        
        for loopQueue in self.queue[id]:
            loopJob     = loopQueue["job"]
            loopType    = loopQueue["type"]
                
            if loopType == "scriptJob": self.removeScriptJob(loopJob, loopType, id)
            else:                       self.removeApiCallback(loopJob, loopType, id)
                                
            toRemove.append(loopQueue)
            
        for loopRemove in toRemove: self.queue[id].remove(loopRemove)
            
        if len(self.queue[id]) == 0: self.queue.pop(id, None)
    
    def removeScriptJob(self, job, type, id):

        try:
            if cmds.scriptJob(exists=job):  cmds.scriptJob(kill=job, force=True)    
        except:                             print(("aTools CallbackManager could not remove job %s/%s/%s"%(id, type, job)))
 
        
    def removeApiCallback(self, job, type, id):
        #print "removeApiCallback", job, type, id
        
        function = eval("%s.removeCallback"%type)
                
        try:    function(job)
        except: cmds.warning("aTools CallbackManager could not remove job %s/%s/%s"%(id, type, job))
             
    
    def clearQueue(self):    
       
        for loopId in list(self.queue.keys()): self.removeFromQueue(loopId)
        
        
    def inQueue(self, id):        
        
        results = 0
        
        for loopId in list(self.queue.keys()):
            
            if loopId == id: results += len(self.queue[id])
            
            
        return results
    

CallbackManager()  

