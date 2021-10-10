# Basic-TOTP

## Credits



## Scope

Simple authentication proxy for backend without any authentication
facilities or ones requiring basic authentication, but lacking TOTP
feature.

## Dependencies

Python 3, pip and virtualenv is needed, the requeired python packages
are in ```requirements.txt```.

## Use

Run ```mk-venv.sh``` to prepare the virtualenv in the ```venv```
directory.

The ```run.sh``` script can then be used to start the proxy at the
command line. Use the provided Systemd unit example to run the proxy as
a daemon.

## Performance

This solution is simple enogh to be reasonably performant. Even running
as a single-threaded solution, several hundred requests / second can
be achieved.

*The following is just an idea, it was not tested at all.*

One could start more than one instance of basic-totp and configure nginx
to balance load amongst them.

## Examples

* Systemd unit
* Nginx configuration

