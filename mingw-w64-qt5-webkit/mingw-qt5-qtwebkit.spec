%?mingw_package_header

%global qt_module qtwebkit

#%%global pre beta1

#%%global snapshot_date 20121130
#%%global snapshot_rev 3c213ae3

%if 0%{?snapshot_date}
%global source_folder qtwebkit-qt5-module
%else
%global source_folder %{qt_module}-opensource-src-%{version}%{?pre:-%{pre}}
%endif

# first two digits of version
%global release_version %(echo %{version} | awk -F. '{print $1"."$2}')

Name:           mingw-qt5-%{qt_module}
Version:        5.1.1
Release:        1%{?pre:.%{pre}}%{?snapshot_date:.git%{snapshot_date}.%{snapshot_rev}}%{?dist}
Summary:        Qt5 for Windows - QtWebKit component

License:        GPLv3 with exceptions or LGPLv2 with exceptions
Group:          Development/Libraries
URL:            http://qt-project.org/

%if 0%{?snapshot_date}
# To regenerate:
# wget http://qt.gitorious.org/qtwebkit/qt5-module/archive-tarball/%{snapshot_rev} -O qt5-qtwebkit-%{snapshot_rev}.tar.gz
Source0:        qt5-%{qt_module}-%{snapshot_rev}.tar.gz
%else
Source0:        http://download.qt-project.org/official_releases/qt/%{release_version}/%{version}/submodules/%{qt_module}-opensource-src-%{version}%{?pre:-%{pre}}.tar.xz
%endif

BuildArch:      noarch

BuildRequires:  mingw32-filesystem >= 96
BuildRequires:  mingw32-gcc-c++
BuildRequires:  mingw32-qt5-qtbase
BuildRequires:  mingw32-qt5-qtdeclarative
BuildRequires:  mingw32-qt5-qtsensors
BuildRequires:  mingw32-qt5-qtlocation
BuildRequires:  mingw32-qt5-qtmultimedia
BuildRequires:  mingw32-angleproject >= 0-0.5.svn2215.20130517
BuildRequires:  mingw32-fontconfig
BuildRequires:  mingw32-libpng
BuildRequires:  mingw32-libjpeg-turbo
BuildRequires:  mingw32-libxslt
BuildRequires:  mingw32-zlib
BuildRequires:  mingw32-icu
BuildRequires:  mingw32-pkg-config
BuildRequires:  mingw32-sqlite
BuildRequires:  mingw32-libwebp

BuildRequires:  mingw64-filesystem >= 96
BuildRequires:  mingw64-gcc-c++
BuildRequires:  mingw64-qt5-qtbase
BuildRequires:  mingw64-qt5-qtdeclarative
BuildRequires:  mingw64-qt5-qtsensors
BuildRequires:  mingw64-qt5-qtlocation
BuildRequires:  mingw64-qt5-qtmultimedia
BuildRequires:  mingw64-angleproject >= 0-0.5.svn2215.20130517
BuildRequires:  mingw64-fontconfig
BuildRequires:  mingw64-libpng
BuildRequires:  mingw64-libjpeg-turbo
BuildRequires:  mingw64-libxslt
BuildRequires:  mingw64-zlib
BuildRequires:  mingw64-icu
BuildRequires:  mingw64-pkg-config
BuildRequires:  mingw64-sqlite
BuildRequires:  mingw64-libwebp

BuildRequires:  python
BuildRequires:  ruby
BuildRequires:  gperf
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  perl-version
BuildRequires:  perl-Digest-MD5

# The ICU libraries used for cross-compilation are named exactly the same as their native Linux counterpart
Patch0:         qt5-qtwebkit-use-correct-icu-libs.patch

# By default the build system assumes that pkg-config isn't used for the win32 target
# However, we're using it in the Fedora MinGW toolchain so make sure it is used automatically
Patch2:         qt5-qtwebkit-enable-pkgconfig-support-for-win32-target.patch

# Make sure the bundled copy of the ANGLE library isn't used
Patch3:         qtwebkit-dont-use-bundled-angle-libraries.patch

# qtwebkit depends on qtbase with ICU support.
# As ICU support in qtbase also introduces over 20MB of additional dependency
# bloat (and the qtbase libraries itself are only 13MB) the decision was made
# to build qtbase without ICU support.
# Make sure qtwebkit doesn't depend on a qtbase with ICU support any more
Patch4:         qt5-qtwebkit-dont-depend-on-icu.patch

# WebKit svn commit 136242 implemented a split into QtWebKit and QtWebKitWidgets
# Due to this change a static library named WebKit1.a is created first.
# After this a shared library is created named Qt5WebKit.dll which contains
# the contents of this static library and some other object files.
# However, various symbols in the static library are expected to be exported
# in the Qt5WebKit.dll shared library. As static libraries normally don't care
# about exported symbols (everything is exported after all) the decoration
# attribute Q_DECL_EXPORT won't be set.
# This results in undefined references when trying to link the QtWebKitWidgets
# shared library (which depends on various symbols which aren't exported properly
# in the Qt5WebKit.dll shared library)
Patch6:         qt5-qtwebkit-workaround-build-breakage-after-svn-commit-136242.patch

# Fix compilation against latest ANGLE
# https://bugs.webkit.org/show_bug.cgi?id=109127
Patch8:         webkit-commit-142567.patch

# Fix detection of native tools which started to fail as of QtWebkit 5.1.0
# Caused by upstream commit 150223, so revert it for now
Patch9:         changeset_150223.diff

# smaller debuginfo s/-g/-g1/ (debian uses -gstabs) to avoid 4gb size limit
Patch10:        qtwebkit-opensource-src-5.0.1-debuginfo.patch 


%description
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.


# Win32
%package -n mingw32-qt5-%{qt_module}
Summary:        Qt5 for Windows - QtWebkit component

%description -n mingw32-qt5-%{qt_module}
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.


# Win64
%package -n mingw64-qt5-%{qt_module}
Summary:        Qt5 for Windows - QtWebkit component

%description -n mingw64-qt5-%{qt_module}
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.


%?mingw_debug_package


%prep
%setup -q -n %{source_folder}
%patch0 -p0 -b .icu
%patch2 -p0 -b .pkgconfig
%patch3 -p1 -b .angle
%patch4 -p1 -b .no_icu
%patch6 -p0 -b .export
%patch8 -p1 -b .angle_size_t
%patch9 -p1 -b .tools -R
%patch10 -p1 -b .debuginfo

# Make sure the bundled copy of the ANGLE libraries isn't used
rm -rf Source/ThirdParty/ANGLE


%build
# Make sure the native pkg-config files aren't used (RPM sets this environment variable automatically)
unset PKG_CONFIG_PATH

# The QMAKE_CXXFLAGS override is used to prevent a flood
# of warnings like: identifier 'nullptr' is a keyword in C++11 
%mingw_qmake_qt5 QMAKE_CXXFLAGS+=-Wno-c++0x-compat ../WebKit.pro
%mingw_make %{?_smp_mflags}


%install
%mingw_make install INSTALL_ROOT=$RPM_BUILD_ROOT

# .prl files aren't interesting for us
find $RPM_BUILD_ROOT -name "*.prl" -delete

# Rename the .a files to .dll.a as they're actually import libraries and not static libraries
for FN in $RPM_BUILD_ROOT%{mingw32_libdir}/*.a $RPM_BUILD_ROOT%{mingw64_libdir}/*.a ; do
    FN_NEW=$(echo $FN | sed s/'.a$'/'.dll.a'/)
    mv $FN $FN_NEW
done

# The .dll's are installed in both %%{mingw32_bindir} and %%{mingw32_libdir}
# One copy of the .dll's is sufficient
rm -f $RPM_BUILD_ROOT%{mingw32_libdir}/*.dll
rm -f $RPM_BUILD_ROOT%{mingw64_libdir}/*.dll

# The QtWebProcess executable is placed in the wrong folder, move it manually
mv $RPM_BUILD_ROOT%{mingw32_datadir}/qt5/bin/QtWebProcess.exe $RPM_BUILD_ROOT%{mingw32_bindir}/
mv $RPM_BUILD_ROOT%{mingw64_datadir}/qt5/bin/QtWebProcess.exe $RPM_BUILD_ROOT%{mingw64_bindir}/


# Win32
%files -n mingw32-qt5-%{qt_module}
%doc Source/WebCore/LICENSE*
%doc ChangeLog VERSION
%{mingw32_bindir}/QtWebProcess.exe
%{mingw32_bindir}/Qt5WebKit.dll
%{mingw32_bindir}/Qt5WebKitWidgets.dll
%{mingw32_includedir}/qt5/QtWebKit/
%{mingw32_includedir}/qt5/QtWebKitWidgets/
%{mingw32_libdir}/libQt5WebKit.dll.a
%{mingw32_libdir}/libQt5WebKitWidgets.dll.a
%{mingw32_libdir}/cmake/Qt5WebKit/
%{mingw32_libdir}/cmake/Qt5WebKitWidgets/
%{mingw32_libdir}/pkgconfig/Qt5WebKit.pc
%{mingw32_libdir}/pkgconfig/Qt5WebKitWidgets.pc
%{mingw32_datadir}/qt5/qml/QtWebKit/
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_webkit.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_webkitwidgets.pri

# Win64
%files -n mingw64-qt5-%{qt_module}
%doc Source/WebCore/LICENSE*
%doc ChangeLog VERSION
%{mingw64_bindir}/QtWebProcess.exe
%{mingw64_bindir}/Qt5WebKit.dll
%{mingw64_bindir}/Qt5WebKitWidgets.dll
%{mingw64_includedir}/qt5/QtWebKit/
%{mingw64_includedir}/qt5/QtWebKitWidgets/
%{mingw64_libdir}/libQt5WebKit.dll.a
%{mingw64_libdir}/libQt5WebKitWidgets.dll.a
%{mingw64_libdir}/cmake/Qt5WebKit/
%{mingw64_libdir}/cmake/Qt5WebKitWidgets/
%{mingw64_libdir}/pkgconfig/Qt5WebKit.pc
%{mingw64_libdir}/pkgconfig/Qt5WebKitWidgets.pc
%{mingw64_datadir}/qt5/qml/QtWebKit
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_webkit.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_webkitwidgets.pri


%changelog
* Sun Sep 22 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.1-1
- Update to 5.1.1
- Added license files

* Wed Jul 24 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-2
- Fix detection of native tools which started to fail as of QtWebkit 5.1.0
- Avoid 'too many sections' build failure

* Sun Jul 14 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-1
- Update to 5.1.0

* Sat May 18 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.2-2
- Bumped the BR: mingw{32,64}-angleproject to >= 0-0.5.svn2215.20130517
- Don't use the bundled ANGLE libraries any more
- Applied some upstream patches to prevent flooding the logs with
  compiler warnings when using gcc 4.8
- Added BR: mingw32-qt5-qtmultimedia mingw64-qt5-qtmultimedia
- Added BR: mingw32-libwebp mingw64-libwebp

* Fri May 10 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.2-1
- Update to 5.0.2
- Added BR: flex perl-version perl-Digest-MD5

* Sun Jan  6 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-1
- Update to QtWebKit 5.0.0 Final
- Workaround linker failure caused by recent QWebKit/QWebKitWidgets split
- Use the Qt4 unicode API as the mingw-qt5-qtbase currently doesn't use ICU
- Added BR: mingw32-pkg-config mingw64-pkg-config mingw32-sqlite mingw64-sqlite
- Added BR: mingw32-angleproject mingw64-angleproject
- Use the bundled ANGLE libraries for now as qtwebkit depends on non-public symbols

* Mon Nov 12 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.2.beta1.git20121112.23037105
- Update to 20121112 snapshot (rev 23037105)
- Rebuild against latest mingw-qt5-qtbase
- Dropped pkg-config rename hack as it's unneeded now
- Dropped upstreamed patch
- Added BR: python
- Added BR: ruby

* Wed Sep 12 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.1.beta1
- Initial release

