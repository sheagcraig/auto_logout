USE_PKGBUILD=1
include /usr/local/share/luggage/luggage.make

TITLE=auto_logout
REVERSE_DOMAIN=org.da
PAYLOAD=\
		pack-Library-LaunchAgents-org.da.auto_logout.plist\
		pack-usr-local-bin-auto_logout.py\
		pack-usr-local-share-EvilCloud.png\
		pack-script-postinstall

PACKAGE_VERSION=$(shell python -c "import auto_logout; print auto_logout.__version__")

pack-usr-local-share-%: % l_usr_local_share
	@sudo ${INSTALL} -m 755 -g wheel -o root "${<}" ${WORK_D}/usr/local/share
