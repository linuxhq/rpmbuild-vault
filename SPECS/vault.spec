%define debug_package %{nil}

%define vault_version %{?vault_version_override}%{?!vault_version_override:1.2.1}

%if "%{vault_mode_override}" == "agent"
%define vault_mode agent
%define vault_name_suffix -agent
%else
%define vault_mode server
%define vault_name_suffix %{nil}
%endif

Name:           vault%{vault_name_suffix}
Version:        %{vault_version}
Release:        1%{dist}
Summary:        A tool for managing secrets
License:        Mozilla Public License 2.0
URL:            https://www.vaultproject.io/
%ifarch x86_64 amd64
Source0:        https://releases.hashicorp.com/vault/%{vault_version}/vault_%{vault_version}_linux_amd64.zip
%else
Source0:        https://releases.hashicorp.com/vault/%{vault_version}/vault_%{vault_version}_linux_386.zip
%endif
Source1:        vault.hcl.%{vault_mode}
Source2:        vault.rhel%{rhel}.sysconfig
%if 0%{?rhel} < 7
Source3:        vault.init
Source4:        vault.logrotate
%else
Source3:        vault.service
Source4:        vault.tmpfiles
Source5:        vault.firewalld
%endif
%if 0%{?rhel} >= 7
%if "%{vault_mode}" == "server"
Requires:         firewalld-filesystem
%endif
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
BuildRequires:    systemd-units
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Vault is a tool for securely accessing secrets. A secret is anything that you
want to tightly control access to, such as API keys, passwords, certificates,
and more.
Vault provides a unified interface to any secret, while providing tight access
control and recording a detailed audit log.

%prep
%setup -c
%build
%install
%{__install} -d -m 0755 %{buildroot}%{_sbindir} \
                        %{buildroot}%{_sysconfdir}/%{name} \
                        %{buildroot}%{_sysconfdir}/sysconfig \
                        %{buildroot}%{_localstatedir}/lib/%{name}
%if 0%{?rhel} < 7
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/rc.d/init.d \
                        %{buildroot}%{_sysconfdir}/logrotate.d \
                        %{buildroot}%{_localstatedir}/log/%{name} \
                        %{buildroot}%{_localstatedir}/run/%{name}
%else
%{__install} -d -m 0755 %{buildroot}%{_unitdir} \
                        %{buildroot}%{_rundir}/%{name} \
                        %{buildroot}%{_tmpfilesdir}
%if "%{vault_mode}" == "server"
%{__install} -d -m 0755 %{buildroot}%{_prefix}/lib/firewalld/services
%endif
%endif

%define __sed    sed
%define sed_expr 's/%%{name}/%{name}/g; s/%%{mode}/%{vault_mode}/g'
         
%{__install} -m 0755 vault %{buildroot}%{_sbindir}/%{name}
%{__install} -m 0600 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/%{name}.hcl
%{__sed}     -i %{sed_expr}     %{buildroot}%{_sysconfdir}/%{name}/%{name}.hcl
%{__install} -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__sed}     -i %{sed_expr}     %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%if 0%{?rhel} < 7
%{__install} -m 0755 %{SOURCE3} %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
%{__sed}     -i %{sed_expr}     %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
%{__install} -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__sed}     -i %{sed_expr}     %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%else
%{__install} -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
%{__sed}     -i %{sed_expr}     %{buildroot}%{_unitdir}/%{name}.service
%{__install} -m 0644 %{SOURCE4} %{buildroot}%{_tmpfilesdir}/%{name}.conf
%{__sed}     -i %{sed_expr}     %{buildroot}%{_tmpfilesdir}/%{name}.conf
%if "%{vault_mode}" == "server"
%{__install} -m 0644 %{SOURCE5} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml
%{__sed}     -i %{sed_expr}     %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml
%endif
%endif

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
  useradd -r -g %{name} -s /sbin/nologin \
    -d %{_localstatedir}/lib/%{name} -c "Vault User" %{name}

%post
%if 0%{?systemd_post:1}
    %systemd_post %{name}.service
    %firewalld_reload
    /usr/bin/systemd-tmpfiles --create %{_tmpfilesdir}/%{name}.conf
%else
    /sbin/chkconfig --add %{name}
%endif

%preun
%if 0%{?systemd_preun:1}
    %systemd_preun %{name}.service
%else
    /sbin/service %{name} stop > /dev/null 2>&1
    /sbin/chkconfig --del %{name}
%endif

%postun
%if 0%{?systemd_postun:1}
    %systemd_postun %{name}.service
    %firewalld_reload
%endif
if [ "$1" = "0" ]; then
   userdel --force %{name} 2> /dev/null; true
   groupdel --force %{name} 2> /dev/null; true
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,%{name},%{name},-)
%attr(-,root,root) %{_sbindir}/%{name}
%if 0%{?rhel} < 7
%attr(-,root,root) %{_sysconfdir}/rc.d/init.d/%{name}
%attr(-,root,root) %{_sysconfdir}/logrotate.d/%{name}
%else
%attr(-,root,root) %{_unitdir}/%{name}.service
%attr(-,root,root) %{_tmpfilesdir}/%{name}.conf
%if "%{vault_mode}" == "server"
%attr(-,root,root) %{_prefix}/lib/firewalld/services/%{name}.xml
%endif
%endif
%attr(-,root,root) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.*
%attr(700,%{name},%{name}) %{_localstatedir}/lib/%{name}
%if 0%{?rhel} >= 7
%ghost %attr(755,%{name},%{name}) %{_rundir}/%{name}
%else
%{_localstatedir}/log/%{name}
%{_localstatedir}/run/%{name}
%endif

%changelog
* Mon Oct 14 2019 Elia Pinto <pinto.elia@gmail.com> - 1.2.1-1
- Update to version 1.2.1

* Tue Apr 02 2019 Giuseppe Ragusa <giuseppe.ragusa@fastmail.fm> - 1.1.0-1
- Updated to 1.1.0
- Modified spec to properly support CentOS/RHEL 7
- Small uniformity mods

* Tue Mar 27 2018 Taylor Kimball <tkimball@linuxhq.org> - 0.9.6-1
- Updated to 0.9.6
- Add vault user to runas

* Mon Feb 12 2018 Taylor Kibmall <tkimball@linuxhq.org> - 0.9.3-1
- Updated to 0.9.3

* Mon May 02 2016 Taylor Kimball <tkimball@linuxhq.org> - 0.5.2-1
- Initial build.
