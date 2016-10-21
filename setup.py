from setuptools import setup, Extension, find_packages

setup(name='transfernode',
      version='1.0',
      author='Filip Sufitchi',
      author_email="fsufitchi@gmail.com",
      description="Websocket file transfer node",
      url="https://github.com/fsufitch/filebounce-transfer-node",
      package_dir={'': 'src'},
      packages=['transfernode'],
      entry_points={
          "console_scripts": [
              "transfernode=transfernode.server:main"
          ],
        },

      install_requires=[
          'protobuf',
          'PyYAML',
          'Rx',
          'tornado',
          ],
      )
