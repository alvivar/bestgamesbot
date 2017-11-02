""" Create an .exe with cx_Freeze, just call 'python setup.py build'. You need
to change the TCL, TK environment variables below to your own. """

import os

from cx_Freeze import Executable, setup

os.environ['TCL_LIBRARY'] = r'C:\Users\matnesis\Anaconda3\envs\junk\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\matnesis\Anaconda3\envs\junk\tcl\tk8.6'

OPTIONS = {'build_exe': {'includes': ['idna.idnadata']}}

EXECUTABLES = [Executable('tumblrqueuer.py', targetName='bestgamesbot.exe')]

setup(
    name='bestgamesbot',
    version='0.1',
    description="Itch.io & Tumblr Bot",
    executables=EXECUTABLES,
    options=OPTIONS)
