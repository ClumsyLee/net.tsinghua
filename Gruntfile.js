module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);

  var version = grunt.file.readJSON('package.json').version;

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    'create-windows-installer': {
      // x64: {
      //   appDirectory: 'build/<%= pkg.name %>-win32-x64',
      //   outputDirectory: 'build/',
      //   authors: 'Thomas Lee',
      //   remoteReleases: 'https://net-tsinghua.herokuapp.com/update/win32/' + version
      // },
      ia32: {
        appDirectory: 'build/<%= pkg.name %>-win32-ia32',
        outputDirectory: 'build/win32-ia32-installer',
        authors: 'Thomas Lee',
        remoteReleases: 'https://net-tsinghua.herokuapp.com/update/win32/' + version
      }
    },
    shell: {
      win32: {
        command: 'electron-packager . <%= pkg.name %> --platform=win32 --arch=ia32 --out=build/ --version=0.33.6 --ignore=build/ --icon=resource/icon.ico --app-version=<%= pkg.version %>'
      },
      darwin: {
        command: 'electron-packager . <%= pkg.name %> --platform=darwin --arch=x64 --out=build/ --version=0.33.6 --ignore=build/ --icon=resource/icon.icns --app-version=<%= pkg.version %>'
      }
    }
  });

  grunt.loadNpmTasks('grunt-electron-installer');

  grunt.registerTask('default', ['shell', 'create-windows-installer']);
};
