#=================================================
# Specification file for OpenLDAP
#
# Install OpenLDAP
# Install an a systemd service
# Create user/group ldap
# Install ppm, an extension to password policy module
#
# Copyright (C) 2008-2023 Clement OUDOT
# Copyright (C) 2018-2023 Worteks
# Copyright (C) 2015-2023 David COUTADEUR
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
%define real_version     2.6.6
%define release_version  1%{?dist}

# exclude private libraries
%global _privatelibs                 libldap
%global _privatelibs %{_privatelibs}|liblber
%global _privatelibs %{_privatelibs}|libslapi
%global __provides_exclude ^(%{_privatelibs}).*so.*$
%global __requires_exclude ^(%{_privatelibs}).*so.*$

%define ldapdir          /usr/local/openldap
%define ldapserverdir    %{ldapdir}
%define ldapdatadir      %{ldapdir}/var/openldap-data
%define ldapbackupdir    /var/backups/openldap
%define ldaplogdir       /var/log/slapd-ltb
%define ldaplogfile      %{ldaplogdir}/slapd.log
%define ldapconfdir      %{ldapdir}/etc/openldap/slapd.d

%define ldapuser         ldap
%define ldapgroup        ldap

%define slapd_cli_name             slapd-cli
%define slapd_cli_version          3.2
%define slapd_cli_bin              %{ldapdir}/sbin/slapd-cli

%define ppm_name         ppm
%define ppm_version      2.2
%define ppm_conf         %{ldapserverdir}/etc/openldap/ppm.example

%define explockout_name            explockout
%define explockout_version         1.1

#=================================================
# Header
#=================================================
Summary: OpenLDAP server with addons from the LDAP Tool Box project
Name: %{real_name}-ltb
Version: %{real_version}
Release: %{release_version}
# http://www.openldap.org/software/release/license.html
License: OpenLDAP Public License

URL: http://www.openldap.org/

Source0: https://www.openldap.org/software/download/OpenLDAP/openldap-release/%{real_name}-%{real_version}.tgz
Source1: https://github.com/ltb-project/slapd-cli/archive/v%{slapd_cli_version}/%{slapd_cli_name}-%{slapd_cli_version}.tar.gz
Source2: openldap.sh
Source4: https://github.com/ltb-project/explockout/archive/v%{explockout_version}/%{explockout_name}-%{explockout_version}.tar.gz
Source5: https://github.com/ltb-project/ppm/archive/v%{ppm_version}/%{ppm_name}-%{ppm_version}.tar.gz

BuildRequires: cracklib
BuildRequires: cracklib-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: gcc
BuildRequires: groff
BuildRequires: krb5-devel
BuildRequires: libkadm5
BuildRequires: libtool-ltdl-devel
BuildRequires: make
BuildRequires: pandoc

%if ! 0%{?el7}
BuildRequires: openssl-devel
BuildRequires: libevent-devel >= 2.1
%else
BuildRequires: tcp_wrappers-devel
BuildRequires: openssl11-devel
BuildRequires: libevent-ltb-devel >= 2.1
%endif

%{?systemd_requires}
BuildRequires: systemd
BuildRequires: libsodium-devel

Requires: gawk, /usr/bin/perl, libtool-ltdl, bash-completion, libsodium
%if ! 0%{?el7}
Requires: libevent >= 2.1
Requires: openssl
%else
Requires: libevent-ltb >= 2.1
Requires: openssl11
%endif

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
# Subpackage contrib-overlays
#=================================================
%package contrib-overlays
Summary:        Overlays contributed to OpenLDAP
Version:        %{real_version}
Release:        %{release_version}
URL:            http://www.ltb-project.org

Requires:       %{real_name}-ltb >= %{real_version}, cracklib

%description contrib-overlays
Some overlays are not included in the OpenLDAP main package but provided
as contributions. This package provide these ones:
autogroup noopsrch nssov pw-pbkdf2 pw-sha2 smbk5pwd variant vc

This is provided by LDAP Tool Box project: http://www.ltb-project.org


#=================================================
# Subpackage mdb-utils
#=================================================
%package mdb-utils
Summary:        MDB utilities
Version:        %{real_version}
Release:        %{release_version}
URL:            http://www.ltb-project.org

Requires:       %{real_name}-ltb >= %{real_version}

%description mdb-utils
MDB utilities contain both mdb_stat and mdb_copy, and the associated
documentation.

This is provided by LDAP Tool Box project: http://www.ltb-project.org

#=================================================
# Subpackage explockout
#=================================================
%package explockout
Summary:        OpenLDAP overlay explockout
Version:        %{real_version}
Release:        %{release_version}
URL:            https://github.com/ltb-project/explockout

Requires:       %{real_name}-ltb >= %{real_version}

%description explockout
explockout is an OpenLDAP module that denies authentication to users who
have previously failed to authenticate, requiring them to wait for an
exponential time

#=================================================
# Source preparation
#=================================================
%prep
%setup -q -n %{real_name}-%{real_version}
%setup -q -n %{real_name}-%{real_version} -T -D -a 1
%setup -q -n %{real_name}-%{real_version} -T -D -a 4
%setup -q -n %{real_name}-%{real_version} -T -D -a 5

#=================================================
# Building
#=================================================
%build
# OpenLDAP
export CC="gcc"
export CFLAGS="-DOPENLDAP_FD_SETSIZE=4096 -O2 -g -DSLAP_SCHEMA_EXPOSE"
# Uncomment to enable config delete option
#export CFLAGS="-DOPENLDAP_FD_SETSIZE=4096 -O2 -g -DSLAP_SCHEMA_EXPOSE -DSLAP_CONFIG_DELETE"
export CPPFLAGS="-I/usr/kerberos/include"
export LDFLAGS=""
%if 0%{?el7}
export CPPFLAGS="${CPPFLAGS} -I/usr/include/openssl11 -I/usr/local/libevent-ltb-2.1/include"
export LDFLAGS="${LDFLAGS} -L/usr/%{_lib}/openssl11 -L/usr/local/libevent-ltb-2.1/lib"
%endif
./configure \
  --prefix=%{ldapserverdir} \
  --libdir=%{ldapserverdir}/%{_lib} \
  --enable-modules=yes \
  --enable-overlays=mod \
  --enable-backends=mod \
  --enable-dynamic=yes \
  --with-tls=openssl \
  --enable-debug \
  --with-cyrus-sasl \
  --enable-spasswd \
  --enable-ppolicy=mod \
  --enable-crypt \
  --enable-slapi \
  --enable-mdb=mod \
  --enable-ldap=mod \
  --enable-meta=mod \
  --enable-sock=mod \
%{?el7:--enable-wrappers} \
  --enable-rlookups \
  --enable-argon2=yes \
  --enable-otp=mod \
  --enable-balancer=mod \
  --enable-sql=no \
  --enable-ndb=no \
  --enable-wt=no \
  --enable-perl=no
make depend
make %{?_smp_mflags}
# contrib-overlays
cd contrib/slapd-modules
## smbk5pwd
cd smbk5pwd
make clean
make %{?_smp_mflags} "DEFS=-DDO_SAMBA -DDO_SHADOW" "LDAP_LIB=-L../../../libraries/liblber/.libs/ -L../../../libraries/libldap/.libs/ -lldap -llber" "prefix=%{ldapserverdir}"
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
# variant
cd variant
make clean
make "prefix=%{ldapserverdir}"
cd ..
# vc
cd vc
make clean
make "prefix=%{ldapserverdir}"
cd ..
cd ../..
# MDB utils
cd libraries/liblmdb
make %{?_smp_mflags}
cd ../..
# explockout
cd %{explockout_name}-%{explockout_version}
make clean
make "OLDAP_SOURCES=.." "LIBDIR=%{ldapserverdir}/libexec/openldap"
cd ..
## ppm
cd %{ppm_name}-%{ppm_version}
make clean
make LDAP_SRC=.. prefix=%{ldapserverdir} libdir=%{ldapserverdir}/lib64
%if "%{real_version}" == "2.5.7"
:
%else
make doc prefix=%{ldapserverdir}
%endif
make test LDAP_SRC=.. prefix=%{ldapserverdir} libdir=%{ldapserverdir}/lib64
cd ..

#=================================================
# Installation
#=================================================
%install
make install DESTDIR=%{buildroot} STRIP=""

# create some directories
mkdir -p %{buildroot}%{ldapdatadir}
mkdir -p %{buildroot}%{ldapbackupdir}
mkdir -p %{buildroot}/etc/profile.d
mkdir -p %{buildroot}%{_unitdir}/

# Copy 3rd party files

## systemd
install -m 644 %{slapd_cli_name}-%{slapd_cli_version}/slapd-ltb.service %{buildroot}%{_unitdir}/
install -m 644 %{slapd_cli_name}-%{slapd_cli_version}/lload-ltb.service %{buildroot}%{_unitdir}/

## profile
install -m 755 %{SOURCE2} %{buildroot}/etc/profile.d/openldap.sh

## slapd-cli
install -m 755 %{slapd_cli_name}-%{slapd_cli_version}/slapd-cli %{buildroot}%{ldapserverdir}/sbin/
install -m 644 %{slapd_cli_name}-%{slapd_cli_version}/slapd-cli.conf %{buildroot}%{ldapserverdir}/etc/openldap/
install -m 644 %{slapd_cli_name}-%{slapd_cli_version}/config-template-2.6.conf %{buildroot}%{ldapserverdir}/etc/openldap/
install -m 644 %{slapd_cli_name}-%{slapd_cli_version}/config-template-2.6.ldif %{buildroot}%{ldapserverdir}/etc/openldap/
install -m 644 %{slapd_cli_name}-%{slapd_cli_version}/data-template-2.6.ldif %{buildroot}%{ldapserverdir}/etc/openldap/
install -m 640 %{slapd_cli_name}-%{slapd_cli_version}/lload.conf %{buildroot}%{ldapserverdir}/etc/openldap/
mkdir -p %{buildroot}/etc/bash_completion.d/
install -m 644 %{slapd_cli_name}-%{slapd_cli_version}/slapd-cli-prompt %{buildroot}/etc/bash_completion.d/

# replace variables in slapd-cli.conf
sed -i 's:^SLAPD_PATH.*:SLAPD_PATH="'%{ldapdir}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf
sed -i 's:^SLAPD_USER.*:SLAPD_USER="'%{ldapuser}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf
sed -i 's:^SLAPD_GROUP.*:SLAPD_GROUP="'%{ldapgroup}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf
sed -i 's:^BACKUP_PATH.*:BACKUP_PATH="'%{ldapbackupdir}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf
sed -i 's:^SLAPD_CONF_DIR.*:SLAPD_CONF_DIR="'%{ldapconfdir}'":' %{buildroot}%{ldapserverdir}/etc/openldap/slapd-cli.conf

# PATH modification
sed -i 's:^OL_BIN.*:OL_BIN='%{ldapdir}/bin':' %{buildroot}/etc/profile.d/openldap.sh
sed -i 's:^OL_SBIN.*:OL_SBIN='%{ldapdir}/sbin':' %{buildroot}/etc/profile.d/openldap.sh

# Modify data directory in slapd.conf
sed -i 's:^directory.*:directory\t'%{ldapdatadir}':' %{buildroot}%{ldapserverdir}/etc/openldap/slapd.conf

# contrib-overlays
cd contrib/slapd-modules
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
cd variant
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
cd vc
make install "prefix=%{buildroot}%{ldapserverdir}"
cd ..
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
make install "OLDAP_SOURCES=.." "DSTDIR=%{buildroot}%{ldapserverdir}/libexec/openldap"
install -m 644 "slapo-explockout.5" "%{buildroot}%{ldapserverdir}/share/man/man5"
cd ..

cd %{ppm_name}-%{ppm_version}
make install "LDAP_SRC=.." "prefix=%{buildroot}%{ldapserverdir}" "libdir=%{buildroot}%{ldapserverdir}/libexec/openldap"
cp ppm_test "%{buildroot}%{ldapserverdir}/libexec/openldap/"
cd ..

%pretrans -n openldap-ltb
#=================================================
# Pre Transaction
#=================================================

%{ldapserverdir}/sbin/slapd-cli status > /dev/null 2>&1
if [ $? -eq 0 ]
then
	touch %{_localstatedir}/openldap-ltb-slapd-running
fi
%{ldapserverdir}/sbin/slapd-cli lloadstatus > /dev/null 2>&1
if [ $? -eq 0 ]
then
	touch %{_localstatedir}/openldap-ltb-lload-running
fi

%pre -n openldap-ltb
#=================================================
# Pre Installation
#=================================================
# Create user and group if needed
getent group %{ldapgroup} >/dev/null || groupadd -r -g 55 %{ldapgroup}
getent passwd %{ldapuser} >/dev/null || useradd -r -g %{ldapgroup} -u 55 -d %{ldapdir} -s /sbin/nologin -c "LDAP User" %{ldapuser}

# If upgrade stop slapd and lload
if [ $1 -eq 2 ]
then
	%{ldapserverdir}/sbin/slapd-cli lloadstop > /dev/null 2>&1
	%{ldapserverdir}/sbin/slapd-cli stop > /dev/null 2>&1
fi

%post -n openldap-ltb
#=================================================
# Post Installation
#=================================================

%systemd_post slapd-ltb.service
/bin/systemctl --system daemon-reload

%systemd_post lload-ltb.service
/bin/systemctl --system daemon-reload

# Do this at first install
if [ $1 -eq 1 ]
then
	# Set slapd as service
	/bin/systemctl enable slapd-ltb.service
fi

# Always do this
# Specifically adapt some files/directories owner and permissions
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapdatadir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapbackupdir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldapserverdir}/var/run
/bin/chown -R root:%{ldapgroup} %{ldapserverdir}/etc/openldap/slapd.conf
/bin/chmod 640 %{ldapserverdir}/etc/openldap/slapd.conf
/bin/chown -R root:%{ldapgroup} %{ldapserverdir}/etc/openldap/lload.conf
/bin/chmod 640 %{ldapserverdir}/etc/openldap/lload.conf
mkdir -p %{ldaplogdir}
/bin/chown -R %{ldapuser}:%{ldapgroup} %{ldaplogdir}

# Add configuration directory if it does not exist
mkdir -p %{ldapconfdir}
chown root:%{ldapgroup} %{ldapconfdir}
chmod 770 %{ldapconfdir}

# Adapt slapd version number
if ! grep -q -E "^SLAPD_VERSION=" %{ldapserverdir}/etc/openldap/slapd-cli.conf; then
	printf 'SLAPD_VERSION=2.6' >> %{ldapserverdir}/etc/openldap/slapd-cli.conf
else
	sed -i -e 's/SLAPD_VERSION=.*$/SLAPD_VERSION=2.6/' %{ldapserverdir}/etc/openldap/slapd-cli.conf
fi

# first install + empty configuration directory, so import a new fresh config from template
if [ $1 -eq 1 ] && [ -z "$( ls -A %{ldapconfdir} )" ]; then

  # Import configuration from ldif template
  %{slapd_cli_bin} importldifconfigtemplate > /dev/null

fi

# Start OpenLDAP at the end of first install
if [ $1 -eq 1 ]
then
  /bin/systemctl start slapd-ltb.service
fi

%preun -n openldap-ltb
#=================================================
# Pre Uninstallation
#=================================================

%systemd_preun slapd-ltb.service

# Don't do this if newer version is installed
if [ $1 -eq 0 ]
then
	# Stop slapd and disable service
	/bin/systemctl stop slapd-ltb.service > /dev/null 2>&1
	/bin/systemctl disable slapd-ltb.service
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
	/bin/systemctl start slapd-ltb.service

	rm -f %{_localstatedir}/openldap-ltb-slapd-running
fi

if [ -e %{_localstatedir}/openldap-ltb-lload-running ]
then
	# Start lload
	/bin/systemctl start lload-ltb.service

	rm -f %{_localstatedir}/openldap-ltb-lload-running
fi


#=================================================
# Files
#=================================================
%files -n openldap-ltb
%defattr(-, root, root, 0755)
%{ldapdir}
%docdir %{ldapserverdir}/share/man
%config(noreplace) %{ldapserverdir}/etc/openldap/slapd.conf
%config(noreplace) %{ldapserverdir}/etc/openldap/ldap.conf
%{_unitdir}/slapd-ltb.service
%{_unitdir}/lload-ltb.service
%config(noreplace) %{ldapserverdir}/etc/openldap/slapd-cli.conf
%config(noreplace) %{ldapserverdir}/etc/openldap/*template*
%config(noreplace) %{ldapserverdir}/etc/openldap/lload.conf
/etc/profile.d/openldap.sh
%config /etc/bash_completion.d/slapd-cli-prompt
%{ldapbackupdir}
# exclude explockout man page and library
%exclude %{ldapserverdir}/share/man/man5/slapo-explockout.5
%exclude %{ldapserverdir}/libexec/openldap/explockout.*
# exclude mdb-utils man pages and binaries
%exclude %{ldapserverdir}/share/man/man1/mdb_copy.1
%exclude %{ldapserverdir}/share/man/man1/mdb_stat.1
%exclude %{ldapserverdir}/sbin/mdb_copy
%exclude %{ldapserverdir}/sbin/mdb_stat
# exclude contrib overlays man pages
%exclude %{ldapserverdir}/share/man/man5/slapo-nssov.5
%exclude %{ldapserverdir}/share/man/man5/slapo-smbk5pwd.5
%exclude %{ldapserverdir}/share/man/man5/slapo-variant.5
%exclude %{ldapserverdir}/share/man/man1/ldapvc.1
# exclude contrib overlays libraries
%exclude %{ldapserverdir}/libexec/openldap/autogroup.*
%exclude %{ldapserverdir}/libexec/openldap/noopsrch.*
%exclude %{ldapserverdir}/libexec/openldap/nssov.*
%exclude %{ldapserverdir}/libexec/openldap/pw-pbkdf2.*
%exclude %{ldapserverdir}/libexec/openldap/pw-sha2.*
%exclude %{ldapserverdir}/libexec/openldap/smbk5pwd.*
%exclude %{ldapserverdir}/libexec/openldap/variant.*
%exclude %{ldapserverdir}/libexec/openldap/vc.*

%files contrib-overlays
# contrib overlays man pages
%doc %{ldapserverdir}/share/man/man5/slapo-nssov.5
%doc %{ldapserverdir}/share/man/man5/slapo-smbk5pwd.5
%doc %{ldapserverdir}/share/man/man5/slapo-variant.5
%doc %{ldapserverdir}/share/man/man1/ldapvc.1
# contrib overlays libraries
%{ldapserverdir}/libexec/openldap/autogroup.*
%{ldapserverdir}/libexec/openldap/noopsrch.*
%{ldapserverdir}/libexec/openldap/nssov.*
%{ldapserverdir}/libexec/openldap/pw-pbkdf2.*
%{ldapserverdir}/libexec/openldap/pw-sha2.*
%{ldapserverdir}/libexec/openldap/smbk5pwd.*
%{ldapserverdir}/libexec/openldap/variant.*
%{ldapserverdir}/libexec/openldap/vc.*

%files mdb-utils
%{ldapserverdir}/sbin/mdb_copy
%{ldapserverdir}/sbin/mdb_stat
%doc %{ldapserverdir}/share/man/man1/mdb_copy.1
%doc %{ldapserverdir}/share/man/man1/mdb_stat.1

%files explockout
# explockout man page and library
%doc %{ldapserverdir}/share/man/man5/slapo-explockout.5
%{ldapserverdir}/libexec/openldap/explockout.*

#=================================================
# Changelog
#=================================================
%changelog
* Tue Aug 22 2023 - Clement Oudot <clem@ltb-project.org> - 2.6.6-1
- Upgrade to OpenLDAP 2.6.6
* Tue Jul 11 2023 - Clement Oudot <clem@ltb-project.org> - 2.6.5-1
- Upgrade to OpenLDAP 2.6.5
* Tue Feb 21 2023 - Clement Oudot <clem@ltb-project.org> - 2.6.4-1
- Upgrade to OpenLDAP 2.6.4
* Fri Aug 19 2022 - Clement Oudot <clem@ltb-project.org> - 2.6.3-1
- Upgrade to OpenLDAP 2.6.3
* Fri May 20 2022 - Clement Oudot <clem@ltb-project.org> - 2.6.2-1
- Upgrade to OpenLDAP 2.6.2
* Fri Oct 29 2021 - David Coutadeur <david.coutadeur@gmail.com> - 2.6.0.1
- Upgrade to OpenLDAP 2.6.0
* Tue Oct 26 2021 - Clement Oudot <clem@ltb-project.org> - 2.5.9-1
- Upgrade to OpenLDAP 2.5.9
* Tue Sep 07 2021 - Clement Oudot <clem@ltb-project.org> - 2.5.7-1
- Major version upgrade to OpenLDAP 2.5.7
* Fri Jun 04 2021 - Clement Oudot <clem@ltb-project.org> - 2.4.59-1
- Upgrade to OpenLDAP 2.4.59
* Fri Mar 19 2021 - Clement Oudot <clem@ltb-project.org> - 2.4.58-1
- Upgrade to OpenLDAP 2.4.58
* Tue Jan 19 2021 - Clement Oudot <clem@ltb-project.org> - 2.4.57-1
- Upgrade to OpenLDAP 2.4.57
* Sun Nov 15 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.56-1
- Upgrade to OpenLDAP 2.4.56
* Fri Oct 30 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.55-1
- Upgrade to OpenLDAP 2.4.55
* Tue Oct 13 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.54-1
- Upgrade to OpenLDAP 2.4.54
* Mon Sep 07 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.53-1
- Upgrade to OpenLDAP 2.4.53
* Sun Sep 06 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.52-1
- Upgrade to OpenLDAP 2.4.52
* Thu Aug 13 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.51-1
- Upgrade to OpenLDAP 2.4.51
* Tue Apr 28 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.50-1
- Upgrade to OpenLDAP 2.4.50
- Add module passwd argon2
* Fri Jan 31 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.49-1
- Upgrade to OpenLDAP 2.4.49
* Thu Jan 16 2020 - Clement Oudot <clem@ltb-project.org> - 2.4.48-3
- Apply patch for ITS#9146
- Apply patch for ITS#9150
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
- Use %%config(noreplace)
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
