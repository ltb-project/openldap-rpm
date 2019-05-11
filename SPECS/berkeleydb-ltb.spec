#=================================================
# Specification file for BerkeleyDB
#
# Install BerkeleyDB
# Modify /etc/ld.so.conf
#
# Copyright (C) 2008-2019 Clement OUDOT
# Copyright (C) 2018-2019 Worteks
# Copyright (C) 2008 Raphael Ouazana
# Copyright (C) 2008 LINAGORA
#
# LTB project (http://www.ltb-project.org)
#=================================================

#=================================================
# Variables
#=================================================

%define real_name db

%define bdbdir	/usr/local/berkeleydb

#=================================================
# Header
#=================================================
Summary: Sleepycat Database Software - Berkeley Database
Name: berkeleydb-ltb
Version: 4.6.21.NC
Release: 4%{?dist}.patch4
# http://www.oracle.com/technology/software/products/berkeley-db/htdocs/oslicense.html
License: Open Source License for Berkeley DB

Group: Applications/System
URL: http://www.oracle.com/technology/products/berkeley-db/db/index.html

Source: %{real_name}-%{version}.tar.gz
Source1: berkeleydb.sh
Patch1: patch.4.6.21.1
Patch2: patch.4.6.21.2
Patch3: patch.4.6.21.3
Patch4: patch.4.6.21.4
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: gcc, make

Requires(pre): /sbin/ldconfig, coreutils

%description
Berkeley DB, the most widely-used developer database in the world, is open
source and runs on all major operating systems, including embedded Linux,
Linux, MacOS X, QNX, UNIX, VxWorks and Windows.

Berkeley DB delivers the core data management functionality, power, scalability
and flexibility of enterprise relational databases but without the overhead
of a query processing layer.

#=================================================
# Source preparation
#=================================================
%prep
%setup -n %{real_name}-%{version}

%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0

#=================================================
# Building
#=================================================
%build
cd build_unix
export CC=gcc
../dist/configure --prefix=%{bdbdir} --libdir=%{bdbdir}/%{_lib}
make %{?_smp_mflags}

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}
cd build_unix
make install DESTDIR=%{buildroot}

# PATH modification
mkdir -p %{buildroot}/etc/profile.d
install -m 755 %{SOURCE1} %{buildroot}/etc/profile.d/
sed -i 's:^BDB_BIN.*:BDB_BIN='%{bdbdir}/bin':' %{buildroot}/etc/profile.d/berkeleydb.sh

#=================================================
# Post Installation
#=================================================
%post
# Don't do this if older version is installed
if [ $1 -eq 1 ]
then
	# Add BerkeleyDB libraries to the system
	echo "%{bdbdir}/%{_lib}" >> /etc/ld.so.conf
	/sbin/ldconfig
fi

#=================================================
# Pre uninstallation
#=================================================
%preun
# Don't do this if newer version is installed
if [ $1 -eq 0 ]
then
	# Remove BerkeleyDB libraries from the system
	sed -i '\:'%{bdbdir}/%{_lib}':d' /etc/ld.so.conf
	/sbin/ldconfig
fi

#=================================================
# Files
#=================================================
%files
%defattr(-, root, root, 0755)
%doc %{bdbdir}/docs
%dir %{bdbdir}
%{bdbdir}/bin
%{bdbdir}/include
%{bdbdir}/%{_lib}
/etc/profile.d/berkeleydb.sh

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 2 2009 - Clement Oudot <clem@ltb-project.org> - 4.6.21-4
- Add patch 4
* Mon Mar 2 2009 - Clement Oudot <clem@ltb-project.org> - 4.6.21-3
- This package is now maintained in LTB project
* Thu Jan 15 2009 - Clement Oudot <clement.oudot@linagora.com> - 4.6.21-2
- use real_name variable
- update URL to Oracle Website
* Fri Oct 24 2008 - Clement Oudot <clement.oudot@linagora.com> - 4.6.21-2
- install in /opt
- update PATH
* Mon Oct 20 2008 - Clement Oudot <clement.oudot@linagora.com> - 4.6.21-1
- new version 4.6.21 + patchs for RHEL/CentOS 5
* Thu Sep 28 2006 - Raphael Ouazana <raphael.ouazana@linagora.com> - 4.2.52-2
- new version
* Fri Aug 26 2005 - Clement Oudot <clement.oudot@linagora.com> - 4.2.52-1
- package for RHEL3 ES UP5
