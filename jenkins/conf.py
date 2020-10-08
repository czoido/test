import argparse
import os
import platform
from contextlib import contextmanager

winpylocation = {"py27": "C:\\Python27\\python.exe",
                 "py34": "C:\\Python34\\python.exe",
                 "py36": "C:\\Python36\\python.exe",
                 "py37": "C:\\Python37\\python.exe",
                 "py38": "C:\\Python38\\python.exe"}

macpylocation = {"py27": "/usr/bin/python",  # /Users/jenkins_ci/.pyenv/versions/2.7.11/bin/python",
                 "py34": "/Users/jenkins_ci/.pyenv/versions/3.4.7/bin/python",
                 "py36": "/Users/jenkins_ci/.pyenv/versions/3.6.5/bin/python",
                 "py37": "/Users/jenkins_ci/.pyenv/versions/3.7.6/bin/python",
                 "py38": "/Users/jenkins_ci/.pyenv/versions/3.8.1/bin/python",}

linuxpylocation = {"py27": "/usr/bin/python2.7",
                   "py34": "/usr/bin/python3.4",
                   "py36": "/usr/bin/python3.6",
                   "py37": "/usr/bin/python3.7",
                   "py38": "/usr/bin/python3.8"}


def get_environ(tmp_path):
    if platform.system() == "Windows":
        return {"CONAN_USER_HOME_SHORT": os.path.join(tmp_path, ".conan")}
    return {}


class Extender(argparse.Action):
    """Allows to use the same flag several times in a command and creates a list with the values.
       For example:
           conan install MyPackage/1.2@user/channel -o qt:value -o mode:2 -s cucumber:true
           It creates:
           options = ['qt:value', 'mode:2']
           settings = ['cucumber:true']
    """
    def __call__(self, parser, namespace, values, option_strings=None):  # @UnusedVariable
        # Need None here incase `argparse.SUPPRESS` was supplied for `dest`
        dest = getattr(namespace, self.dest, None)
        if not hasattr(dest, 'extend') or dest == self.default:
            dest = []
            setattr(namespace, self.dest, dest)
            # if default isn't set to None, this method might be called
            # with the default as `values` for other arguments which
            # share this destination.
            parser.set_defaults(**{self.dest: None})

        try:
            dest.extend(values)
        except ValueError:
            dest.append(values)



@contextmanager
def _environment_add(env_vars, post=False):
    """
    :param env_vars: List (dict) of simple environment vars. {name: value, name2: value2}
                     => e.g.: MYVAR=1
                     The values can also be lists of appendable environment vars.
                     {name: [value, value2]} => e.g. PATH=/path/1:/path/2
                     If the value is set to None, then that environment variable is unset.
    :param post: if True, the environment is appended at the end, not prepended (only LISTS)
    :return: None
    """
    if not env_vars:
        yield
        return

    unset_vars = []
    apply_vars = {}
    for name, value in env_vars.items():
        if value is None:
            unset_vars.append(name)
        elif isinstance(value, list):
            apply_vars[name] = os.pathsep.join(value)
            old = os.environ.get(name)
            if old:
                if post:
                    apply_vars[name] = old + os.pathsep + apply_vars[name]
                else:
                    apply_vars[name] += os.pathsep + old
        else:
            apply_vars[name] = value

    old_env = dict(os.environ)
    os.environ.update(apply_vars)
    for var in unset_vars:
        os.environ.pop(var, None)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_env)

@contextmanager
def environment_append(env_vars):
    with _environment_add(env_vars, post=False):
        yield

@contextmanager
def chdir(newdir):
    old_path = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(old_path)
