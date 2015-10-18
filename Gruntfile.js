module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);

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
      nupkg_delta: '<%= path.win32_installer %>/<%= pkg.name %>-<%= pkg.version %>-delta.nupkg',
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
        certificatePassword: '',
        iconUrl: 'https://raw.githubusercontent.com/ThomasLee969/net.tsinghua/master/resource/icon.ico',
        setupIcon: 'resource/icon.ico',
        remoteReleases: 'https://github.com/ThomasLee969/net.tsinghua'
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
      zip_win32: {
        command: 'zip -q --junk-paths <%= file.win32_zip %> <%= file.setup_exe %>'
      },
      zip_darwin: {
        command: 'cd <%= path.darwin %> && zip -rq --symlinks ' +
                 '../../<%= file.darwin_zip %> <%= pkg.name %>.app'
      },
      mkdir: {
        command: 'mkdir <%= path.release %>'
      },
      mv_files: {
        command: 'mv <%= file.RELEASES %> <%= file.nupkg_full %> ' +
                 '<%= file.nupkg_delta %> <%= path.release %>'
      },
      appdmg: {
        command: 'appdmg appdmg.json <%= file.darwin_dmg %>'
      }
    }
  });

  grunt.loadNpmTasks('grunt-electron-installer');

  grunt.registerTask('win32', ['shell:build_win32', 'create-windows-installer']);
  grunt.registerTask('darwin', ['shell:mkdir', 'shell:build_darwin']);
  grunt.registerTask('release', ['shell:zip_win32', 'shell:zip_darwin',
                                 'shell:mv_files', 'shell:appdmg']);
};
