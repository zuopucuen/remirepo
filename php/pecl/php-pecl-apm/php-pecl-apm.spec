# spec file for php-pecl-apm
#
# Copyright (c) 2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%{?scl:          %scl_package        php-pecl-apm}
%{!?scl:         %global pkg_name    %{name}}
%{!?scl:         %global _root_sysconfdir %{_sysconfdir}}
%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?php_incldir: %global php_incldir %{_includedir}/php}
%{!?__pecl:      %global __pecl      %{_bindir}/pecl}
%{!?__php:       %global __php       %{_bindir}/php}
%global pecl_name apm
%global proj_name APM
# https://github.com/patrickallaert/php-apm/issues/13
%global with_zts  0
%if "%{php_version}" < "5.6"
# after json.ini
%global ini_name  z-%{pecl_name}.ini
%else
# after 40-json.ini
%global ini_name  50-%{pecl_name}.ini
%endif
%if 0%{?fedora} >= 21
# support for apache / nginx / php-fpm
%global with_phpfpm 1
%else
%global with_phpfpm 0
%endif
%if 0%{?fedora} >= 11 || 0%{?rhel} >= 6
%global with_sqlite 1
%else
%global with_sqlite 0
%endif


Name:           %{?scl_prefix}php-pecl-apm
Summary:        Alternative PHP Monitor
Version:        2.0.0
Release:        2%{?dist}%{!?nophptag:%(%{__php} -r 'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')}
Source0:        http://pecl.php.net/get/%{proj_name}-%{version}.tgz

# Webserver configuration files
Source1:        %{pkg_name}.httpd
Source2:        %{pkg_name}.nginx

License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/%{proj_name}

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  %{?scl_prefix}php-devel
BuildRequires:  %{?scl_prefix}php-pear
BuildRequires:  %{?scl_prefix}php-json
%if %{with_sqlite}
BuildRequires:  sqlite-devel >= 3.6
%endif
BuildRequires:  mysql-devel
BuildRequires:  zlib-devel

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}
Requires:       %{?scl_prefix}php-json%{?_isa}
%{?_sclreq:Requires: %{?scl_prefix}runtime%{?_sclreq}%{?_isa}}

Provides:       %{?scl_prefix}php-%{pecl_name} = %{version}
Provides:       %{?scl_prefix}php-%{pecl_name}%{?_isa} = %{version}
Provides:       %{?scl_prefix}php-pecl(%{proj_name}) = %{version}
Provides:       %{?scl_prefix}php-pecl(%{proj_name})%{?_isa} = %{version}

%if "%{?vendor}" == "Remi Collet" && 0%{!?scl:1}
# Other third party repo stuff
Obsoletes:     php53-pecl-%{pecl_name}  <= %{version}
Obsoletes:     php53u-pecl-%{pecl_name} <= %{version}
Obsoletes:     php54-pecl-%{pecl_name}  <= %{version}
Obsoletes:     php54w-pecl-%{pecl_name} <= %{version}
%if "%{php_version}" > "5.5"
Obsoletes:     php55u-pecl-%{pecl_name} <= %{version}
Obsoletes:     php55w-pecl-%{pecl_name} <= %{version}
%endif
%if "%{php_version}" > "5.6"
Obsoletes:     php56u-pecl-%{pecl_name} <= %{version}
Obsoletes:     php56w-pecl-%{pecl_name} <= %{version}
%endif
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
Monitoring extension for PHP, collects error events and statistics and send
them to one of his drivers:

* StatsD driver sends them to StatsD using UDP.

* Socket driver sends them via UDP or TCP socket using its dedicated protocol.
%if %{with_sqlite}
* SQLite and MariaDB/MySQL drivers are storing those in a database.
%else
* MariaDB/MySQL drivers are storing those in a database.
%endif

The optional %{?scl_prefix}apm-web package provides the web application.

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection}.


%package -n %{?scl_prefix}apm-web
Summary:       Alternative PHP Monitor web application
Group:         Applications/Internet
%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
BuildArch:     noarch
%endif
%if %{with_phpfpm}
Requires:      webserver
Requires:      nginx-filesystem
Requires:      httpd-filesystem
Requires:      php(httpd)
%else
Requires:      httpd
Requires:      mod_php
%endif
# From phpcompatinfo report
Requires:      %{?scl_prefix}php-date
Requires:      %{?scl_prefix}php-json
Requires:      %{?scl_prefix}php-pcre
Requires:      %{?scl_prefix}php-pdo


%description -n %{?scl_prefix}apm-web
This package provides the APM (Alternative PHP Monitor) web
application, with Apache%{?with_phpfpm: and Nginx} configuration,
available on http://localhost/%{?scl_prefix}apm-web/

The optional %{?scl_prefix}php-pecl-apm package provides the extension.


%prep
%setup -qc
mv %{proj_name}-%{version} NTS

# Don't install/register tests
# https://github.com/patrickallaert/php-apm/issues/12
sed -e 's/role="test"/role="src"/' \
    -e 's/role="data"/role="src"/' \
    -e 's/role="php"/role="src"/' \
    -i package.xml

cd NTS
# https://github.com/patrickallaert/php-apm/issues/11
sed -e '/APM_VERSION/s/1.2.0alpha1/%{version}/' -i apm.c

# Sanity check, really often broken
extver=$(sed -n '/#define APM_VERSION/{s/.* "//;s/".*$//;p}' apm.c)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}.
   exit 1
fi

: Fix configuration path
sed -e 's:"config/db.php":"%{_sysconfdir}/apm-web/db.php":' \
    -i web/model/repository.php
: Disable the ext
sed -e 's/; apm.enabled="1"/apm.enabled="0"/' \
    -i apm.ini
cd ..

%if %{with_zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif

: Create webserver configuration files
sed -e 's:@ALIAS@:%{?scl_prefix}apm-web:g' \
    -e 's:@SHARE@:%{_datadir}:g' \
    %{SOURCE1} | tee %{name}.httpd

sed -e 's:@ALIAS@:%{?scl_prefix}apm-web:g' \
    -e 's:@SHARE@:%{_datadir}:g' \
    %{SOURCE2} | tee %{name}.nginx


%build
peclconf() {
%configure \
  --enable-apm \
%if %{with_sqlite}
  --with-sqlite3 \
%else
  --without-sqlite3 \
%endif
  --with-mysql \
  --enable-statsd \
  --enable-socket \
  --with-libdir=%{_lib} \
  --with-php-config=$1
}
cd NTS
%{_bindir}/phpize
peclconf %{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
peclconf %{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
rm -rf %{buildroot}

# Install the NTS stuff
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 NTS/apm.ini %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
# Install the ZTS stuff
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 ZTS/apm.ini %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Install the web application
mv NTS/web/config config

install -d %{buildroot}%{_datadir}
cp -pr NTS/web %{buildroot}%{_datadir}/%{?scl_prefix}apm-web

# Apache config
install -D -m 644 %{name}.httpd \
        %{buildroot}%{_root_sysconfdir}/httpd/conf.d/%{?scl_prefix}apm-web.conf

# Nginx config
%if %{with_phpfpm}
install -Dpm 0644 %{name}.nginx \
        %{buildroot}/%{_root_sysconfdir}/nginx/default.d/%{?scl_prefix}apm-web.conf
%endif

# Application config
install -D -m 644 -p config/db.php \
         %{buildroot}%{_sysconfdir}/apm-web/db.php

cd NTS
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{proj_name}/$i
done


%check
cd NTS

opt="--no-php-ini --define apm.enabled=0"
if [ -f %{php_extdir}/json.so ]; then
  opt="$opt --define extension=json.so"
fi

: Minimal load test for NTS extension
%{__php} $opt \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

%if %{with_zts}
cd ../ZTS
: Minimal load test for ZTS extension
%{__ztsphp} --no-php-ini \
    $dep \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}
%endif


%clean
rm -rf %{buildroot}


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{proj_name} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%doc %{pecl_docdir}/%{proj_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%{php_ztsextdir}/%{pecl_name}.so
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%endif


%files -n %{?scl_prefix}apm-web
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license NTS/LICENSE
# Need to restrict access, as it contains a clear password
%attr(750,root,apache) %dir %{_sysconfdir}/apm-web
%attr(640,root,apache) %config(noreplace) %{_sysconfdir}/apm-web/db.php
%{_datadir}/%{?scl_prefix}apm-web
%config(noreplace) %{_root_sysconfdir}/httpd/conf.d/%{?scl_prefix}apm-web.conf
%if %{with_phpfpm}
%config(noreplace) %{_root_sysconfdir}/nginx/default.d/%{?scl_prefix}apm-web.conf
%endif


%changelog
* Sat Feb 21 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-2
- add missing dependencies
- drop dependency between extension and webapp
- move configuration to /etc/apm-web
- fix permission of configuration file

* Sat Feb 21 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-1
- initial package, version 2.0.0
- open upstream bugs:
  https://github.com/patrickallaert/php-apm/issues/10 - configure
  https://github.com/patrickallaert/php-apm/issues/11 - bad version
  https://github.com/patrickallaert/php-apm/issues/12 - bad roles
  https://github.com/patrickallaert/php-apm/issues/13 - zts broken