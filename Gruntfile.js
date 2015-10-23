module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);
  var fs = require('fs-extra');
  var path = require('path');

  var version = grunt.file.readJSON('package.json').version;

  // Project configuration.
  grunt.initConfig({
    // Custom configuration.
    path: {
      win32: 'build/<%= pkg.name %>-win32-ia32',
      win32_installer: 'build/win32-ia32-installer',
      darwin: 'build/<%= pkg.name %>-darwin-x64',
      release: 'build/release/<%= pkg.version %>'
    },
    file: {
      setup_exe: '<%= path.win32_installer %>/Setup.exe',
      RELEASES: '<%= path.win32_installer %>/RELEASES',
      nupkg_full: '<%= path.win32_installer %>/<%= pkg.name %>-<%= pkg.version %>-full.nupkg',
      // nupkg_delta: '<%= path.win32_installer %>/<%= pkg.name %>-<%= pkg.version %>-delta.nupkg',
      win32_zip: '<%= path.release %>/<%= pkg.name %>-v<%= pkg.version %>-win32-ia32.zip',
      darwin_zip: '<%= path.release %>/<%= pkg.name %>-v<%= pkg.version %>-darwin-x64.zip',
      darwin_dmg: '<%= path.release %>/<%= pkg.name %>-v<%= pkg.version %>-darwin-x64.dmg'
    },
    electron_version: '0.33.6',

    pkg: grunt.file.readJSON('package.json'),
    'create-windows-installer': {
      ia32: {
        appDirectory: '<%= path.win32 %>',
        outputDirectory: '<%= path.win32_installer %>',
        authors: 'Thomas Lee',
        certificateFile: 'resource/cert.p12',
        certificatePassword: process.env.CERTIFICATE_PASSWORD,
        iconUrl: 'https://raw.githubusercontent.com/ThomasLee969/net.tsinghua/master/resource/icon.ico',
        setupIcon: 'resource/icon.ico'
        // remoteReleases: 'https://github.com/ThomasLee969/net.tsinghua'
      }
    },
    shell: {
      build_win32: {
        command: 'electron-packager . <%= pkg.name %> --platform=win32 ' +
                 '--arch=ia32 --out=build/ --version=<%= electron_version %> ' +
                 '--asar=true --ignore="(build|resource/cert.p12)" --icon=resource/icon.ico ' +
                 '--app-version=<%= pkg.version %> --overwrite=true ' +
                 '--version-string.CompanyName="Thomas Lee" ' +
                 '--version-string.LegalCopyright="Copyright (c) 2015 Thomas Lee" ' +
                 '--version-string.FileDescription=<%= pkg.name %> ' +
                 '--version-string.OriginalFilename=<%= pkg.name %>.exe ' +
                 '--version-string.FileVersion="<%= pkg.version %>" ' +
                 '--version-string.ProductVersion=<%= pkg.version %> ' +
                 '--version-string.ProductName=<%= pkg.name %> ' +
                 '--version-string.InternalName=<%= pkg.name %>'
      },
      build_darwin: {
        command: 'electron-packager . <%= pkg.name %> --platform=darwin ' +
                 '--arch=x64 --out=build/ --version=<%= electron_version %> ' +
                 '--ignore="(build|resource/cert.p12)" --icon=resource/icon.icns ' +
                 '--app-version=<%= pkg.version %> --overwrite=true ' +
                 '--sign="Thomas Lee"'
      },
      zip_setup_exe: {
        command: '7z a <%= file.win32_zip %> %APPVEYOR_BUILD_FOLDER%/<%= file.setup_exe %>'
      },
      zip_app: {
        command: 'cd <%= path.darwin %> && zip -rq --symlinks ' +
                 '../../<%= file.darwin_zip %> <%= pkg.name %>.app'
      },
      appdmg: {
        command: 'appdmg appdmg.json <%= file.darwin_dmg %>'
      }
    }
  });

  grunt.loadNpmTasks('grunt-electron-installer');

  grunt.registerTask('mkdir', function () {
    try {
      fs.mkdirpSync(grunt.config(['path', 'release']));
    } catch (err) {
      console.error('Unable to create release directory: %s', err);
    }
  });

  grunt.registerTask('move_win32_files', function () {
    ['RELEASES', 'nupkg_full'].forEach(function (filename) {
      var origin_path = grunt.config(['file', filename]);
      var basename = path.basename(origin_path);
      var new_path = path.join(grunt.config(['path', 'release']), basename);

      console.log('Moving %s to %s', origin_path, new_path);
      fs.copySync(origin_path, new_path);
    });
  });

  grunt.registerTask('win32', ['mkdir', 'shell:build_win32',
                               'create-windows-installer',
                               'shell:zip_setup_exe',
                               'move_win32_files']);
  grunt.registerTask('darwin', ['mkdir', 'shell:build_darwin',
                                'shell:zip_app', 'shell:appdmg']);
};
