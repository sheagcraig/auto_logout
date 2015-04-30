## auto_logout
Package to automatically hard-logout users in OS X computer labs.

Computers can be set using the builtin tools to automatically logout users
after a predetermined amount of time. However, it will wait, and ultimately
fail, if a user has unsaved changes in an Office document, running processes in a terminal session, etc.

I tried numerous ways of doing this--the first idea was to ```killall -9
loginwindow```, but, that frequently left users with a glitched out loginwindow
(Go figure...)

So I eventually decided to just reboot the computer. Of course, this requires
a change to the sudoers file, which is why there is a postinstall script. Please take note! As configured, this will allow *any* user to reboot or shutdown the computer using the commandline ```reboot``` and ```shutdown``` commands.

If the computer has a power schedule, and the machine is past the scheduled shutdown time, it will just shut down instead of reboot.

### Installation
Grab the latest package from the releases section and install on clients to use the default timing and icon.

If you would like to build yourself to incorporate custom settings, a Makefile is provided for use with [the Luggage](https://github.com/unixorn/luggage). Of course, feel free to use your choice of package building software.

### Customization
There are a few variables that you can adjust to suit your environment.

In ```/usr/local/bin/auto_logout.py```:
* ```MAXIDLE```: The number of seconds after which a system is considered to be idle. (Default is 1800 seconds, i.e. 30 minutes).
* ```LO_TIMEOUT```: The number of seconds a user has to cancel the auto logout after the alert runs. (Configured for 120 seconds).
* ```ICON_PATH```: A valid path to an icon file (a .png) to use in the alert window. (Defaults to a nasty dark cloud icon).

In ```/Library/LaunchAgents/org.da.autoLogout.plist```
* ```StartInterval``` The interval, in seconds, after which the LaunchAgent runs. (Defaults to run every 5 minutes).
