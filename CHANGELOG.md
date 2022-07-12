# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

2022-07-11 Three's a Charm
### Changed
- first effort at python3 compatibility
- also mima's first attempt at a github fork

## [1.6.4] - 2016-03-23 Kick That FileVault
### ADDED
- Tests for FileVault status, and when restarting, uses the fdesetup authrestart command to bypass the FileVault unlock screen.

## [1.5.4] - 2015-04-30 Nobody Tosses a Dwarf
### CHANGED
- Now activates the app over top of all other apps (```NSApplication.activateIgnoringOtherApps_()```)
- Reports idle time in whole seconds instead of 6-digit precision floats.
- Defaults to playing the "Submarine" sound when firing alert.
- Sound may be overridden with globals.

## [1.5.3] - 2015-04-30 Kim Chee Hot Pants
### CHANGED
- Now uses PyObjC instead of Applescript to present alert. This helps us avoid some issues with timeout.
- Added an icon, and a global constant for configuring a custom one.

### FIXED
- ```LO_TIMEOUT``` >= 120 seconds results in Applescript timing out (not the alert timing out) which results in auto_logout thinking user has cancelled.

## [1.5.2] - 2015-04-28 Dijon
### FIXED
- Reverts ```LO_TIMEOUT``` to 120 seconds instead of 10.
- Syntax error breaks script.

## [1.5.1] - 2015-04-23 Stylin'
### CHANGED
- Under-the-hood style and reorganization changes

## [1.5.0] - 2014-10-12
### FIXED
- User cancellation window does not cancel anything.
- Computers with a power schedule fail to execute script.
- Computers past shutdown time need an additional sudoers entry for shutdown privileges.

[unreleased]: https://github.com/sheagcraig/yo/compare/1.6.4...HEAD
[1.6.4]: https://github.com/sheagcraig/yo/compare/1.5.4...HEAD
[1.5.4]: https://github.com/sheagcraig/auto_logout/compare/1.5.3...1.5.4
[1.5.3]: https://github.com/sheagcraig/auto_logout/compare/1.5.2...1.5.3
[1.5.2]: https://github.com/sheagcraig/auto_logout/compare/1.5.1...1.5.2
[1.5.1]: https://github.com/sheagcraig/auto_logout/compare/1.5...1.5.1
