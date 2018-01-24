"""
    Run 'python cxfreezesetup.py build' to create a executable with cx_Freeze.
    You need to change the TCL, TK environment variables below to your own.
"""

import os

from cx_Freeze import Executable, setup

os.environ['TCL_LIBRARY'] = r'C:\Users\matnesis\Anaconda3\envs\junk\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\matnesis\Anaconda3\envs\junk\tcl\tk8.6'

OPTIONS = {'build_exe': {'includes': ['idna.idnadata', 'multiprocessing']}}

EXECUTABLES = [Executable('tumblrqueuer.py', targetName='bestgamesbot.exe')]

setup(
    name='bestgamesbot',
    version='0.1',
    description=
    "Bot that collects popular games from Itch.io and publish them in Twitter and Tumblr!",
    executables=EXECUTABLES,
    options=OPTIONS)
