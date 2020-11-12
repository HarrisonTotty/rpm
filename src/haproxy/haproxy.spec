# HAProxy SPEC File
# -----------------

%global haproxy_user haproxy
%global haproxy_group %{haproxy_user}
%global haproxy_home_dir /var/lib/haproxy
%global haproxy_conf_dir /etc/haproxy
%global maj_ver 2.2
%global min_ver 4

# ---------- Preamble ----------

Name:             haproxy
Summary:          The Reliable, High Performance TCP/HTTP Load Balancer
Version:          %{maj_ver}.%{min_ver}
Release:          1.el8
Source0:          http://www.haproxy.org/download/%{maj_ver}/src/haproxy-%{maj_ver}.%{min_ver}.tar.gz
Source1:          haproxy.cfg
Source2:          haproxy.service
Group:            Applications/System
License:          GPLv2+
URL:              http://www.haproxy.org/
Provides:         haproxy
BuildRequires:    gcc
BuildRequires:    make
BuildRequires:    openssl-devel
BuildRequires:    pcre-devel
BuildRequires:    systemd-devel
BuildRequires:    systemd-units
BuildRequires:    zlib-devel
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd


# ----------- Description ----------

%description
HAProxy is a free, very fast and reliable solution offering high availability,
load balancing, and proxying for TCP and HTTP-based applications. It is
particularly suited for very high traffic web sites and powers quite a number of
the world's most visited ones. Over the years it has become the de-facto
standard opensource load balancer, is now shipped with most mainstream Linux
distributions, and is often deployed by default in cloud platforms. Since it does
not advertise itself, we only know it's used when the admins report it.


# ---------- Setup/Build ----------

%prep
%setup -q

%define __perl_requires /bin/true
%define debug_package %{nil}

%build
make clean

make -j $(nproc) \
    TARGET=linux-glibc \
    USE_CRYPT_H=1 \
    USE_GETADDRINFO=1 \
    USE_OPENSSL=1 \
    USE_PCRE=1 \
    USE_PCRE_JIT=1 \
    USE_SYSTEMD=1 \
    USE_THREAD=1 \
    USE_ZLIB=1

# ---------- Installation ----------

%install
make install-bin install-man DESTDIR=$RPM_BUILD_ROOT PREFIX=/usr

install -d -m 755 $RPM_BUILD_ROOT%{haproxy_home_dir}

install -d -m 755 $RPM_BUILD_ROOT%{haproxy_conf_dir}
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{haproxy_conf_dir}/haproxy.cfg

install -d -m 755 $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/%{name}.service

%pre
getent group %{haproxy_group} >/dev/null || groupadd -f -r %{haproxy_group}
getent passwd %{haproxy_user} >/dev/null || useradd -r -g %{haproxy_group} -d %{haproxy_home_dir} -s /sbin/nologin -c "HAProxy" %{haproxy_user}
exit 0

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

# ---------- Files ----------

%files
%attr(-,root,haproxy) %dir %{haproxy_home_dir}
%dir %{haproxy_conf_dir}
%attr(0755,root,root) /usr/sbin/haproxy
%config(noreplace) %{haproxy_conf_dir}/haproxy.cfg
%attr(0644,root,root) %doc /usr/share/man/man1/haproxy.1.gz
%{_unitdir}/%{name}.service

# ---------- Changelog ----------

%changelog
* Tue Nov 03 2020 - harrisongtotty@gmail.com - 2.2.4-1
  - Initial package creation
