USE_PKGBUILD=1
include /usr/local/share/luggage/luggage.make

TITLE=auto_logout
REVERSE_DOMAIN=org.da
PAYLOAD=\
		pack-Library-LaunchAgents-org.da.auto_logout.plist\
		pack-usr-local-bin-auto_logout.py\
		pack-script-postinstall

PACKAGE_VERSION=1.5