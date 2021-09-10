#=================================================
# Update PATH variable for OpenLDAP
#
# Provided by LTB-project (http://www.ltb-project.org)
#=================================================

OL_BIN="/usr/bin"
OL_SBIN="/usr/sbin"

PATH="$PATH:$OL_BIN"

if [ `id -u` -eq 0 ]
then
	PATH="$PATH:$OL_SBIN"
fi

export PATH
