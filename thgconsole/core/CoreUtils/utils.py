import re
import os
import importlib
import string
import random
from functools import wraps

import thgconsole.modules as thg_modules

import thgconsole.file_suport.wordlists as wordlists

from thgconsole.core.CoreUtils.printer import print_error, print_info
from thgconsole.core.CoreUtils.exceptions import THGtException

MODULES_DIR = thg_modules.__path__[0]
WORDLISTS_DIR = wordlists.__path__[0]

def random_text(length: int, alph: str = string.ascii_letters + string.digits) -> str:
    """ Generates random string text

    :param int length: length of text to generate
    :param str alph: string of all possible characters to choose from
    :return str: generated random string of specified size
    """

    return "".join(random.choice(alph) for _ in range(length))


def is_ipv4(address: str) -> bool:
    """ Checks if given address is valid IPv4 address

    :param str address: IP address to check
    :return bool: True if address is valid IPv4 address, False otherwise
    """

    regexp = "^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    if re.match(regexp, address):
        return True

    return False


def is_ipv6(address: str) -> bool:
    """ Checks if given address is valid IPv6 address

    :param str address: IP address to check
    :return bool: True if address is valid IPv6 address, False otherwise
    """

    regexp = "^(?:(?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)%.*$"

    if re.match(regexp, address):
        return True

    return False


def convert_ip(address: str) -> bytes:
    """ Converts IP to bytes

    :param str address: IP address that should be converted to bytes
    :return bytes: IP converted to bytes format
    """

    res = b""
    for i in address.split("."):
        res += bytes([int(i)])
    return res


def convert_port(port: int) -> bytes:
    """ Converts Port to bytes

    :param int port: port that should be conveted to bytes
    :return bytes: port converted to bytes format
    """

    res = "%.4x" % int(port)
    return bytes.fromhex(res)


def index_modules(modules_directory: str = MODULES_DIR) -> list:
    """ Returns list of all exploits modules

    :param str modules_directory: path to modules directory
    :return list: list of found modules
    """

    modules = []
    for root, dirs, files in os.walk(modules_directory):
        _, package, root = root.rpartition("thgconsole/modules/".replace("/", os.sep))
        root = root.replace(os.sep, ".")
        files = filter(lambda x: not x.startswith("__") and x.endswith(".py"), files)
        modules.extend(map(lambda x: ".".join((root, os.path.splitext(x)[0])), files))

    return modules

def index_extra_modules(modules_directory=MODULES_DIR):
    """ Return list of all exploits modules """

    modules = []
    for root, dirs, files in os.walk(modules_directory):
        _, package, root = root.rpartition('thg_extra_modules/'.replace('/', os.sep))
        root = root.replace(os.sep, '.')
        files = filter(lambda x: not x.startswith("__") and x.endswith('.py'), files)
        modules.extend(map(lambda x: '.'.join((root, os.path.splitext(x)[0])), files))
    return modules

def import_exploit(path: str):
    """ Imports exploit module

    :param str path: absolute path to exploit e.g. thgconsole.modules.exploits.asus_auth_bypass
    :return: exploit module or error
    """

    try:
        module = importlib.import_module(path)
        if hasattr(module, "Payload"):
            return getattr(module, "Payload")
        elif hasattr(module, "Encoder"):
            return getattr(module, "Encoder")
        elif hasattr(module, "Exploit"):
            return getattr(module, "Exploit")
        else:
            raise ImportError("No module named '{}'".format(path))

    except (ImportError, AttributeError, KeyError) as err:
        raise THGtException(
            "Error during loading '{}'\n\n"
            "Error: {}\n\n"
            "It should be valid path to the module. "
            "Use <tab> key multiple times for completion.".format(humanize_path(path), err)
        )


def iter_modules(modules_directory: str = MODULES_DIR) -> list:
    """ Iterates over valid modules

    :param str modules_directory: path to modules directory
    :return list: list of found modules
    """

    modules = index_modules(modules_directory)
    modules = map(lambda x: "".join(["thgconsole.modules.", x]), modules)
    for path in modules:
        yield import_exploit(path)


def pythonize_path(path: str) -> str:
    """ Replaces argument to valid python dotted notation.

    ex. foo/bar/baz -> foo.bar.baz

    :param str path: path to pythonize
    :return str: pythonized path
    """

    return path.replace("/", ".")


def humanize_path(path: str) -> str:
    """ Replace python dotted path to directory-like one.

    ex. foo.bar.baz -> foo/bar/baz

    :param str path: path to humanize
    :return str: humanized path
    """

    return path.replace(".", "/")


def module_required(fn):
    """ Checks if module is loaded.

    Decorator that checks if any module is activated
    before executing command specific to modules (ex. 'run').
    """

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if not self.current_module:
            print_error("You have to activate any module with 'use' command.")
            return
        return fn(self, *args, **kwargs)

    try:
        name = "module_required"
        wrapper.__decorators__.append(name)
    except AttributeError:
        wrapper.__decorators__ = [name]
    return wrapper


def stop_after(space_number):
    """ Decorator that determines when to stop tab-completion

    Decorator that tells command specific complete function
    (ex. "complete_use") when to stop tab-completion.
    Decorator counts number of spaces (' ') in line in order
    to determine when to stop.

        ex. "use exploits/dlink/specific_module " -> stop complete after 2 spaces
        "set rhost " -> stop completing after 2 spaces
        "run " -> stop after 1 space

    :param space_number: number of spaces (' ') after which tab-completion should stop
    :return:
    """

    def _outer_wrapper(wrapped_function):
        @wraps(wrapped_function)
        def _wrapper(self, *args, **kwargs):
            try:
                if args[1].count(" ") == space_number:
                    return []
            except Exception as err:
                print_info(err)
            return wrapped_function(self, *args, **kwargs)
        return _wrapper
    return _outer_wrapper


def lookup_vendor(addr: str) -> str:
    """ Lookups vendor (manufacturer) based on MAC address

    :param str addr: MAC address to lookup
    :return str: vendor name from oui.dat database
    """

    addr = addr.upper().replace(":", "")

    path = "./thgconsole/file_suport/vendors/oui.dat"
    with open(path, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line == "" or line[0] == "#":
                continue

            mac, name = line.split(" ", 1)
            if addr.startswith(mac):
                return name

    return None


class Version(object):
    def __init__(self, value):
        self.value = str(value)

    def __set__(self, value):
        self.value = value

    def __lt__(self, other):
        """ Override the default x<y """
        if self._compare_versions(self.value, other.value) < 0:
            return True
        return False

    def __le__(self, other):
        """Override the default x<=y"""
        if self._compare_versions(self.value, other.value) <= 0:
            return True
        return False

    def __eq__(self, other):
        """Override the default x==y"""
        return self.value == other.value

    def __ne__(self, other):
        """Override the default x!=y or x<>y"""
        return self.value != other.value

    def __gt__(self, other):
        """Override the defualt x>y"""
        if self._compare_versions(self.value, other.value) > 0:
            return True
        return False

    def __ge__(self, other):
        """Override the default x>=y"""
        if self._compare_versions(self.value, other.value) >= 0:
            return True
        return False

    @staticmethod
    def _compare_versions(version1, version2):
        """ Version comparision

        :param Version version1:
        :param Version version2:
        :return int:
            if version1 < version2 then -1
            if version1 == version2 then 0
            if version1 > version2 then 1
        """

        arr1 = re.sub(r"\D", ".", str(version1)).split(".")
        arr2 = re.sub(r"\D", ".", str(version2)).split(".")

        i = 0

        while(i < len(arr1)):
            if int(arr2[i]) > int(arr1[i]):
                return -1

            if int(arr1[i]) > int(arr2[i]):
                return 1

            i += 1

        return 0


def detect_file_content(content: str, f: str = "/etc/passwd") -> bool:
    """ Detect specific file content in content

    :param str content: file content that should be analyzed
    :param str f: file that the content should be compared with
    :return bool: True if the content was recognized, False otherwise
    """

    if f in ["/etc/passwd", "/etc/shadow"]:
        if re.findall(r"(root|[aA]dmin):.*?:.*?:.*?:.*?:.*?:", content):
            return True

    return False
