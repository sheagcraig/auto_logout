#!/usr/bin/env python3
# Copyright (C) 2014 Shea G Craig
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
auto_logout.py

Check for whether system idle time has exceeded some set amount of time,
as specified in seconds with global MAXIDLE.

If system is idle, prompt user for a chance to prevent logout.

If no user intervention prevents logout, either restart the computer or
shut down, depending on whether the time is past the scheduled shutdown
time.

Code for killing the loginwindow is included for reference purposes,
although this method of force-logging out is not recommended due to
graphics glitches.

Restarting the computer is the most stable way to forcibly logout a user
who may have applications preventing logout via the normal means.
"""


import datetime
import getpass
import re
import subprocess
import sys
import syslog

# pylint: disable=no-name-in-module
from AppKit import (NSImage, NSAlert, NSTimer, NSRunLoop, NSApplication,
                    NSSound, NSModalPanelRunLoopMode, NSApp,
                    NSRunAbortedResponse)
# pylint: enable=no-name-in-module


__version__ = "2.0.0"
# Number of seconds to wait before initiating a logout.
MAXIDLE = 1800
# Number of seconds user has to cancel logout.
LO_TIMEOUT = 120
# Icon displayed as the app icon for the alert dialog.
ICON_PATH = "/usr/local/share/EvilCloud.png"
# Sound played when alert is presented. See README.
ALERT_SOUND = "Submarine"

# Cocoa objects must use class func alloc().init(), so pylint doesn't
# see our init().
# pylint: disable=no-init

# Methods are named according to PyObjC/Cocoa style.
# pylint: disable=invalid-name
class Alert(NSAlert):
    """Subclasses NSAlert to include a timeout."""

    def init(self):  # pylint: disable=super-on-old-class
        """Add an instance variable for our timer."""
        self = super(Alert, self).init()
        self.timer = None
        self.alert_sound = None
        return self

    def setIconWithContentsOfFile_(self, path):
        """Convenience method for adding an icon.

        Args:
            path: String path to a valid NSImage filetype (png)
        """
        icon = NSImage.alloc().initWithContentsOfFile_(path)
        self.setIcon_(icon)  # pylint: disable=no-member

    def setAlertSound_(self, name):
        """Set the sound to play when alert is presented.

        Args:
            name: String name of a system sound. See the README.
        """
        self.alert_sound = name

    def setTimeToGiveUp_(self, time):
        """Configure alert to give up after time seconds."""
        # Cocoa objects must use class func alloc().init(), so pylint
        # doesn't see our init().
        # pylint: disable=attribute-defined-outside-init
        self.timer = \
            NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
                time, self, "_killWindow", None, False)
        # pylint: enable=attribute-defined-outside-init

    def present(self):
        """Present the Alert, giving up after configured time..

        Returns: Int result code, based on PyObjC enums. See NSAlert
            Class reference, but result should be one of:
                User clicked the cancel button:
                    NSAlertFirstButtonReturn = 1000
                Alert timed out:
                    NSRunAbortedResponse = -1001
        """
        if self.timer:
            NSRunLoop.currentRunLoop().addTimer_forMode_(
                self.timer, NSModalPanelRunLoopMode)
        # Start a Cocoa application by getting the shared app object.
        # Make the python app the active app so alert is noticed.
        app = NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)
        if self.alert_sound:
            sound = NSSound.soundNamed_(self.alert_sound).play()
        result = self.runModal()  # pylint: disable=no-member
        print(result)
        return result

    # pylint: disable=no-self-use
    def _killWindow(self):
        """Abort the modal window as managed by NSApp."""
        NSApp.abortModal()
    # pylint: enable=no-self-use

# pylint: enable=no-init
# pylint: enable=invalid-name


def logout():
    """Forcibly log current user out of the gui.

    This function is currently unused. killall loginwindow often results
    in corrupted loginwindow graphics. The function remains more as
    documentation of how to do these things.
    """
    result = subprocess.check_output(["sudo", "-u", "root", "/usr/bin/killall",
                                      "-9", "loginwindow"], text=True)
    syslog.syslog(syslog.LOG_ALERT, result)


def restart():
    """Forcibly restart the computer."""
    result = subprocess.check_output(
        ["sudo", "-u", "root", "/sbin/reboot", "-q"], text=True)
    syslog.syslog(syslog.LOG_ALERT, result)


def fvrestart():
    """Forcibly restart a FV2 enabled computer."""
    result = subprocess.check_output(
        ["sudo", "-u", "root", "/usr/bin/fdesetup", "authrestart"], text=True)
    syslog.syslog(syslog.LOG_ALERT, result)


def shutdown():
    """Shutdown the computer immediately."""
    result = subprocess.check_output(["sudo", "-u", "root", "/sbin/shutdown", "-h", "now"],
                                     text=True)
    syslog.syslog(syslog.LOG_ALERT, result)


def fv_active():
    """Get FileVault status."""
    result = subprocess.check_output(["/usr/bin/fdesetup", "status"], text=True)
    return result == "FileVault is On.\n"


def get_shutdown_time():
    """Return a system's shutdown time.

    Returns:
        A datetime.time object representing the time system is supposed
        to shut itself down, or None if no schedule has been set.
    """
    # Get the schedule items from pmset
    result = subprocess.check_output(["pmset", "-g", "sched"], text=True)

    # Get the shutdown time
    pattern = re.compile(r"(shutdown at )(\d{1,2}:\d{2}[AP]M)")
    final = pattern.search(result)

    if final:
        # Create a datetime object from the unhelpful apple format
        today = datetime.date.today().strftime("%Y%m%d")
        shutdown_time = datetime.datetime.strptime(
            today + final.group(2), "%Y%m%d%I:%M%p")
    else:
        shutdown_time = None

    return shutdown_time


def get_idle():
    """Check the IOREG for the idle time of the input devices.

    Returns:
        Float number of seconds computer has been idle.
    """
    result = subprocess.check_output(["ioreg", "-c", "IOHIDSystem"], text=True)

    # Strip out the first result (there are lots and lots of results;
    # close enough!
    pattern = re.compile(r'("HIDIdleTime" = )([0-9]*)')
    final = pattern.search(result)
    # Idle time is in really absurd units; convert to seconds.
    idle_time = float(final.group(2)) / 1000000000
    syslog.syslog(syslog.LOG_ALERT, "System Idle: %i seconds out of %i "
                  "allowed." % (idle_time, MAXIDLE))

    return idle_time


def get_loginwindow_pid():
    """Get the pid for the user's loginwindow.

    Currently unused since we need to use killall to pull this off.

    Returns: An int process ID for the loginwindow.
    """
    pid = None
    result = subprocess.check_output(["ps", "-Axjc"], text=True)
    pattern = re.compile(r".*loginwindow")
    for line in result.splitlines():
        match = pattern.search(line)
        if match:
            pid = match.group(0).split()[1]

    return int(pid)


def build_alert():
    """Build an alert for auto-logout notifications."""
    alert = Alert.alloc().init()  # pylint: disable=no-member
    alert.setMessageText_("Logging out idle user in %i seconds!" % LO_TIMEOUT)
    alert.setInformativeText_("Click Cancel to prevent automatic logout.")
    alert.addButtonWithTitle_("Cancel")
    alert.setIconWithContentsOfFile_(ICON_PATH)
    alert.setAlertSound_(ALERT_SOUND)
    alert.setTimeToGiveUp_(LO_TIMEOUT)
    return alert


def main():
    """Main program"""
    idle_time = get_idle()
    if idle_time > MAXIDLE:
        syslog.syslog(syslog.LOG_ALERT, "System is idle.")
        syslog.syslog(syslog.LOG_ALERT, "Idle user: %s" % getpass.getuser())
        alert = build_alert()
        if alert.present() != NSRunAbortedResponse:
            # User cancelled
            syslog.syslog(syslog.LOG_ALERT, "User cancelled auto logout.")
            sys.exit()
        else:
            # If it's past shutdown time, go straight to shutting down.
            # If there is no schedule, or it's before scheduled
            # shutdown, restart.
            shutdown_time = get_shutdown_time()
            syslog.syslog(syslog.LOG_ALERT,
                          "Scheduled system shutdown time: %s" % shutdown_time)
            if shutdown_time and datetime.datetime.now() > shutdown_time:
                syslog.syslog(syslog.LOG_ALERT, "Shutdown time is nigh. "
                              "Shutting down.")
                shutdown()
            else:
                syslog.syslog(syslog.LOG_ALERT, "Restarting")
                if fv_active():
                    syslog.syslog(syslog.LOG_ALERT, "Authenticated Restart.")
                    fvrestart()
                else:
                    restart()
    else:
        syslog.syslog(syslog.LOG_ALERT, "System is not idle.")


if __name__ == "__main__":
    main()
