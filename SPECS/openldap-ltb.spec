#=================================================
# Specification file for OpenLDAP
#
# Install OpenLDAP
# Install an init script in /etc/init.d
# Create user/group ldap
# Configure syslog and logrotate
# Install a pwdChecker module
#
# Copyright (C) 2008 Raphael OUAZANA
# Copyright (C) 2008 Clement OUDOT
# Copyright (C) 2008 LINAGORA
#
# Provided by LTB-project (http://www.ltb-project.org)
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        openldap
%define real_version     2.4.28
%define release_version  2%{?dist}

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
%define slapd_init_version          1.4

%define check_password_name         ltb-project-openldap-ppolicy-check-password
%define check_password_version      1.1
%define check_password_conf         %{ldapserverdir}/etc/openldap/check_password.conf
%define check_password_minPoints    3
%define check_password_useCracklib  0
%define check_password_minUpper     0
%define check_password_minLower     0
%define check_password_minDigit     0
%define check_password_minPunct     0

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
# Sources available on http://www.ltb-project.org
Source1: %{slapd_init_name}-%{slapd_init_version}.tar.gz
# Sources available on http://www.ltb-project.org
Source2: %{check_password_name}-%{check_password_version}.tar.gz
Source3: openldap.sh
Source4: DB_CONFIG
Source5: openldap.logrotate
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: gcc, make
BuildRequires: openssl-devel, cyrus-sasl-devel, berkeleydb-ltb >= 4.6.21, libtool-ltdl-devel
BuildRequires: cracklib
Requires: berkeleydb-ltb >= 4.6.21, gawk, libtool-ltdl

Requires(pre): coreutils
Obsoletes: openldap-servers, openldap-clients

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
Release:        8%{?dist}
Group:          Applications/System
URL:		http://www.ltb-project.org

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
# Source preparation
#=================================================
%prep
%setup -n %{real_name}-%{real_version}
%setup -n %{real_name}-%{real_version} -T -D -a 1
%setup -n %{real_name}-%{real_version} -T -D -a 2

#=================================================
# Building
#=================================================
%build
# OpenLDAP
export CC="gcc"
export CFLAGS="-DOPENLDAP_FD_SETSIZE=4096 -O2 -g"
export CPPFLAGS="-I%{bdbdir}/include -I/usr/kerberos/include"
export LDFLAGS="-L%{bdbdir}/%{_lib}"
./configure --enable-ldap --enable-debug --prefix=%{ldapserverdir} --libdir=%{ldapserverdir}/%{_lib} --with-tls --with-cyrus-sasl --enable-spasswd --enable-overlays --enable-modules --enable-slapi
make depend
make %{?_smp_mflags}
# check_password
cd %{check_password_name}-%{check_password_version} 
make %{?_smp_mflags} "CONFIG=%{check_password_conf}" "LDAP_INC=-I../include -I../servers/slapd"
cd ..
# contrib-overlays
cd contrib/slapd-modules
## lastbind
cd lastbind
make %{?_smp_mflags}
cd ..
## smbk5pwd
cd smbk5pwd
make %{?_smp_mflags} "DEFS=-DDO_SAMBA -DDO_SHADOW" "LDAP_LIB=-L%{_builddir}/%{real_name}-%{real_version}/libraries/liblber/.libs/ -L%{_builddir}/%{real_name}-%{real_version}/libraries/libldap_r/.libs/ -lldap_r -llber" "prefix=%{ldapserverdir}"
cd ..
cd ../..

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
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
install -m 755 %{slapd_init_name}-%{slapd_init_version}/slapd %{buildroot}/etc/init.d/slapd
install -m 644 %{slapd_init_name}-%{slapd_init_version}/slapd.default %{buildroot}/etc/default/slapd
sed -i 's:^SLAPD_PATH.*:SLAPD_PATH="'%{ldapdir}'":' %{buildroot}/etc/default/slapd
sed -i 's:^SLAPD_USER.*:SLAPD_USER="'%{ldapuser}'":' %{buildroot}/etc/default/slapd
sed -i 's:^SLAPD_GROUP.*:SLAPD_GROUP="'%{ldapgroup}'":' %{buildroot}/etc/default/slapd
sed -i 's:^BDB_PATH.*:BDB_PATH="'%{bdbdir}'":' %{buildroot}/etc/default/slapd
sed -i 's:^BACKUP_PATH.*:BACKUP_PATH="'%{ldapbackupdir}'":' %{buildroot}/etc/default/slapd

# PATH modification
mkdir -p %{buildroot}/etc/profile.d
install -m 755 %{SOURCE3} %{buildroot}/etc/profile.d/openldap.sh
sed -i 's:^OL_BIN.*:OL_BIN='%{ldapdir}/bin':' %{buildroot}/etc/profile.d/openldap.sh
sed -i 's:^OL_SBIN.*:OL_SBIN='%{ldapdir}/sbin':' %{buildroot}/etc/profile.d/openldap.sh

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

# contrib-overlays
cd contrib/slapd-modules
cd lastbind
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
cd smbk5pwd
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
cd ../..

%pre -n openldap-ltb
#=================================================
# Pre Installation
#=================================================

# If upgrade stop slapd
if [ $1 -eq 2 ]
then
	/sbin/service slapd stop > /dev/null 2>&1
fi

%post -n openldap-ltb
#=================================================
# Post Installation
#=================================================

# Do this at first install
if [ $1 -eq 1 ]
then
	# Set slapd as service
	/sbin/chkconfig --add slapd

	# Create user and group
	/usr/sbin/groupadd %{ldapgroup}
	/usr/sbin/useradd %{ldapuser} -g %{ldapgroup}

	# Add syslog facility
	echo "local4.*	-%{ldaplogfile}" >> /etc/syslog.conf
	/sbin/service syslog restart > /dev/null 2>&1
fi

# Always do this
# Change owner
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapserverdir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapdatadir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldaplogsdir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapbackupdir}

%post check-password
#=================================================
# Post Installation
#=================================================

# Change owner
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapserverdir}/%{_lib}

%preun -n openldap-ltb
#=================================================
# Pre uninstallation
#=================================================

# Don't do this if newer version is installed
if [ $1 -eq 0 ]
then
	# Stop slapd
	/sbin/service slapd stop > /dev/null 2>&1

	# Delete service
	/sbin/chkconfig --del slapd

        # Remove syslog facility
	sed -i '/local4\..*/d' /etc/syslog.conf
	/sbin/service syslog restart
fi

%postun -n openldap-ltb
#=================================================
# Post uninstallation
#=================================================

# Don't do this if newer version is installed
if [ $1 -eq 0 ]
then
	# Delete user and group
	/usr/sbin/userdel -r %{ldapuser}
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
%config(noreplace) %{ldapserverdir}/etc/openldap/slapd.conf
%config(noreplace) %{ldapserverdir}/etc/openldap/ldap.conf
/etc/init.d/slapd
%config(noreplace) /etc/default/slapd
/etc/profile.d/openldap.sh
%{ldaplogsdir}
%config(noreplace) /etc/logrotate.d/openldap
%{ldapbackupdir}
%exclude %{check_password_conf}
%exclude %{ldapserverdir}/%{_lib}/check_password.so
%exclude %{ldapserverdir}/libexec/openldap

%files check-password
%config(noreplace) %{check_password_conf}
%{ldapserverdir}/%{_lib}/check_password.so

%files contrib-overlays
%{ldapserverdir}/libexec/openldap

#=================================================
# Changelog
#=================================================
%changelog
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
* Tue Apr 29 2009 - Clement Oudot <clem@ltb-project.org> - 2.4.16-1 / 1.0.3-4
- Upgrade to OpenLDAP 2.4.16
* Mon Mar 2 2009 - Clement Oudot <clem@ltb-project.org> - 2.4.15-1 / 1.0.3-3
- This package is now maintened in LTB project
- Upgrade to OpenLDAP 2.4.15
- Upgrade to init script 0.7
* Fri Feb 6 2009 - Clement Oudot <clement.oudot@linagora.com> - 2.4.13-2
- Upgrade check_password to 1.0.3 (useCracklib parameter support)
* Fri Jan 15 2009 - Clement Oudot <clement.oudot@linagora.com> - 2.4.13-1
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
* Mon Oct 6 2005 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.2.28-4.2
- Another fix for init level
* Mon Oct 6 2005 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.2.28-4
- Fix typo in CFLAGS
- Fix init level in init script (v0.4)
* Mon Oct 3 2005 - Clement Oudot <clement.oudot@linagora.com> - 2.2.28-3
- Update init script version from 0.2 to 0.3
* Fri Sep 30 2005 - Raphael Ouazana <raphael.ouazana@linagora.com> - 2.2.28-2
- add patch because getaddrinfo is thread-safe on Linux
* Thu Aug 30 2005 - Clement Oudot <clement.oudot@linagora.com> - 2.2.28-1
- package for RHEL3 ES UP5
