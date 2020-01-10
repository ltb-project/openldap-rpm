#=================================================
# Specification file for OpenLDAP
#
# Install OpenLDAP
# Install an init script in /etc/init.d
# Create user/group ldap
# Configure syslog and logrotate
# Install a pwdChecker module
#
# Copyright (C) 2008-2019 Clement OUDOT
# Copyright (C) 2018-2019 Worteks
# Copyright (C) 2015 David COUTADEUR
# Copyright (C) 2008 Raphael OUAZANA
# Copyright (C) 2015 LINAGORA
# Copyright (C) 2015 Savoir-faire Linux
#
# Provided by LTB-project (http://www.ltb-project.org)
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        openldap
%define real_version     2.4.48
%define release_version  2%{?dist}

# Fix for CentOS7
%if 0%{?rhel} == 7
 %define dist .el7
%endif

# Fix for CentOS8
%if 0%{?rhel} == 8
 %define dist .el8
%endif

%define bdbdir           /usr/local/berkeleydb
%define ldapdir          /usr/local/openldap
%define ldapserverdir    %{ldapdir}
%define ldapdatadir      %{ldapdir}/var/openldap-data
%define ldaplogsdir      %{bdbdir}/openldap-logs
%define ldapbackupdir    /var/backups/openldap
%define ldaplogfile      /var/log/openldap.log

%define ldapuser         ldap
%define ldapgroup        ldap

%define slapd_init_name             ltb-project-openldap-initscript
%define slapd_init_version          2.5

%define check_password_name         ltb-project-openldap-ppolicy-check-password
%define check_password_version      1.1
%define check_password_conf         %{ldapserverdir}/etc/openldap/check_password.conf
%define check_password_minPoints    3
%define check_password_useCracklib  0
%define check_password_minUpper     0
%define check_password_minLower     0
%define check_password_minDigit     0
%define check_password_minPunct     0

%define ppm_name         ppm
%define ppm_version      1.8
%define ppm_conf         %{ldapserverdir}/etc/openldap/ppm.conf

%define explockout_name		explockout
%define explockout_version	1.0

#=================================================
# Header
#=================================================
Summary: OpenLDAP server with addons from the LDAP Tool Box project
Name: %{real_name}-ltb
Version: %{real_version}
Release: %{release_version}
# http://www.openldap.org/software/release/license.html
License: OpenLDAP Public License

Group: Applications/System
URL: http://www.openldap.org/

# Source available on http://www.openldap.org
Source: %{real_name}-%{real_version}.tgz
# Sources available on https://github.com/ltb-project/openldap-initscript
Source1: %{slapd_init_name}-%{slapd_init_version}.tar.gz
# Sources available on https://github.com/ltb-project/openldap-ppolicy-check-password
Source2: %{check_password_name}-%{check_password_version}.tar.gz
Source3: openldap.sh
Source4: DB_CONFIG
Source5: openldap.logrotate
# Sources available on https://github.com/ltb-project/ppm
Source6: %{ppm_name}-%{ppm_version}.tar.gz
# Sources available on https://github.com/davidcoutadeur/explockout
Source7: %{explockout_name}-%{explockout_version}.tar.gz
# This patch changes the default ldapi:/// path to /var/run/slapd/ldapi
Patch0: change_default_ldapi_path.diff
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: gcc, make
BuildRequires: openssl-devel, cyrus-sasl-devel, berkeleydb-ltb >= 4.6.21, libtool-ltdl-devel
BuildRequires: cracklib

%if "%{?dist}" != ".el8"
BuildRequires: groff, tcp_wrappers-devel
%endif

%if "%{?dist}" == ".el7" || "%{?dist}" == ".el8"
%{?systemd_requires}
BuildRequires: systemd
%endif

Requires: gawk, libtool-ltdl, berkeleydb-ltb >= 4.6.21

Requires(pre): /sbin/ldconfig, coreutils, shadow-utils

%description
OpenLDAP is an open source suite of LDAP (Lightweight Directory Access
Protocol) applications and development tools. LDAP is a set of
protocols for accessing directory services (usually phone book style
information, but other information is possible) over the Internet,
similar to the way DNS (Domain Name System) information is propagated
over the Internet.

This package contains all: server, clients, librairies and docs. It
can be installed with openldap and openldap-devel. It provides tools
from the LDAP Tool Box project:
o Start/stop script
o Logrotate script

#=================================================
# Subpackage check-password
#=================================================
%package check-password
Summary:        check_password module for password policy
Version:        %{check_password_version}
Release:        9%{?dist}
Group:          Applications/System
URL:		http://www.ltb-project.org

%if "%{?dist}" == ".el6" || "%{?dist}" == ".el7"
BuildRequires:	cracklib-devel
%endif

Requires:	cracklib, cracklib-dicts, %{real_name}-ltb >= %{real_version}

%description check-password
check_password.c is an OpenLDAP pwdPolicyChecker module used to check the strength
and quality of user-provided passwords. This module is used as an extension of the
OpenLDAP password policy controls, see slapo-ppolicy(5) section pwdCheckModule.
check_password.c will run a number of checks on the passwords to ensure minimum
strength and quality requirements are met. Passwords that do not meet these
requirements are rejected.

This is provided by LDAP Tool Box project: http://www.ltb-project.org

#=================================================
# Subpackage ppm
#=================================================
%package ppm
Summary:        OpenLDAP password policy module
Version:        %{ppm_version}
Release:        1%{?dist}
Group:          Applications/System
URL:            https://github.com/ltb-project/ppm

Requires:       %{real_name}-ltb >= %{real_version}

%description ppm
ppm.c is an OpenLDAP module for checking password quality when they are modified.
Passwords are checked against the presence or absence of certain character classes.
This module is used as an extension of the OpenLDAP password policy controls,
see slapo-ppolicy(5) section pwdCheckModule.

#=================================================
# Subpackage contrib-overlays
#=================================================
%package contrib-overlays
Summary:        Overlays contributed to OpenLDAP
Version:        %{real_version}
Release:        %{release_version}
Group:          Applications/System
URL:		http://www.ltb-project.org

Requires:	%{real_name}-ltb >= %{real_version}

%description contrib-overlays
Some overlays are not included in the OpenLDAP main package but provided
as contributions. This package provide some of them.

This is provided by LDAP Tool Box project: http://www.ltb-project.org

#=================================================
# Subpackage mdb-utils
#=================================================
%package mdb-utils
Summary:        MDB utilities
Version:        %{real_version}
Release:        %{release_version}
Group:          Applications/System
URL:		http://www.ltb-project.org

Requires:	%{real_name}-ltb >= %{real_version}

%description mdb-utils
MDB utilities contain both mdb_stat and mdb_copy, and the associated
documentation.

This is provided by LDAP Tool Box project: http://www.ltb-project.org

#=================================================
# Subpackage explockout
#=================================================
%package explockout
Summary:        OpenLDAP overlay explockout
Version:        %{explockout_version}
Release:        2%{?dist}
Group:          Applications/System
URL:            https://github.com/davidcoutadeur/explockout

Requires:       %{real_name}-ltb >= %{real_version}

%description explockout
explockout is an OpenLDAP module that denies authentication to users who
have previously failed to authenticate, requiring them to wait for an
exponential time

#=================================================
# Source preparation
#=================================================
%prep
%setup -n %{real_name}-%{real_version}
%setup -n %{real_name}-%{real_version} -T -D -a 1
%setup -n %{real_name}-%{real_version} -T -D -a 2
%setup -n %{real_name}-%{real_version} -T -D -a 6
%setup -n %{real_name}-%{real_version} -T -D -a 7

# Apply patches
%patch0 -p1

#=================================================
# Building
#=================================================
%build
# OpenLDAP
export CC="gcc"
export CFLAGS="-DOPENLDAP_FD_SETSIZE=4096 -O2 -g -DSLAP_SCHEMA_EXPOSE"
# Uncomment to enable config delete option
#export CFLAGS="-DOPENLDAP_FD_SETSIZE=4096 -O2 -g -DSLAP_SCHEMA_EXPOSE -DSLAP_CONFIG_DELETE"
export CPPFLAGS="-I%{bdbdir}/include -I/usr/kerberos/include"
export LDFLAGS="-L%{bdbdir}/%{_lib}"
%if "%{?dist}" == ".el8"
./configure --disable-dependency-tracking --enable-ldap --enable-debug --prefix=%{ldapserverdir} --libdir=%{ldapserverdir}/%{_lib} --with-tls --with-cyrus-sasl --enable-spasswd --enable-overlays --enable-modules --enable-dynamic=no --enable-slapi --enable-meta --enable-crypt --enable-sock --enable-rlookups
%else
./configure --disable-dependency-tracking --enable-ldap --enable-debug --prefix=%{ldapserverdir} --libdir=%{ldapserverdir}/%{_lib} --with-tls --with-cyrus-sasl --enable-spasswd --enable-overlays --enable-modules --enable-dynamic=no --enable-slapi --enable-meta --enable-crypt --enable-sock --enable-wrappers --enable-rlookups
%endif
make depend
make %{?_smp_mflags}
# check_password
cd %{check_password_name}-%{check_password_version}
%if "%{?dist}" == ".el8"
sed -i 's:^CRACKLIB_LIB:#CRACKLIB_LIB:' Makefile
make %{?_smp_mflags} "CONFIG=%{check_password_conf}" "LDAP_INC=-I../include -I../servers/slapd" 'OPT=-g -O2 -Wall -fpic -DDEBUG -DCONFIG_FILE="\"$(CONFIG)\""'
%else
make %{?_smp_mflags} "CONFIG=%{check_password_conf}" "LDAP_INC=-I../include -I../servers/slapd"
%endif
cd ..
# ppm
cd %{ppm_name}-%{ppm_version}
make clean
%if "%{?dist}" == ".el8"
make "CONFIG=%{ppm_conf}" "OLDAP_SOURCES=.." "CRACK_INC=" "CRACK_LIB="
%else
make "CONFIG=%{ppm_conf}" "OLDAP_SOURCES=.."
%endif
cd ..
# contrib-overlays
cd contrib/slapd-modules
## lastbind
cd lastbind
make clean
make %{?_smp_mflags} "prefix=%{ldapserverdir}" "LDAP_LIB="
cd ..
## smbk5pwd
cd smbk5pwd
make clean
make %{?_smp_mflags} "DEFS=-DDO_SAMBA -DDO_SHADOW" "LDAP_LIB=-L../../../libraries/liblber/.libs/ -L../../../libraries/libldap_r/.libs/ -lldap_r -llber" "prefix=%{ldapserverdir}"
cd ..
## nssov
cd nssov
make clean
make %{?_smp_mflags} "prefix=%{ldapserverdir}" "LDAP_LIB="
cd ..
## noopsrch
cd noopsrch
make clean
make %{?_smp_mflags} "prefix=%{ldapserverdir}" "LDAP_LIB="
cd ..
## autogroup
cd autogroup
make clean
make %{?_smp_mflags} "prefix=%{ldapserverdir}" "LDAP_LIB="
cd ..
## pbkdf2
cd passwd/pbkdf2
make clean
make %{?_smp_mflags} "prefix=%{ldapserverdir}" "LDAP_LIB="
cd ../..
## sha512
cd passwd/sha2
make clean
make %{?_smp_mflags} "prefix=%{ldapserverdir}" "LDAP_LIB="
cd ../..
cd ../..
# MDB utils
cd libraries/liblmdb
make %{?_smp_mflags}
cd ../..
# explockout
cd %{explockout_name}-%{explockout_version}
make clean
make %{?_smp_mflags} "OLDAP_SOURCES=.." "LIBDIR=%{ldapserverdir}/libexec/openldap"
cd ..

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} STRIP=""

# Directories
mkdir -p %{buildroot}%{ldapdatadir}
mkdir -p %{buildroot}%{ldaplogsdir}
mkdir -p %{buildroot}%{ldapbackupdir}

# Init script
%if "%{?dist}" == ".el7" || "%{?dist}" == ".el8"
mkdir -p %{buildroot}%{_unitdir}/
install -m 644 %{slapd_init_name}-%{slapd_init_version}/slapd.service %{buildroot}%{_unitdir}/
%else
mkdir -p %{buildroot}/etc/init.d
install -m 755 %{slapd_init_name}-%{slapd_init_version}/slapd.init %{buildroot}/etc/init.d/slapd
%endif
install -m 755 %{slapd_init_name}-%{slapd_init_version}/slapd-cli %{buildroot}%{ldapserverdir}/sbin/
install -m 644 %{slapd_init_name}-%{slapd_init_version}/slapd-cli.conf %{buildroot}%{ldapserverdir}/etc/openldap/
sed -i 's:^SLAPD_PATH.*:SLAPD_PATH="'%{ldapdir}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf
sed -i 's:^SLAPD_USER.*:SLAPD_USER="'%{ldapuser}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf
sed -i 's:^SLAPD_GROUP.*:SLAPD_GROUP="'%{ldapgroup}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf
sed -i 's:^BDB_PATH.*:BDB_PATH="'%{bdbdir}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf
sed -i 's:^BACKUP_PATH.*:BACKUP_PATH="'%{ldapbackupdir}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf

# PATH modification
mkdir -p %{buildroot}/etc/profile.d
install -m 755 %{SOURCE3} %{buildroot}/etc/profile.d/openldap.sh
sed -i 's:^OL_BIN.*:OL_BIN='%{ldapdir}/bin':' %{buildroot}/etc/profile.d/openldap.sh
sed -i 's:^OL_SBIN.*:OL_SBIN='%{ldapdir}/sbin':' %{buildroot}/etc/profile.d/openldap.sh
sed -i 's:^OL_MAN.*:OL_MAN='%{ldapdir}/share/man':' %{buildroot}/etc/profile.d/openldap.sh

# BDB configuration
install -m 644 %{SOURCE4} %{buildroot}%{ldapdatadir}
sed -i 's:^set_lg_dir.*:set_lg_dir\t'%{ldaplogsdir}':' %{buildroot}%{ldapdatadir}/DB_CONFIG

# Logrotate
mkdir -p %{buildroot}/etc/logrotate.d
install -m 644 %{SOURCE5} %{buildroot}/etc/logrotate.d/openldap

# Modify data directory in slapd.conf
sed -i 's:^directory.*:directory\t'%{ldapdatadir}':' %{buildroot}%{ldapserverdir}/etc/openldap/slapd.conf

# check_password
install -m 644 %{check_password_name}-%{check_password_version}/check_password.so %{buildroot}%{ldapserverdir}/%{_lib}
echo "minPoints %{check_password_minPoints}" > %{buildroot}%{check_password_conf}
echo "useCracklib %{check_password_useCracklib}" >> %{buildroot}%{check_password_conf}
echo "minUpper %{check_password_minUpper}" >> %{buildroot}%{check_password_conf}
echo "minLower %{check_password_minLower}" >> %{buildroot}%{check_password_conf}
echo "minDigit %{check_password_minDigit}" >> %{buildroot}%{check_password_conf}
echo "minPunct %{check_password_minPunct}" >> %{buildroot}%{check_password_conf}

# ppm
cd %{ppm_name}-%{ppm_version}
%if "%{?dist}" == ".el8"
make install "CONFIG=%{buildroot}%{ppm_conf}" LIBDIR="%{buildroot}%{ldapserverdir}/%{_lib}" "CRACK_INC=" "CRACK_LIB="
%else
make install "CONFIG=%{buildroot}%{ppm_conf}" LIBDIR="%{buildroot}%{ldapserverdir}/%{_lib}"
%endif
cd ..

# contrib-overlays
cd contrib/slapd-modules
cd lastbind
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
cd smbk5pwd
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
cd nssov
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
cd noopsrch
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
cd autogroup
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
cd passwd/pbkdf2
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ../..
cd passwd/sha2
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ../..
cd ../..

# MDB utils
cd libraries/liblmdb
install -m 755 "mdb_copy"  %{buildroot}%{ldapserverdir}/sbin
install -m 755 "mdb_stat"  %{buildroot}%{ldapserverdir}/sbin
install -m 644 "mdb_copy.1"  %{buildroot}%{ldapserverdir}/share/man/man1
install -m 644 "mdb_stat.1"  %{buildroot}%{ldapserverdir}/share/man/man1
cd ../..

# explockout
cd %{explockout_name}-%{explockout_version}
mkdir -p "%{buildroot}%{ldapserverdir}/libexec/openldap"
mkdir -p "%{buildroot}%{ldapserverdir}/share/man/man5"
make install "OLDAP_SOURCES=.." "LIBDIR=%{buildroot}%{ldapserverdir}/libexec/openldap"
install -m 644 "slapo-explockout.5" "%{buildroot}%{ldapserverdir}/share/man/man5"
cd ..

%pretrans -n openldap-ltb
#=================================================
# Pre Transaction
#=================================================

slapd_running=`/sbin/service slapd status | grep "is running" | wc -l`
if [ $slapd_running -eq 1 ]
then
	touch %{_localstatedir}/openldap-ltb-slapd-running
fi

if [ -e /etc/default/slapd ]
then
	cp /etc/default/slapd %{_localstatedir}/slapd.default
fi

%pre -n openldap-ltb
#=================================================
# Pre Installation
#=================================================

# If upgrade stop slapd
if [ $1 -eq 2 ]
then
%if "%{?dist}" == ".el7" || "%{?dist}" == ".el8"
	/bin/systemctl stop slapd.service
%else
	/sbin/service slapd stop > /dev/null 2>&1
%endif
fi

%post -n openldap-ltb
#=================================================
# Post Installation
#=================================================

%if "%{?dist}" == ".el7" || "%{?dist}" == ".el8"
%systemd_post slapd.service
/bin/systemctl --system daemon-reload
%endif

# Do this at first install
if [ $1 -eq 1 ]
then
	if [ -e /etc/init.d/slapd ]
	then
	# Set slapd as service
	/sbin/chkconfig --add slapd
	fi

	# Add syslog facility
%if "%{?dist}" == ".el5"
	echo "local4.*	-%{ldaplogfile}" >> /etc/syslog.conf
	/sbin/service syslog restart > /dev/null 2>&1
%else
	echo "local4.*	-%{ldaplogfile}" >> /etc/rsyslog.conf
	/sbin/service rsyslog restart > /dev/null 2>&1
%endif

fi

# Always do this
# Create user and group if needed
getent group %{ldapgroup} >/dev/null || groupadd -r -g 55 %{ldapgroup}
getent passwd %{ldapuser} >/dev/null || useradd -r -g %{ldapgroup} -u 55 -d %{ldapdir} -s /sbin/nologin -c "LDAP User" %{ldapuser}
# Globally set owner to root:root
/bin/chown root:root %{ldapserverdir}
/bin/chown -R root:root %{ldapserverdir}/bin
/bin/chown -R root:root %{ldapserverdir}/etc/openldap/{DB_CONFIG.example,ldap.conf,ldap.conf.default,schema,slapd.conf.default,slapd.ldif,slapd.ldif.default}
/bin/chown -R root:root %{ldapserverdir}/include
/bin/chown -R root:root %{ldapserverdir}/lib*
/bin/chown -R root:root %{ldapserverdir}/libexec
/bin/chown -R root:root %{ldapserverdir}/sbin
/bin/chown -R root:root %{ldapserverdir}/var
# Specifically adapt some files/directories owner and permissions
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapdatadir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldaplogsdir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapbackupdir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapserverdir}/var/run
/bin/chown -R root:%{ldapgroup} %{ldapserverdir}/etc/openldap/slapd.conf
/bin/chmod 640 %{ldapserverdir}/etc/openldap/slapd.conf

%post check-password
#=================================================
# Post Installation
#=================================================

# Change owner
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapserverdir}/%{_lib}
/bin/chown -R root:%{ldapgroup} %{check_password_conf}
/bin/chmod 640 %{check_password_conf}

%post ppm
#=================================================
# Post Installation
#=================================================

# Change owner
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapserverdir}/%{_lib}
/bin/chown -R root:%{ldapgroup} %{ppm_conf}
/bin/chmod 640 %{ppm_conf}

%preun -n openldap-ltb
#=================================================
# Pre Uninstallation
#=================================================

%if "%{?dist}" == ".el7" || "%{?dist}" == ".el8"
%systemd_preun slapd.service
%endif

# Don't do this if newer version is installed
if [ $1 -eq 0 ]
then
	if [ -e /etc/init.d/slapd ]
	then
	# Stop slapd and disable service
	/sbin/service slapd stop > /dev/null 2>&1
	/sbin/chkconfig --del slapd
	fi

        # Remove syslog facility
%if "%{?dist}" == ".el5"
	sed -i '/local4\..*/d' /etc/syslog.conf
	/sbin/service syslog restart
%else
	sed -i '/local4\..*/d' /etc/rsyslog.conf
	/sbin/service rsyslog restart
%endif

fi

# Always do this
# Remove OpenLDAP libraries from the system
sed -i '\:'%{ldapserverdir}/%{_lib}':d' /etc/ld.so.conf
/sbin/ldconfig

%posttrans -n openldap-ltb
#=================================================
# Post transaction
#=================================================
# Do this after an upgrade
if [ -e %{_localstatedir}/openldap-ltb-slapd-running ]
then
	# Start slapd
%if "%{?dist}" == ".el7" || "%{?dist}" == ".el8"
	/bin/systemctl start slapd.service
%else
	/sbin/service slapd start > /dev/null 2>&1
%endif

	rm -f %{_localstatedir}/openldap-ltb-slapd-running
fi

if [ -e %{_localstatedir}/slapd.default ]
then
	mv %{_localstatedir}/slapd.default %{ldapserverdir}/etc/openldap/slapd-cli.conf
	rm -f %{_localstatedir}/slapd.default
fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n openldap-ltb
%defattr(-, root, root, 0755)
%{ldapdir}
%docdir %{ldapserverdir}/share/man
%config(noreplace) %{ldapserverdir}/etc/openldap/slapd.conf
%config(noreplace) %{ldapserverdir}/etc/openldap/ldap.conf
%if "%{?dist}" == ".el7" || "%{?dist}" == ".el8"
%{_unitdir}/slapd.service
%else
/etc/init.d/slapd
%endif
%config(noreplace) %{ldapserverdir}/etc/openldap/slapd-cli.conf
/etc/profile.d/openldap.sh
%{ldaplogsdir}
%config(noreplace) /etc/logrotate.d/openldap
%{ldapbackupdir}
%exclude %{check_password_conf}
%exclude %{ldapserverdir}/%{_lib}/check_password.so
%exclude %{ldapserverdir}/libexec/openldap
%config(noreplace) %{ldapdatadir}/DB_CONFIG
%exclude %{ppm_conf}
%exclude %{ldapserverdir}/%{_lib}/ppm.so
%exclude %{ldapserverdir}/%{_lib}/ppm_test
%exclude %{ldapserverdir}/sbin/mdb_copy
%exclude %{ldapserverdir}/sbin/mdb_stat
%exclude %{ldapserverdir}/share/man/man1/mdb_copy.1
%exclude %{ldapserverdir}/share/man/man1/mdb_stat.1
%exclude %{ldapserverdir}/share/man/man5/slapo-explockout.5

%files check-password
%config(noreplace) %{check_password_conf}
%{ldapserverdir}/%{_lib}/check_password.so

%files ppm
%config(noreplace) %{ppm_conf}
%{ldapserverdir}/%{_lib}/ppm.so
%{ldapserverdir}/%{_lib}/ppm_test

%files contrib-overlays
%{ldapserverdir}/libexec/openldap
%exclude %{ldapserverdir}/libexec/openldap/explockout.a
%exclude %{ldapserverdir}/libexec/openldap/explockout.la
%exclude %{ldapserverdir}/libexec/openldap/explockout.so
%exclude %{ldapserverdir}/libexec/openldap/explockout.so.0
%exclude %{ldapserverdir}/libexec/openldap/explockout.so.0.0.0

%files mdb-utils
%{ldapserverdir}/sbin/mdb_copy
%{ldapserverdir}/sbin/mdb_stat
%doc %{ldapserverdir}/share/man/man1/mdb_copy.1
%doc %{ldapserverdir}/share/man/man1/mdb_stat.1

%files explockout
%{ldapserverdir}/libexec/openldap/explockout.a
%{ldapserverdir}/libexec/openldap/explockout.la
%{ldapserverdir}/libexec/openldap/explockout.so
%{ldapserverdir}/libexec/openldap/explockout.so.0
%{ldapserverdir}/libexec/openldap/explockout.so.0.0.0
%doc %{ldapserverdir}/share/man/man5/slapo-explockout.5

#=================================================
# Changelog
#=================================================
%changelog
* Thu Aug 29 2019 - Clement Oudot <clem@ltb-project.org> - 2.4.48-2
- Upgrade to initscript 2.5
- Upgrade to ppm 1.8
* Thu Jul 25 2019 - Clement Oudot <clem@ltb-project.org> - 2.4.48-1
- Upgrade to OpenLDAP 2.4.48
* Mon Jan 07 2019 - Clement Oudot <clem@ltb-project.org> - 2.4.47-1
- Upgrade to OpenLDAP 2.4.47
- Add explockout overlay 1.0
- Upgrade to initscript 2.4
* Mon Apr 02 2018 - Clement Oudot <clem@ltb-project.org> - 2.4.46-1
- Upgrade to OpenLDAP 2.4.46
- Upgrade to ppm 1.7
- Upgrade to initscript 2.3
* Mon Oct 02 2017 - Clement Oudot <clem@ltb-project.org> - 2.4.45-2
- Rebuilt on RHEL 7 to fix kerberos dependency
* Mon Jun 05 2017 - Clement Oudot <clem@ltb-project.org> - 2.4.45-1
- Upgrade to OpenLDAP 2.4.45
- Upgrade to ppm 1.6
* Fri May 05 2017 - Clement Oudot <clem@ltb-project.org> - 2.4.44-3
- Rebuilt on RHEL 7 to fix kerberos dependency (#10)
- Upgrade to ppm 1.5
- Upgrade to initscript 2.2
* Wed Feb 22 2017 - Manoel Domingues Junior <mdjunior@ufrj.br> - 2.4.44-2 / 1.1-8
- Add PBKDF2 module
* Thu Feb 18 2016 - Clement Oudot <clem@ltb-project.org> - 2.4.44-2 / 1.1-8
- Fix user/group creation (#830)
* Mon Feb 08 2016 - Clement Oudot <clem@ltb-project.org> - 2.4.44-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.44
- ldap user should be a system user (#828)
* Tue Dec 01 2015 - Clement Oudot <clem@ltb-project.org> - 2.4.43-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.43
- Restart OpenLDAP after upgrade (#788)
- Fix crash in smbk5pwd (#793)
- Exclude files from ppm and mdb-utils package (#814)
* Mon Aug 17 2015 - Clement Oudot <clem@ltb-project.org> - 2.4.42-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.42
- Add SHA 512 in contrib package (#752)
- Enable TCP wrappers (#784)
* Thu Jul 02 2015 - Clement Oudot <clem@ltb-project.org> - 2.4.41-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.41 (#778)
- Upgrade to init script 2.1 (#778)
- Add ppm module (#738)
- Add autogroup overlay (#771)
* Tue Sep 30 2014 - Clement Oudot <clem@ltb-project.org> - 2.4.40-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.40
- Enable sock backend (#661)
- Upgrade to init script 2.0 (#731)
* Mon Feb 03 2014 - Clement Oudot <clem@ltb-project.org> - 2.4.39-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.39
- Mark documentation as such in the RPM spec file (#636)
- Include MDB utilities in RPM (#638)
- Add man directory to $MANPATH (#644)
* Wed Nov 27 2013 - Clement Oudot <clem@ltb-project.org> - 2.4.38-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.38
* Thu Oct 31 2013 - Clement Oudot <clem@ltb-project.org> - 2.4.37-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.37
- Disable dynamic library linking (#629)
* Tue Aug 20 2013 - Clement Oudot <clem@ltb-project.org> - 2.4.36-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.36
- Add dependency to BerkeleyDB (#610)
* Tue Apr 02 2013 - Clement Oudot <clem@ltb-project.org> - 2.4.35-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.35
- Remove dependency to Berkeley DB (#585)
- Make DB_CONFIG a config file (#588)
* Tue Mar 12 2013 - Clement Oudot <clem@ltb-project.org> - 2.4.34-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.34
- Upgrade to init script 1.9
* Thu Oct 11 2012 - Clement Oudot <clem@ltb-project.org> - 2.4.33-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.33
- Upgrade to init script 1.8
* Thu Aug 23 2012 - Clement Oudot <clem@ltb-project.org> - 2.4.32-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.32
- Upgrade to init script 1.7
- Comment to enable config delete option (#476)
- Use rsyslog on EL6 (#480)
* Tue Apr 24 2012 - Clement Oudot <clem@ltb-project.org> - 2.4.31-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.31
- Upgrade to init script 1.6
- Add OpenLDAP libraries to the system (#411)
* Fri Mar 09 2012 - Clement Oudot <clem@ltb-project.org> - 2.4.30-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.30
- Upgrade to init script 1.5
* Thu Jan 05 2012 - Clement Oudot <clem@ltb-project.org> - 2.4.28-2 / 1.1-8
- Upgrade to init script 1.4
- Remove circular build dependency
* Wed Nov 30 2011 - Clement Oudot <clem@ltb-project.org> - 2.4.28-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.28
- Create package contrib-overlays
* Fri Nov 25 2011 - Clement Oudot <clem@ltb-project.org> - 2.4.27-1 / 1.1-8
- Upgrade to OpenLDAP 2.4.27
- Upgrade to init script 1.3
- Remove OpenLDAP restart on log rotation
* Fri Jul 08 2011 - Clement Oudot <clem@ltb-project.org> - 2.4.26-1 / 1.1-7
- Upgrade to OpenLDAP 2.4.26
* Tue May 03 2011 - Clement Oudot <clem@ltb-project.org> - 2.4.25-1 / 1.1-6
- Upgrade to OpenLDAP 2.4.25
- Enable SLAPI
* Thu Mar 24 2011 - Clement Oudot <clem@ltb-project.org> - 2.4.24-1 / 1.1-5
- Upgrade to OpenLDAP 2.4.24
- Upgrade to init script 1.2
* Wed Jul 21 2010 - Clement Oudot <clem@ltb-project.org> - 2.4.23-1 / 1.1-4
- Upgrade to OpenLDAP 2.4.23
- Upgrade to init script 1.1
* Mon May 10 2010 - Clement Oudot <clem@ltb-project.org> - 2.4.22-1 / 1.1-3
- Upgrade to OpenLDAP 2.4.22
- Upgrade to init script 1.0
* Fri Feb 19 2010 - Clement Oudot <clem@ltb-project.org> - 2.4.21-1 / 1.1-2
- Upgrade to OpenLDAP 2.4.21
* Sat Oct 31 2009 - Clement Oudot <clem@ltb-project.org> - 2.4.19-1 / 1.1-1
- Upgrade to OpenLDAP 2.4.19 (#135)
- Upgrade to init script 0.9
- Upgrade to check_password 1.1
- Disable strip to provide debuginfo package (#117)
- Use %config(noreplace)
- Start slapd before upgrade, and start after upgrade
* Fri Jul 3 2009 - Clement Oudot <clem@ltb-project.org> - 2.4.16-2 / 1.0.3-4
- Upgrade to init script 0.8
* Wed Apr 29 2009 - Clement Oudot <clem@ltb-project.org> - 2.4.16-1 / 1.0.3-4
- Upgrade to OpenLDAP 2.4.16
* Mon Mar 2 2009 - Clement Oudot <clem@ltb-project.org> - 2.4.15-1 / 1.0.3-3
- This package is now maintened in LTB project
- Upgrade to OpenLDAP 2.4.15
- Upgrade to init script 0.7
* Fri Feb 6 2009 - Clement Oudot <clement.oudot@linagora.com> - 2.4.13-2
- Upgrade check_password to 1.0.3 (useCracklib parameter support)
* Thu Jan 15 2009 - Clement Oudot <clement.oudot@linagora.com> - 2.4.13-1
- remove checkLdapPwdExpiration script with cron configuration (provided by linagora-ldap-tools)
- add pwdModuleChecker check_password-1.0.2  from Calivia
- enable modules to support external password checking module
* Fri Oct 24 2008 - Clement Oudot <clement.oudot@linagora.com> - 2.4.12-1.2
- install in /opt
- remove slurpd references
- set OpenLDAP and BerkelyDB dirs in all scripts
* Mon Oct 20 2008 - Clement Oudot <clement.oudot@linagora.com> - 2.4.12-1.1
- new version 2.4.12
- use BerkeleyDB 4.6.21
- use SASL and all overlays
- use init script 0.6.5
- configure syslog and logrotate
- add checkLdapPwdExpiration script with cron configuration
* Fri Sep 29 2006 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.3.27-1.1
- Add Berkeley DB logs directory
* Fri Sep 29 2006 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.3.27-1.0
- New version
* Fri Nov 25 2005 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.3.12-1.0
- New version
* Thu Oct 6 2005 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.2.28-4.2
- Another fix for init level
* Thu Oct 6 2005 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.2.28-4
- Fix typo in CFLAGS
- Fix init level in init script (v0.4)
* Mon Oct 3 2005 - Clement Oudot <clement.oudot@linagora.com> - 2.2.28-3
- Update init script version from 0.2 to 0.3
* Fri Sep 30 2005 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.2.28-2
- add patch because getaddrinfo is thread-safe on Linux
* Tue Aug 30 2005 - Clement Oudot <clement.oudot@linagora.com> - 2.2.28-1
- package for RHEL3 ES UP5
