from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=['keyring'],
                    excludes=[],
                    include_files=['config.yml'],
                    icon='icon.ico',
                    compressed=True)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('application.py', base=base, targetName='net_dot_tsinghua.exe')
]

setup(name='net.tsinghua',
      version = '0.1',
      description = 'A cross-platform auto-login utility for tsinghua students.',
      options = dict(build_exe = buildOptions),
      executables = executables)
