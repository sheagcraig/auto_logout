#!/usr/bin/python

"""Check for whether idle time has exceeded some set amount of time,
prompt user for a chance to prevent logout, and then forcibly logout
without allowing user to save work.

"""
import sys
import re
import shlex
import subprocess
import datetime

# Number of seconds to wait before initiating a logout
MAXIDLE = 1800
# Number of seconds user has to cancel logout
LO_TIMEOUT = 60


def run_applescript(script):
    """Run an applescript"""
    process = subprocess.Popen(['osascript', '-'], stdout=subprocess.PIPE, 
                               stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = process.communicate(script)

    if err:
        raise Exception(err)
    return process.returncode


def logout():
    """Forcibly log current user out of the gui"""
    #pid = get_loginwindow_pid()
    args = shlex.split('sudo -u root /usr/bin/killall -9 loginwindow')
    process = subprocess.Popen(args, shell=False)
    process.communicate()


def restart():
    """Prompt, but then failing that, forcibly restart the computer"""
    #args = shlex.split('shutdown -r now')
    args = shlex.split('sudo -u root reboot -q')
    process = subprocess.Popen(args, shell=False)
    process.communicate()


def shutdown():
    """Shutdown the computer immediately"""
    args = shlex.split('shutdown -h now')
    process = subprocess.Popen(args, shell=False)
    result = process.communicate()


def get_shutdown_time():
    """Return a datetime.time object representing the time system is supposed
    to shut itself down

    """
    # Get the schedule items from pmset
    args = shlex.split('pmset -g sched')
    process = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)
    result = process.communicate()

    # Get the shutdown time
    pattern = re.compile(r'(shutdown at )(\d{1,2}:\d{2}[AP]M)')
    final = pattern.search(result[0])

    # Create a datetime object from the unhelpful apple format
    today = datetime.date.today().strftime('%Y%m%d')
    shutdown_time = datetime.datetime.strptime(today + final.group(2), '%Y%m%d%I:%M%p')

    return shutdown_time


def check_idle():
    """Check the IOREG for the idletime of the input devices"""
    args = shlex.split('ioreg -c IOHIDSystem')
    process = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)
    result = process.communicate()

    # Strip out the first result (there are lots and lots of results, close
    # enough!
    pattern = re.compile(r'("HIDIdleTime" = )([0-9]*)')
    final = pattern.search(result[0])
    # Get our result from the match object;
    # Idle time is in really absurd units, convert to seconds
    idle_time = float(final.group(2)) / 1000000000
    print(idle_time, MAXIDLE)

    # Determine if we are idling
    if idle_time > MAXIDLE:
        script = """
            tell application "System Events"
                display dialog "Logging out idle user:\nClick Cancel to prevent automatic logout." buttons "Cancel" giving up after %i with icon 0
            end tell""" % LO_TIMEOUT

        try:
            result = run_applescript(script)
        except:
            # If user cancels, just ignore the exception
            pass

        if result == 1:
            sys.exit()
        else:
            # If it's past shutdown time, go straight to shutting down
            shutdown_time = get_shutdown_time()
            if datetime.datetime.now() > shutdown_time:
                shutdown()
            else:
                restart()


def get_loginwindow_pid():
    """Get the pid for the user's loginwindow
    Currently unused since we need to use killall to pull this off

    """
    args = shlex.split('ps -Axjc')
    process = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)
    result = process.communicate()

    pattern = re.compile(r'.*loginwindow')
    for line in result:
        match = pattern.search(result[0])
        if match:
            pid = match.group(0).split()[1]

    return pid


def main():
    """Main program"""
    check_idle()


if __name__ == '__main__':
    main()
