#!/usr/bin/python
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
autoLogout.py

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
import re
import subprocess
import sys
import syslog


# Number of seconds to wait before initiating a logout
MAXIDLE = 1800
# Number of seconds user has to cancel logout
LO_TIMEOUT = 10


def run_applescript(script):
    """Run an applescript.

    Args:
        script: A string of the entire applescript. Must include proper
            formatting.

    Returns:
        The returncode of the osascript command.

        However, the result and err variables contain more information on
        what the user did, so if you are doing more serious applescript
        result parsing, use them,
    """
    process = subprocess.Popen(['osascript', '-'], stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = process.communicate(script)
    syslog.syslog(syslog.LOG_ALERT, "Applescript result: %s Error: %s" %
                  (result, err))

    return process.returncode


def logout():
    """Forcibly log current user out of the gui.

    This function is currently unused. killall loginwindow often results
    in corrupted loginwindow graphics. The function remains more as
    documentation of how to do these things.
    """
    result = subprocess.check_output(["sudo", "-u", "root", "/usr/bin/killall",
                                      "-9", "loginwindow"], shell=False)
    syslog.syslog(syslog.LOG_ALERT, result)


def restart():
    """Forcibly restart the computer."""
    result = subprocess.check_output(["sudo", "-u", "root", "reboot", "-q"],
                                     shell=False)
    syslog.syslog(syslog.LOG_ALERT, result)


def shutdown():
    """Shutdown the computer immediately."""
    result = subprocess.check_output(["shutdown", "-h", "now"], shell=False)
    syslog.syslog(syslog.LOG_ALERT, result)


def get_shutdown_time():
    """Return a system's shutdown time.

    Returns:
        A datetime.time object representing the time system is supposed
        to shut itself down, or None if no schedule has been set.
    """
    # Get the schedule items from pmset
    result = subprocess.check_output(["pmset", "-g", "sched"])

    # Get the shutdown time
    pattern = re.compile(r'(shutdown at )(\d{1,2}:\d{2}[AP]M)')
    final = pattern.search(result)

    if final:
        # Create a datetime object from the unhelpful apple format
        today = datetime.date.today().strftime('%Y%m%d')
        shutdown_time = datetime.datetime.strptime(
            today + final.group(2), '%Y%m%d%I:%M%p')
    else:
        shutdown_time = None

    return shutdown_time


def check_idle():
    """Check the IOREG for the idletime of the input devices."""
    syslog.syslog(syslog.LOG_ALERT, "Checking idle time.")
    result = subprocess.check_output(["ioreg", "-c", "IOHIDSystem"])

    # Strip out the first result (there are lots and lots of results,
    # close enough!
    pattern = re.compile(r'("HIDIdleTime" = )([0-9]*)')
    final = pattern.search(result)
    # Get our result from the match object;
    # Idle time is in really absurd units, convert to seconds
    idle_time = float(final.group(2)) / 1000000000
    syslog.syslog(syslog.LOG_ALERT, "System Idle: %f seconds out of %i "
                  "allowed." % (idle_time, MAXIDLE))

    # Determine if we are idling
    if idle_time > MAXIDLE:
        syslog.syslog(syslog.LOG_ALERT, "System is idle.")
        script = """
            tell application "System Events"
                display dialog "Logging out idle user:\nClick Cancel to prevent automatic logout." buttons "Cancel" giving up after %i with icon 0
            end tell""" % LO_TIMEOUT

        applescript_result = run_applescript(script)

        if applescript_result != 0:
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
                restart()
    else:
        syslog.syslog(syslog.LOG_ALERT, "System is not idle.")


def get_loginwindow_pid():
    """Get the pid for the user's loginwindow.

    Currently unused since we need to use killall to pull this off.

    Returns: An int process ID for the loginwindow.
    """
    pid = None
    result = subprocess.check_output(["ps", "-Axjc"])
    pattern = re.compile(r'.*loginwindow')
    for line in result.splitlines():
        match = pattern.search(line)
        if match:
            pid = match.group(0).split()[1]

    return int(pid)


def main():
    """Main program"""
    check_idle()


if __name__ == '__main__':
    main()
