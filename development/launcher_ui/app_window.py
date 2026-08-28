"""
Main Window Controller for SIR Launcher
"""
import sys
import os

from launcher_source.SIR_Launcher_Studio import SIRLauncherApp

def run_launcher():
    app = SIRLauncherApp()
    app.mainloop()

if __name__ == "__main__":
    run_launcher()
