module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);

  var version = grunt.file.readJSON('package.json').version;

  // Project configuration.
  grunt.initConfig({
    // Custom configuration.
    path: {
      win32: 'build/<%= pkg.name %>-win32-ia32',
      win32_installer: 'build/win32-ia32-installer',
    },
    electron_version: '0.33.6',

    pkg: grunt.file.readJSON('package.json'),
    'create-windows-installer': {
      ia32: {
        appDirectory: '<%= path.win32 %>',
        outputDirectory: '<%= path.win32_installer %>',
        remoteReleases: 'https://github.com/ThomasLee969/net.tsinghua'
      }
    },
    shell: {
      win32: {
        command: 'electron-packager . <%= pkg.name %> --platform=win32 ' +
                 '--arch=ia32 --out=build/ --version=<%= electron_version %> ' +
                 '--asar=true --ignore=build/ --icon=resource/icon.ico ' +
                 '--app-version=<%= pkg.version %> --overwrite=true'
      },
      darwin: {
        command: 'electron-packager . <%= pkg.name %> --platform=darwin ' +
                 '--arch=x64 --out=build/ --version=<%= electron_version %> ' +
                 '--ignore=build/ --icon=resource/icon.icns ' +
                 '--app-version=<%= pkg.version %> --overwrite=true'
      }
    }
  });

  grunt.loadNpmTasks('grunt-electron-installer');

  grunt.registerTask('win32', ['shell:win32', 'create-windows-installer']);
  grunt.registerTask('osx', ['shell:darwin']);
};
