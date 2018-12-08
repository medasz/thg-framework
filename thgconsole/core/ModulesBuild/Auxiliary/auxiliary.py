import os
import threading
import time
from future.utils import with_metaclass, iteritems
from itertools import chain
from functools import wraps

from thgconsole.core.CoreUtils.printer import (print_status, thread_output_stream, )
from thgconsole.core.CoreUtils.option import THGOption

GLOBAL_OPTS = {}


class Protocol:
    CUSTOM = "custom"
    TCP = "custom/tcp"
    UDP = "custom/udp"
    FTP = "ftp"
    FTPS = "ftps"
    SSH = "ssh"
    TELNET = "telnet"
    HTTP = "http"
    HTTPS = "https"
    SNMP = "snmp"


class AuxiliaryOptionsAggregator(type):
    """ Metaclass for auxiliary base class.

    Metaclass is aggregating all possible Attributes that user can set
    for tab completion purposes.
    """

    def __new__(cls, name, bases, attrs):
        try:
            base_exploit_attributes = chain([base.exploit_attributes for base in bases])
        except AttributeError:
            attrs["auxiliary_attributes"] = {}
        else:
            attrs["auxiliary_attributes"] = {k: v for d in base_exploit_attributes for k, v in iteritems(d)}

        for key, value in iteritems(attrs):
            if isinstance(value, THGOption):
                value.label = key
                attrs["auxiliary_attributes"].update({key: [value.display_value, value.description]})
            elif key == "__info__":
                attrs["_{}{}".format(name, key)] = value
                del attrs[key]
            elif key in attrs["auxiliary_attributes"]:  # removing exploit_attribtue that was overwritten
                del attrs["auxiliary_attributes"][key]  # in the child and is not an Option() instance

        return super(AuxiliaryOptionsAggregator, cls).__new__(cls, name, bases, attrs)


class BaseAuxiliary(with_metaclass(AuxiliaryOptionsAggregator, object)):
    @property
    def options(self):
        """ Returns list of options that user can set.

        Returns list of options aggregated by
        ExploitionOptionsAggegator metaclass that user can set.

        :return: list of options that user can set
        """

        return list(self.auxiliary_attributes.keys())

    def __str__(self):
        return self.__module__.split('.', 2).pop().replace('.', os.sep)


class Exploit(BaseAuxiliary):
    """ Base class for Auxiliary """

    target_protocol = Protocol.CUSTOM

    def run(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def check(self):
        raise NotImplementedError("You have to define your own 'check' method.")

    def run_threads(self, threads_number: int, target_function: any, *args, **kwargs) -> None:
        """ Run function across specified number of threads

        :param int thread_number: number of threads that should be executed
        :param func target_function: function that should be executed accross specified number of threads
        :param any args: args passed to target_function
        :param any kwargs: kwargs passed to target function
        :return None
        """

        threads = []
        threads_running = threading.Event()
        threads_running.set()

        for thread_id in range(int(threads_number)):
            thread = threading.Thread(
                target=target_function,
                args=chain((threads_running,), args),
                kwargs=kwargs,
                name="thread-{}".format(thread_id),
            )
            threads.append(thread)

            print_status("{} thread is starting...".format(thread.name))
            thread.start()

        start = time.time()
        try:
            while thread.isAlive():
                thread.join(1)

        except KeyboardInterrupt:
            threads_running.clear()

        for thread in threads:
            thread.join()
            print_status("{} thread is terminated.".format(thread.name))

        print_status("Elapsed time: {} seconds".format(time.time() - start))


def multi(fn):
    """ Decorator for auxiliary.Auxiliary class

    Decorator that allows to feed auxiliary using text file containing
    multiple targets definition. Decorated function will be executed
    as many times as there is targets in the feed file.

    WARNING:
    Important thing to remember is fact that decorator will
    supress values returned by decorated function. Since method that
    perform attack is not supposed to return anything this is not a problem.

    """

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if self.target.startswith("file://"):
            original_target = self.target
            original_port = self.port

            _, _, feed_path = self.target.partition("file://")
            try:
                with open(feed_path) as file_handler:
                    for target in file_handler:
                        target = target.strip()
                        if not target:
                            continue

                        self.target, _, port = target.partition(":")
                        if port:
                            self.port = port
                        else:
                            self.port = original_port

                        fn(self, *args, **kwargs)
                    self.target = original_target
                    self.port = original_port
                    return  # Nothing to return, ran multiple times

            except IOError:
                return
        else:
            return fn(self, *args, **kwargs)

    return wrapper


class DummyFile(object):
    """ Mocking file object. Optimilization for the "mute" decorator. """
    def write(self, x):
        pass


def mute(fn):
    """ Suppress function from printing to sys.stdout """

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        thread_output_stream.setdefault(threading.current_thread(), []).append(DummyFile())
        try:
            return fn(self, *args, **kwargs)
        finally:
            thread_output_stream[threading.current_thread()].pop()
    return wrapper


class LockedIterator(object):
    def __init__(self, it):
        self.lock = threading.Lock()
        self.it = it.__iter__()

    def __iter__(self):
        return self

    def next(self):
        self.lock.acquire()
        try:
            item = next(self.it)

            if type(item) is tuple:
                return (item[0].strip(), item[1].strip())
            elif type(item) is str:
                return item.strip()

            return item
        finally:
            self.lock.release()
