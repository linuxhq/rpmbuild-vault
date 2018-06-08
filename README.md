# rpmbuild-vault

[![Package Cloud](https://img.shields.io/badge/packagecloud-vault-blue.svg?style=flat)](https://packagecloud.io/linuxhq/vault)
[![License](https://img.shields.io/badge/license-GPLv3-brightgreen.svg?style=flat)](COPYING)

Create a vault RPM for RHEL/CentOS.

## Requirements

To download package sources and install build dependencies

    sudo yum -y install mock rpmdevtools
    sudo usermod -a -G mock $(whoami)

## Build process

To build the package follow the steps outlined below

    source /etc/os-release
    tmp=$(mktemp -d)

    git clone https://github.com/linuxhq/rpmbuild-vault.git ${tmp}
    mkdir -p ${tmp}/{SOURCES,SRPMS}
    spectool -g -C ${tmp}/SOURCES ${tmp}/SPECS/*.spec

    mock --clean \
         --root epel-${VERSION_ID}-$(uname -i)

    mock --buildsrpm \
         --cleanup-after \
         --resultdir ${tmp}/SRPMS \
         --root epel-${VERSION_ID}-$(uname -i) \
         --sources ${tmp}/SOURCES \
         --spec ${tmp}/SPECS/*.spec

    mock --rebuild \
         --root epel-${VERSION_ID}-$(uname -i) \
         ${tmp}/SRPMS/*.src.rpm

    rm -rf ${tmp}

## Partners

[![packagecloud](http://dka575ofm4ao0.cloudfront.net/pages-transactional_logos/retina/10543/gKme3F4XRaC5EyKJzKsA)](https://packagecloud.io)

Do you need trustworthy hosted package repositories?  Then packagecloud is for you.

A big thank you to packagecloud for supporting the open source community!

## License

Copyright (C) 2018 Taylor Kimball <tkimball@linuxhq.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
