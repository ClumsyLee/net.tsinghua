module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);

  var version = grunt.file.readJSON('package.json').version;

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    'create-windows-installer': {
      ia32: {
        appDirectory: 'build/<%= pkg.name %>-win32-ia32',
        outputDirectory: 'build/win32-ia32-installer',
        authors: 'Thomas Lee',
        remoteReleases: 'https://github.com/ThomasLee969/net.tsinghua'
      }
    },
    shell: {
      win32: {
        command: 'electron-packager . <%= pkg.name %> --platform=win32 ' +
                 '--arch=ia32 --asar=true --out=build/ --version=0.33.6 ' +
                 '--ignore=build/ --icon=resource/icon.ico ' +
                 '--app-version=<%= pkg.version %>'
      },
      darwin: {
        command: 'electron-packager . <%= pkg.name %> --platform=darwin ' +
                 '--arch=x64 --out=build/ --version=0.33.6 ' +
                 '--ignore=build/ --icon=resource/icon.icns ' +
                 '--app-version=<%= pkg.version %>'
      },
      'clean-win32': {
        command: 'rmdir /s /q build\\<%= pkg.name %>-win32-ia32',
        options: {failOnError: false}
      },
      'clean-win32-installer': {
        command: 'rmdir /s /q build\\win32-ia32-installer',
        options: {failOnError: false}
      },
      'clean-darwin': {
        command: 'rm -rf build/<%= pkg.name %>-darwin-x64/'
      }
    }
  });

  grunt.loadNpmTasks('grunt-electron-installer');

  grunt.registerTask('win32', ['shell:clean-win32', 'shell:win32',
                               'shell:clean-win32-installer',
                               'create-windows-installer']);
  grunt.registerTask('osx', ['shell:clean-darwin', 'shell:darwin']);
  grunt.registerTask('clean', ['shell:clean-darwin', 'shell:clean-win32',
                               'shell:clean-win32-installer']);
};
