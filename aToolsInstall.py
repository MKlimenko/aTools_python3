from maya import cmds, mel
import os, shutil, urllib.request, urllib.error, urllib.parse, shutil, zipfile, importlib

def formatPath(path):
    path = path.replace('/', os.sep)
    path = path.replace('\\', os.sep)
    return path

def download(downloadUrl, saveFile):
        
    try:    response        = urllib.request.urlopen(downloadUrl, timeout=60)          
    except: pass
    
    if response is None: 
        cmds.warning('Error trying to install.')
        return
    
    fileSize        = int(response.info().get('Content-Length')[0])
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


def aToolsInstall():

    mayaAppDir      = mel.eval('getenv MAYA_APP_DIR')    
    aToolsPath      = mayaAppDir + os.sep + "scripts"
    aToolsFolder    = aToolsPath + os.sep + "aTools" + os.sep
    tmpZipFile      = "%s%stmp.zip"%(aToolsPath, os.sep)    
    DOWNLOAD_URL    = "https://github.com/MKlimenko/aTools_python3/releases/download/v2.04/aTools.zip"
        
    if os.path.isfile(tmpZipFile):     os.remove(tmpZipFile)   
    if os.path.isdir(aToolsFolder): shutil.rmtree(aToolsFolder)      
    
    output = download(DOWNLOAD_URL, tmpZipFile)    
    
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

    #delete temp
    zfobj.close()
    if os.path.isfile(tmpZipFile):     os.remove(tmpZipFile)
    
    from aTools import setup; setup.install()    
    
    #refresh
    cmds.evalDeferred("from aTools.animTools.animBar import animBarUI; importlib.reload(animBarUI); animBarUI.show('refresh')")
       
aToolsInstall()