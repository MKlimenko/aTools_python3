from maya import cmds, mel
import os, shutil, urllib.request, urllib.error, urllib.parse, shutil, zipfile
import importlib

def hasInternet(url):
   try:
       proxy    = urllib.request.ProxyHandler({})
       opener   = urllib.request.build_opener(proxy)
       urllib.request.install_opener(opener)
       response = urllib.request.urlopen(url, timeout=60)
       return True
   except: pass
   return False

def install():
    if aToolsZipPath.split(os.sep)[-1] != 'aTools.zip' or not os.path.isfile(aToolsZipPath):
        cmds.confirmDialog(message="%sCouldnt find aTools.zip in this location, installation will stop."%os.sep.join(aToolsZipPath.split(os.sep)[:-1]))
        return   
    aToolsOfflineInstall(aToolsZipPath)

def formatPath(path):
    path = path.replace('/', os.sep)
    path = path.replace('\\\\', os.sep)
    return path

def download(downloadUrl, saveFile):
    
    if not hasInternet(downloadUrl): 
        cmds.warning('Error trying to install.')
        return
        
    try:    response        = urllib.request.urlopen(downloadUrl, timeout=60)          
    except: pass
    
    if response is None: 
        cmds.warning('Error trying to install.')
        return    
    
    fileSize        = int(response.info().getheaders('Content-Length')[0])
    fileSizeDl      = 0
    blockSize       = 128
    output          = open(saveFile,'wb')    
    progBar         = mel.eval('$tmp = $gMainProgressBar')    
    
    cmds.progressBar( progBar,
                        edit=True,
                        beginProgress=True,
                        status='Downloading aTools...',
                        progress=0,
                        maxValue=100 )    
    
    while True:
        buffer = response.read(blockSize)
        if not buffer:
            output.close()
            cmds.progressBar(progBar, edit=True, progress=100)  
            cmds.progressBar(progBar, edit=True, endProgress=True)          
            break
    
        fileSizeDl += len(buffer)
        output.write(buffer)
        p = float(fileSizeDl) / fileSize *100
        
        cmds.progressBar(progBar, edit=True, progress=p)  
        
    return output


def aToolsOfflineInstall(offlineFilePath):

    mayaAppDir      = mel.eval('getenv MAYA_APP_DIR')    
    aToolsPath      = mayaAppDir + os.sep + 'scripts'
    aToolsFolder    = aToolsPath + os.sep + 'aTools' + os.sep
    tmpZipFile      = '%s%stmp.zip'%(aToolsPath, os.sep)
    offlineFileUrl  = r'file:///%s'%offlineFilePath
        
    if os.path.isfile(tmpZipFile):     os.remove(tmpZipFile)   
    if os.path.isdir(aToolsFolder): shutil.rmtree(aToolsFolder)      
    
    output = download(offlineFileUrl, tmpZipFile)    
    
    zfobj = zipfile.ZipFile(tmpZipFile)
    for name in zfobj.namelist():
        uncompressed = zfobj.read(name)
    
        filename  = formatPath('%s%s%s'%(aToolsPath, os.sep, name))        
        d         = os.path.dirname(filename)
        
        if not os.path.exists(d): os.makedirs(d)
        if filename.endswith(os.sep): continue
        
        output = open(filename,'wb')
        output.write(uncompressed)
        output.close()
        
    zfobj.close()
    if os.path.isfile(tmpZipFile):     os.remove(tmpZipFile)
    from aTools import setup; importlib.reload(setup); setup.install([offlineFilePath, False]) 
    cmds.evalDeferred("from aTools.animTools.animBar import animBarUI; importlib.reload(animBarUI); animBarUI.show(\'refresh\')")     


install()