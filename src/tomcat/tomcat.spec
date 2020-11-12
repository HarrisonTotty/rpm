# Apache Tomcat SPEC File
# -----------------------
# Based On: https://gitlab.com/harbottle/harbottle-main/-/blob/master/specs/tomcat9.spec
# Notes:
#   - We don't specify `Requires` because the OpenJDK packages from EPEL don't
#     specify `Provides: java`.
#   - We keep everything contained within /www/tomcat/base/

%global homedir /www/%{name}/base/%{version}
%global tomcat_user %{name}
%global tomcat_group %{name}

# ---------- Preamble ----------

Name:             tomcat
Summary:          Apache Tomcat (Version 9)
Version:          9.0.38
Release:          1.el8
Source0:          http://www-us.apache.org/dist/tomcat/tomcat-9/v%{version}/bin/apache-tomcat-%{version}.tar.gz
Source1:          tomcat.conf
Source2:          tomcat.service
Group:            Applications/System
License:          Apache-2.0
URL:              https://tomcat.apache.org/
BuildRequires:    systemd-units
Provides:         tomcat
Requires(pre):    shadow-utils
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units


# ---------- Description ----------

%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Sun under the Java Community Process.

Tomcat is developed in an open and participatory environment and
released under the Apache Software License version 2.0. Tomcat is intended
to be a collaboration of the best-of-breed developers from around the world.

%package admin-webapps
Group: Applications/System
Summary: The host-manager and manager web applications for Apache Tomcat
Requires: %{name} = %{version}-%{release}

%description admin-webapps
The host-manager and manager web applications for Apache Tomcat.

%package docs-webapp
Group: Applications/Text
Summary: The docs web application for Apache Tomcat
Requires: %{name} = %{version}-%{release}

%description docs-webapp
The docs web application for Apache Tomcat.

%package webapps
Group:    Applications/Internet
Summary:  The ROOT and examples web applications for Apache Tomcat
Requires: %{name} = %{version}-%{release}

%description webapps
The ROOT and examples web applications for Apache Tomcat.


# ---------- Installation ----------

%prep
%setup -qn apache-tomcat-%{version}

%install
rm -f bin/*.bat
sed -i -e '/^2localhost/d' -e '/\[\/localhost\]/d' \
    -e '/^3manager/d' -e '/\[\/manager\]/d' \
    -e '/^4host-manager/d' -e '/\[\/host-manager\]/d' \
    -e 's/, *4host-manager.org.apache.juli.AsyncFileHandler//' \
    -e 's/, *3manager.org.apache.juli.AsyncFileHandler//' \
    conf/logging.properties
install -d -m 755 $RPM_BUILD_ROOT%{homedir}
install -d -m 755 $RPM_BUILD_ROOT%{_unitdir}

mv bin $RPM_BUILD_ROOT%{homedir}/bin
mv conf $RPM_BUILD_ROOT%{homedir}/conf
mv lib $RPM_BUILD_ROOT%{homedir}/lib
mv logs $RPM_BUILD_ROOT%{homedir}/logs
mv temp $RPM_BUILD_ROOT%{homedir}/temp
mv work $RPM_BUILD_ROOT%{homedir}/work
mv webapps $RPM_BUILD_ROOT%{homedir}/webapps

install -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{homedir}/conf/%{name}.conf
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/%{name}.service

%pre
getent group %{tomcat_group} >/dev/null || groupadd -g 91 -f -r %{tomcat_group}
getent passwd %{tomcat_user} >/dev/null || useradd -r -u 91 -g %{tomcat_group} -d /www/%{name}/home -s /bin/sh -c "Apache Tomcat" %{tomcat_user}
exit 0

%post
ln -sf %{homedir} /www/%{name}/base/current
%systemd_post %{name}.service


# ---------- Uninstallation ----------

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


# ---------- Files ----------

%files
%attr(-,root,tomcat) %dir %{homedir}
%attr(-,root,tomcat) %{homedir}/bin
%attr(0770,root,tomcat) %dir %{homedir}/conf
%config(noreplace) %attr(0740,root,tomcat) %{homedir}/conf/*
%attr(-,root,tomcat) %{homedir}/lib
%attr(-,tomcat,tomcat) %{homedir}/logs
%attr(-,tomcat,tomcat) %{homedir}/temp
%attr(-,tomcat,tomcat) %dir %{homedir}/webapps
%attr(-,tomcat,tomcat) %{homedir}/work
%{_unitdir}/%{name}.service

%files admin-webapps
%defattr(0664,root,tomcat,0755)
%{homedir}/webapps/host-manager
%{homedir}/webapps/manager
%config(noreplace) %{homedir}/webapps/host-manager/WEB-INF/web.xml
%config(noreplace) %{homedir}/webapps/manager/WEB-INF/web.xml

%files docs-webapp
%defattr(-,root,root,-)
%{homedir}/webapps/docs

%files webapps
%defattr(0644,tomcat,tomcat,0755)
%{homedir}/webapps/ROOT
%{homedir}/webapps/examples


# ---------- Changelog ----------

%changelog
* Tue Sep 22 2020 - harrisongtotty@gmail.com - 9.0.38-1
  - Fix tomcat user/group id to be 91
  - Bump version
* Wed Sep 09 2020 - harrisongtotty@gmail.com - 9.0.37-4
  - Switch to keeping all files in homedir without symlinks
  - Create symlink for current -> version
* Wed Sep 09 2020 - harrisongtotty@gmail.com - 9.0.37-3
  - Separate out tomcat user and group name
* Wed Sep 09 2020 - harrisongtotty@gmail.com - 9.0.37-2
  - Change base directory to /www/tomcat/base/VERSION
  - Remove documentation files
* Tue Sep 08 2020 - harrisongtotty@gmail.com - 9.0.37-1
  - Initial package creation
