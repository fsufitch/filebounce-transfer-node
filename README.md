# File Bounce Transfer Node

This is a small Python service that receives a file stream via a
websocket connection, and redistributes it to download recipients via
HTTP.

## Development Setup

System requirements:

- Git
- Python 3.5+
- Setuptools installed for the right version of Python
  - To install, run the [ez_setup.py](https://bootstrap.pypa.io/ez_setup.py)
    script.
- Windows, Linux, or Unix. This service is made to be OS-agnostic.

First, we need the `pip` package manager and `virtualenv`.

    $ python -m easy_install pip virtualenv

> Everywhere the `python` command is used, you should be sure to use the correct version of Python you want to use for running this code.

Next, we can clone the repo.

    $ git clone git@github.com:fsufitch/filebounce-transfer-node.git
    $ cd filebounce-transfer-node/

We will create a Python virtual environment for our dependencies in
the `env/` folder in here.

    $ python -m virtualenv env/

>At this point, we should switch to using the "sandboxed" Python
executables available in `env/bin/`. If you get tired of typing `env/bin/python` or `env/bin/pip` all the time, you can "activate" the environment and map those to `python` and `pip` using:

>     $ source env/bin/activate

The source repo contains a `setup.py` that can manage installing all required dependencies and creating the development environment. To do so, simply run:

    $ env/bin/python setup.py develop

The repo is now ready for development.

## Usage

To run the transfer node server, use `env/bin/transfernode <configfile>`. A sample development configuration file is included as `config.develop.yaml`.
