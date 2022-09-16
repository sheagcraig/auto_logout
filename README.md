## auto_logout
Package to automatically hard-logout users in OS X computer labs.

Computers can be set using the builtin tools to automatically logout users
after a predetermined amount of time. However, it will wait, and ultimately
fail, if a user has unsaved changes in an Office document, running processes in a terminal session, etc.

I tried numerous ways of doing this--the first idea was to `killall -9 loginwindow`, but, that frequently left users with a glitched out loginwindow
(Go figure...)

So I eventually decided to just reboot the computer. Of course, this requires
a change to the sudoers file, which is why there is a postinstall script. Please take note! As configured, this will allow *any* user to reboot or shutdown the computer using the commandline `reboot` and `shutdown` commands.

If the computer has a power schedule, and the machine is past the scheduled shutdown time, it will just shut down instead of reboot.

If the boot drive is FileVaulted, `auto_logout` will restart using `fdesetup authrestart` instead of a regular reboot. This bypasses the FileVault unlock screen.

### Installation
Grab the latest package from the releases section and install on clients to use the default timing and icon.

If you would like to build yourself to incorporate custom settings, a Makefile is provided for use with [the Luggage](https://github.com/unixorn/luggage). Of course, feel free to use your choice of package building software.

### Customization
There are a few variables that you can adjust to suit your environment.

In `/usr/local/bin/auto_logout.py`:
* `MAXIDLE`: The number of seconds after which a system is considered to be idle. (Default is 1800 seconds, i.e. 30 minutes).
* `LO_TIMEOUT`: The number of seconds a user has to cancel the auto logout after the alert runs. (Configured for 120 seconds).
* `ICON_PATH`: A valid path to an icon file (a .png) to use in the alert window. (Defaults to a nasty dark cloud icon).
* `ALERT_SOUND`: Name of a sound to play when firing alert. See [Sounds](#sounds) section. (Defaults to "Submarine").

In `/Library/LaunchAgents/org.da.autoLogout.plist`
* `StartInterval` The interval, in seconds, after which the LaunchAgent runs. (Defaults to run every 5 minutes).

### Sounds
If you want to use a different sound, you must provide the *name* of the sound, not the filename, and not the path. I.e "Sosumi", not "Sosumi.aiff" or "/System/Library/Sosumi.aiff".

If you don't want a sound, set `ALERT_SOUND` to `""` or `None`.

The search path is:
- ~/Library/Sounds
- /Library/Sounds
- /Network/Library/Sounds
- /System/Library/Sounds (This is where all of the builtin sounds live)

If you want to include a custom sound, it needs to be available in one of those paths. So for example, if you wanted to use the sound file "TotalEclipseOfTheHeart.aiff", copy it to `/Library/Sounds` (which may not exist by default), and set the `ALERT_SOUND` option like this: 
`ALERT_SOUND = "TotalEclipseOfTheHeart"`

Sounds must be a aiff; extension .aif is not valid.
