%global majorversion 2.1
%global libeventprefix /usr/local/%{name}-%{majorversion}
%global libeventlibprefix %{libeventprefix}/lib
%global libeventincludeprefix %{libeventprefix}/include
%global libeventbinprefix %{libeventprefix}/bin
%global libeventshareprefix %{libeventprefix}/share
%global libeventdocprefix %{libeventshareprefix}/doc

Name:           libevent-ltb
Version:        2.1.12
Release:        1%{?dist}
Summary:        Abstract asynchronous event notification library

# arc4random.c, which is used in build, is ISC. The rest is BSD.
License:        BSD and ISC
URL:            http://libevent.org/
Source0:        https://github.com/libevent/libevent/releases/download/release-%{version}-stable/libevent-%{version}-stable.tar.gz

BuildRequires: openssl-devel
BuildRequires: python3-devel

%description
The libevent API provides a mechanism to execute a callback function
when a specific event occurs on a file descriptor or after a timeout
has been reached. libevent is meant to replace the asynchronous event
loop found in event driven network servers. An application just needs
to call event_dispatch() and can then add or remove events dynamically
without having to change the event loop.

%package devel
Summary: Development files for %{name}
License: BSD
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains the header files and libraries for developing
with %{name}.

%prep
%setup -q -n libevent-%{version}-stable

%build
./configure --build=x86_64-redhat-linux-gnu --host=x86_64-redhat-linux-gnu --disable-dependency-tracking --disable-static --prefix=%{libeventprefix}
make %{?_smp_mflags} all

%install
make DESTDIR=$RPM_BUILD_ROOT install
mkdir -p %{buildroot}/%{libeventdocprefix}
cp LICENSE ChangeLog %{buildroot}/%{libeventdocprefix}/


%check
#make check

%files
%license %{libeventdocprefix}/LICENSE
%doc %{libeventdocprefix}/ChangeLog
%{libeventlibprefix}/libevent*

%files devel
%{libeventincludeprefix}
%{libeventlibprefix}/pkgconfig
%{libeventbinprefix}


%post
echo "%{libeventlibprefix}" > /etc/ld.so.conf.d/%{name}-%{majorversion}.conf
/usr/sbin/ldconfig

%preun
rm /etc/ld.so.conf.d/%{name}-%{majorversion}.conf
/usr/sbin/ldconfig


%changelog
* Thu Sep 09 2021 David Coutadeur <david.coutadeur@gmail.com> - 2.1.12
- package first libevent-ltb 2.1.12 version
- remove documentation (not provided any more by libevent team, only html files)

