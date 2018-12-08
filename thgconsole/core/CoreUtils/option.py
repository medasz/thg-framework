import re
import os.path

from thgconsole.core.CoreUtils.exceptions import OptionValidationError
from thgconsole.core.CoreUtils.utils import (
    is_ipv4,
    is_ipv6,
)


class THGOption(object):
    """ Exploit attribute that is set by the end user """

    def __init__(self, default, description=""):
        self.label = None
        self.description = description

        if default:
            self.__set__("", default)
        else:
            self.display_value = ""
            self.value = ""

    def __get__(self, instance, owner):
        return self.value


class THGOptIP(THGOption):
    """ Option IP attribute """

    def __set__(self, instance, value):
        if not value or is_ipv4(value) or is_ipv6(value):
            self.value = self.display_value = value
        else:
            raise OptionValidationError("Invalid address. Provided address is not valid IPv4 or IPv6 address.")


class THGOptPort(THGOption):
    """ Option Port attribute """

    def __set__(self, instance, value):
        try:
            value = int(value)

            if 0 < value <= 65535:  # max port number is 65535
                self.display_value = str(value)
                self.value = value
            else:
                raise OptionValidationError("Invalid option. Port value should be between 0 and 65536.")
        except ValueError:
            raise OptionValidationError("Invalid option. Cannot cast '{}' to integer.".format(value))


class THGOptBool(THGOption):
    """ Option Bool attribute """

    def __init__(self, default, description=""):
        self.description = description

        if default:
            self.display_value = "true"
        else:
            self.display_value = "false"

        self.value = default

    def __set__(self, instance, value):
        if value == "true":
            self.value = True
            self.display_value = value
        elif value == "false":
            self.value = False
            self.display_value = value
        else:
            raise OptionValidationError("Invalid value. It should be true or false.")


class THGOptInteger(THGOption):
    """ Option Integer attribute """

    def __set__(self, instance, value):
        try:
            self.display_value = str(value)
            self.value = int(value)
        except ValueError:
            raise OptionValidationError("Invalid option. Cannot cast '{}' to integer.".format(value))


class THGOptFloat(THGOption):
    """ Option Float attribute """

    def __set__(self, instance, value):
        try:
            self.display_value = str(value)
            self.value = float(value)
        except ValueError:
            raise OptionValidationError("Invalid option. Cannot cast '{}' to float.".format(value))


class THGOptString(THGOption):
    """ Option String attribute """

    def __set__(self, instance, value):
        try:
            self.value = self.display_value = str(value)
        except ValueError:
            raise OptionValidationError("Invalid option. Cannot cast '{}' to string.".format(value))


class THGOptMAC(THGOption):
    """ Option MAC attribute """

    def __set__(self, instance, value):
        regexp = r"^[a-f\d]{1,2}:[a-f\d]{1,2}:[a-f\d]{1,2}:[a-f\d]{1,2}:[a-f\d]{1,2}:[a-f\d]{1,2}$"
        if re.match(regexp, value.lower()):
            self.value = self.display_value = value
        else:
            raise OptionValidationError("Invalid option. '{}' is not a valid MAC address".format(value))


class THGOptWordlist(THGOption):
    """ Option Wordlist attribute """

    def __get__(self, instance, owner):
        if self.display_value.startswith("file://"):
            path = self.display_value.replace("file://", "")
            with open(path, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                return lines

        return self.display_value.split(",")

    def __set__(self, instance, value):
        if value.startswith("file://"):
            path = value.replace("file://", "")
            if not os.path.exists(path):
                raise OptionValidationError("File '{}' does not exist.".format(path))

        self.value = self.display_value = value


class THGOptEncoder(THGOption):
    """ Option Encoder attribute """

    def __init__(self, default, description=""):
        self.description = description

        if default:
            self.display_value = default
            self.value = default
        else:
            self.display_value = ""
            self.value = None

    def __set__(self, instance, value):
        encoder = instance.get_encoder(value)

        if encoder:
            self.value = encoder
            self.display_value = value
        else:
            raise OptionValidationError("Encoder not available. Check available encoders with `show encoders`.")
