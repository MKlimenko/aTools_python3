# aTools for Python3

Newer versions of Maya (starting from Maya 2022) have switched to Python3, which led to incompatibility with older Python scripts. One of the well-known and loved script toolbox is called [aTools](https://camiloalan.wixsite.com/atoolswebsite). However, it is no longer supported in favour of animBot, which, unfortunately, isn't free.

In this little repo I've made a couple of fixes to convert the existing Python scripts to Python3. I also got rid of the motion trail, since newer versions of Maya have it out-of-the-box.

The installation is the same, you just download the [aTools_install.mel](https://raw.githubusercontent.com/MKlimenko/aTools_python3/master/aTools_install.mel) file and drag-and-drop it to the Viewport. It'll attempt to download the archive and unpack it silently, however, if it'd fail, please proceed with the manual download from the [Releases](https://github.com/MKlimenko/aTools_python3/releases) page.

I haven't tested it thoroughly, so some errors and bugs may occur, feel free to contact me.