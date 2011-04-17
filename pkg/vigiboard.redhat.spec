%define module  @SHORT_NAME@

%define pyver 26
%define pybasever 2.6
%define __python /usr/bin/python%{pybasever}
%define __os_install_post %{__python26_os_install_post}
%{!?python26_sitelib: %define python26_sitelib %(python26 -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    1%{?svn}%{?dist}
Source0:    %{name}-%{version}.tar.gz
URL:        @URL@
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python26-distribute
BuildRequires:   python26-babel

Requires:   python26-distribute
Requires:   vigilo-turbogears
Requires:   python26-tw-forms
Requires:   mod_wsgi-python26

# Renommage
Obsoletes: vigiboard < 1.0-1
Provides:  vigiboard = %{version}-%{release}


%description
@DESCRIPTION@
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q
# A cause des permissions sur /var/log/httpd sur Red Hat
sed -i -e '/<IfModule mod_wsgi\.c>/a WSGISocketPrefix run/wsgi' deployment/%{module}.conf

%build

%install
rm -rf $RPM_BUILD_ROOT
make install_pkg \
	DESTDIR=$RPM_BUILD_ROOT \
	SYSCONFDIR=%{_sysconfdir} \
	PYTHON=%{__python}

# %find_lang %{name} # ne fonctionne qu'avec les fichiers dans /usr/share/locale/


%post
/sbin/service httpd condrestart > /dev/null 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING.txt README.txt
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%config(noreplace) %attr(640,root,apache) %{_sysconfdir}/vigilo/%{module}/*.ini
%ghost %{_sysconfdir}/vigilo/%{module}/*.pyo
%ghost %{_sysconfdir}/vigilo/%{module}/*.pyc
%{_sysconfdir}/httpd/conf.d/%{module}.conf
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{module}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%{python26_sitelib}/*
