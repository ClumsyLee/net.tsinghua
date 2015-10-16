var path = require('path');
var app = require('app');

// init_updater: Return true if need to exist.
// check_updates: Update if possible.

if (process.platform == 'darwin') {
  var autoUpdater = require('auto-updater');

  exports.init_updater = function () {
    autoUpdater.on('error', function (event, message) {
      console.log(message);
    });
    autoUpdater.on('checking-for-update', function () {
      console.log('Checking for update.');
    });
    autoUpdater.on('update-available', function () {
      console.log('Update available.');
    });
    autoUpdater.on('update-not-available', function () {
      console.log('Update not available.');
    });
    autoUpdater.on('update-downloaded', function (
        event, releaseNotes, releaseName, releaseDate, updateUrl, quitAndUpdate) {
      console.log('Update downloaded, quit and update.');
      quitAndUpdate();
    });
    autoUpdater.setFeedUrl('https://net-tsinghua.herokuapp.com/update/osx/' +
                           app.getVersion());
  };

  exports.check_updates = function () {
    autoUpdater.checkForUpdates();
  }
} else if (process.platform == 'win32') {
  var cp = require('child_process');
  // Based on code from http://www.mylifeforthecode.com/tag/windows-installer/.
  // FIXME: Check whether Update.exe exists.
  var updateDotExe = path.resolve(path.dirname(process.execPath),
                                  '..', 'Update.exe');

  function executeSquirrelCommand(args, done) {
    var child = cp.spawn(updateDotExe, args, { detached: true });
    child.on('close', function(code) {
      done();
    });
  }

  function install(done) {
    var target = path.basename(process.execPath);
    console.log('Creating shortcut.');
    executeSquirrelCommand(['--createShortcut', target,
                            '--shortcut-locations', 'Desktop,StartMenu,Startup'],
                           done);
  }

  function uninstall(done) {
    var target = path.basename(process.execPath);
    console.log('Removing shortcut.');
    executeSquirrelCommand(['--removeShortcut', target,
                            '--shortcut-locations', 'Desktop,StartMenu,Startup'],
                           done);
  }

  exports.init_updater = function() {
    var squirrelEvent = process.argv[1];
    switch (squirrelEvent) {
      case '--squirrel-install':
        console.log('App installed.');
        install(app.quit);
        return true;
      case '--squirrel-updated':
        console.log('App updated.');
        install(app.quit);
        return true;
      case '--squirrel-obsolete':
        console.log('About to update to a newer version, quit now.');
        app.quit();
        return true;
      case '--squirrel-uninstall':
        console.log('Uninstalling.');
        uninstall(app.quit);
        return true;
    }
  };

  exports.check_updates = function () {
    var child = cp.spawn(updateDotExe, [
        "--update",
        "https://net-tsinghua.herokuapp.com/update/win32/" + app.getVersion()
      ], { detached: true });
    child.on('close', function(code) {
      console.log('Updating is done.');
    });
  };
} else {  // Unsupported system.
  exports.init_updater = function () {};
  exports.check_updates = function () {};
}
