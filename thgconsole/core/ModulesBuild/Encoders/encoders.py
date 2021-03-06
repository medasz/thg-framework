from thgconsole.core.ModulesBuild.Exploits.exploit import (BaseExploit, )
from thgconsole.core.CoreUtils.printer import (print_error, )


class BaseEncoder(BaseExploit):
    architecture = None

    def __init__(self):
        self.module_name = self.__module__.replace("thgconsole.modules.encoders.", "").replace(".", "/")

    def encode(self):
        raise NotImplementedError("Please implement 'encode()' method")

    def run(self):
        print_error("Module cannot be run")

    def __str__(self):
        return self.module_name

    def __format__(self, form):
        return format(self.module_name, form)
