# spec file for php-twig-ctwig
#
# Copyright (c) 2013 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%{!?php_inidir: %global php_inidir  %{_sysconfdir}/php.d}
%{!?__pecl:     %global __pecl      %{_bindir}/pecl}

%global with_zts     0%{?__ztsphp:1}
%global pecl_name    CTwig
%global ext_name     twig
%global pecl_channel pear.twig-project.org

Summary:        Extension to improve performance of Twig
Name:           php-twig-ctwig
Version:        1.14.1
Release:        3%{?dist}
License:        BSD
Group:          Development/Languages
URL:            http://twig.sensiolabs.org
Source0:        http://%{pecl_channel}/get/%{pecl_name}-%{version}.tgz

BuildRequires:  php-devel >= 5.2.4
BuildRequires:  php-pear
BuildRequires:  php-channel(%{pecl_channel})

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
Requires:       php-channel(%{pecl_channel})

Provides:       php-%{ext_name} = %{version}
Provides:       php-%{ext_name}%{?_isa} = %{version}
Provides:       php-pecl(%{pecl_channel}/%{pecl_name}) = %{version}
Provides:       php-pecl(%{pecl_channel}/%{pecl_name})%{?_isa} = %{version}
# Package have been renamed
Obsoletes:      php-twig-CTwig < 1.14.1-2
Provides:       php-twig-CTwig = %{version}-%{release}

%if 0%{?fedora} < 20
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
Twig is a PHP template engine.

This package provides the Twig C extension (CTwig) to improve performance
of the Twig template language, used by Twig PHP extension (php-twig-Twig).


%prep
%setup -q -c
mv %{pecl_name}-%{version} NTS

%if %{with_zts}
# Duplicate source tree for NTS / ZTS build
cp -pr NTS ZTS
%endif

# Create configuration file
cat > %{ext_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension=%{ext_name}.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure \
    --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure \
    --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# install config file
install -D -m 644 %{ext_name}.ini %{buildroot}%{php_inidir}/%{ext_name}.ini

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}

install -D -m 644 %{ext_name}.ini %{buildroot}%{php_ztsinidir}/%{ext_name}.ini
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_channel}/%{pecl_name} >/dev/null || :
fi


%check
: Minimal load test for NTS extension
%{_bindir}/php --no-php-ini \
    --define extension=NTS/modules/%{ext_name}.so \
    --modules | grep %{ext_name}

%if %{with_zts}
: Minimal load test for ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=ZTS/modules/%{ext_name}.so \
    --modules | grep %{ext_name}
%endif


%files
%doc NTS/LICENSE
%{pecl_xmldir}/%{name}.xml
%config(noreplace) %{php_inidir}/%{ext_name}.ini
%{php_extdir}/%{ext_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ext_name}.ini
%{php_ztsextdir}/%{ext_name}.so
%endif


%changelog
* Mon Oct 21 2013 Remi Collet <remi@fedoraproject.org> - 1.14.1-3
- cleanup for review, drop SCL and EL-5 support

* Fri Oct 18 2013 Remi Collet <remi@fedoraproject.org> - 1.14.1-2
- rename from php-twig-CTwig to php-twig-ctwig

* Wed Oct 16 2013 Remi Collet <remi@fedoraproject.org> - 1.14.1-1
- Update to 1.14.1 (no change, only version bump)

* Sat Oct  5 2013 Remi Collet <rcollet@redhat.com> - 1.14.0-1
- adapt for SCL

* Thu Oct  3 2013 Remi Collet <remi@fedoraproject.org> - 1.14.0-1
- initial package