%global github_owner    natxet
%global github_name     CssMin
%global github_version  3.0.2
%global github_commit   8883d28cd2de131c364f2f657e4bcc09bfa45082
# if set, will be a post-release snapshot build, otherwise a 'normal' build
%global github_date     20141229
%global shortcommit %(c=%{github_commit}; echo ${c:0:7})
%global packagist_owner natxet
%global packagist_name  CssMin

%global lcname  %(echo %{packagist_name} | tr '[:upper:]' '[:lower:]')

# phpci
%global php_min_ver    5.0.0

Name:           php-%{packagist_owner}-%{lcname}
Version:        %{github_version}
Release:        2%{?github_date:.%{github_date}git%{shortcommit}}%{?dist}
Summary:        Configurable CSS parser and minifier

Group:          Development/Libraries
# License text is included in the sole code file
License:        MIT
URL:            https://github.com/%{github_owner}/%{github_name}
# Must use commit-based not tag-based github tarball:
# https://fedoraproject.org/wiki/Packaging:SourceURL#Github
Source0:        https://github.com/%{github_owner}/%{github_name}/archive/%{github_commit}/%{github_name}-%{github_commit}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       php(language) >= %{php_min_ver}
Requires:       php-pcre

Provides:       php-composer(%{packagist_owner}/%{packagist_name}) = %{version}


%description
CssMin is a css parser and minifier. It minifies css by removing
unneeded whitespace characters, comments, empty blocks and empty
declarations. In addition declaration values can get rewritten to
shorter notation if available. The minification is configurable. 


%prep
%setup -qn %{github_name}-%{github_commit}


%build
# Empty build section, nothing required


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_datadir}/php/%{packagist_owner}/%{packagist_name}
cp -pr src/ %{buildroot}%{_datadir}/php/%{packagist_owner}/%{packagist_name}


%clean
rm -rf %{buildroot}


%check
# no tests


%files
%defattr(-,root,root,-)
%doc README composer.json
%{_datadir}/php/%{packagist_owner}


%changelog
* Tue Feb 24 2015 Remi Collet <remi@fedoraproject.org> - 3.0.2-2.20141229git8883d28
- add backport stuff for remi repo

* Mon Feb 23 2015 Adam Williamson <awilliam@redhat.com> - 3.0.2-2.20141229git8883d28
- change layout to match upstream's (with the /src sub-directory)

* Mon Dec 29 2014 Adam Williamson <awilliam@redhat.com> - 3.0.2-1.20141229git8883d28
- initial package
