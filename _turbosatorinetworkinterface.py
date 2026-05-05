"""Turbo-Satori network interface.

This module contains a class implementing a network interface for Turbo-Satori
(see www.brainvoyager.com/products/turbosatori.html).

Rewritten to remove the expyriment dependency.

"""

import sys
import struct
import array as arr
from time import perf_counter

from tcpclient import TcpClient


# ---------------------------------------------------------------------------
# Helpers (replaces expyriment.misc._miscellaneous.byte2unicode / unicode2byte)
# ---------------------------------------------------------------------------

def _byte2unicode(s):
    if isinstance(s, str):
        return s
    return s.decode('utf-8', errors='replace')


def _unicode2byte(u):
    if isinstance(u, bytes):
        return u
    return u.encode('utf-8', errors='replace')


def _get_time():
    """Return current time in seconds (high-resolution)."""
    return perf_counter()


# ---------------------------------------------------------------------------

class TurbosatoriNetworkInterface:
    """A class implementing a network interface to Turbo-Satori.

    See http://www.brainvoyager.com/products/turbosatori.html
    for more information.

    """

    class TimeoutError(Exception):
        pass

    class RequestError(Exception):
        pass

    class DataError(Exception):
        pass

    def __init__(self, host, port, timeout=2000, connect=True):
        """Create a TurbosatoriNetworkInterface.

        Parameters:
        -----------
        host : str
            The hostname or IPv4 address of the TBV server to connect to.
        port : int
            The port on the Turbo-Satori server to connect to.
        timeout : int, optional
            The maximal time to wait for a response from the server for each
            request (default=2000).
        connect : bool, optional
            If True, connect immediately (default=True).

        """

        self._host = host
        self._port = port
        self._is_connected = False
        self._turbosatori_plugin_version = None
        self._tcp = TcpClient(host, port, None, False)
        self._timeout = timeout
        if connect:
            self.connect()

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        if self._is_connected:
            raise AttributeError("Cannot set host if connected!")
        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if self._is_connected:
            raise AttributeError("Cannot set port if connected!")
        self._port = value

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def turbosatori_plugin_version(self):
        return self._turbosatori_plugin_version

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if self._is_connected:
            raise AttributeError("Cannot set timeout if connected!")
        self._timeout = value

    def connect(self):
        """Connect to the Turbo-Satori server."""

        if not self._is_connected:
            self._tcp.connect()
            data, rt = self.request_data("Request Socket")
            try:
                self._turbosatori_plugin_version = (
                    struct.unpack('!i', data[:4])[0],
                    struct.unpack('!i', data[4:8])[0],
                    struct.unpack('!i', data[8:])[0])
            except:
                raise RuntimeError("Requesting a socket failed!")
            self._is_connected = True

    def _send(self, message, *args):
        length = len(message)
        arg_length = sum(len(a) for a in args)
        data = struct.pack('!q', length + 5 + arg_length) + \
            b"\x00\x00\x00" + _unicode2byte(chr(length + 1)) + message + b"\x00"
        for arg in args:
            data += arg
        self._tcp.send(data)

    def _wait(self):
        receive, rt = self._tcp.wait(package_size=8, duration=self._timeout)
        if receive is None:
            return None
        length = struct.unpack('!q', receive)[0]
        data, rt = self._tcp.wait(package_size=length, duration=self._timeout)
        if data is None:
            return None
        return data[4:]

    def request_data(self, request, *args):
        """Request data from Turbo-Satori.

        Parameters:
        -----------
        request : str
            The request to be sent to Turbo-Satori.

        Returns:
        --------
        data : bytes
            The byte string of the received data.
        rt : int
            The time it took to get the data in milliseconds.

        """

        start = _get_time()
        self._tcp.clear()
        request = _unicode2byte(request)
        self._send(request, *args)
        data = self._wait()
        arg_length = sum(len(x) for x in args)
        arg = b"".join(args)

        if data is None:
            raise TurbosatoriNetworkInterface.TimeoutError(
                "Waiting for requested data timed out!")
        elif _byte2unicode(data).startswith("Wrong request!"):
            raise TurbosatoriNetworkInterface.RequestError(
                "Wrong request '{0}'!".format(data[19:-1]))
        elif data[0:len(request) + 1 + arg_length] != request + b"\x00" + arg:
            raise TurbosatoriNetworkInterface.DataError(
                "Received data does not match request!")
        else:
            return data[len(request) + 1:], int((_get_time() - start) * 1000)

    def close(self):
        """Close the connection."""

        self._tcp.close()
        self._is_connected = False

    # -----------------------------------------------------------------------
    # Basic Project Queries
    # -----------------------------------------------------------------------

    def get_current_time_point(self):
        data, rt = self.request_data("tGetCurrentTimePoint")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!i', data)[0], rt

    def get_nr_of_channels(self):
        data, rt = self.request_data("tGetNrOfChannels")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!i', data)[0], rt

    def get_values_feedback_folder(self):
        folder, rt = self.request_data("tGetValuesFeedbackFolder")
        if folder is None:
            return None, rt
        elif folder[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(folder[19:-1]))
        else:
            return _byte2unicode(folder[4:-1]), rt

    def get_images_feedback_folder(self):
        folder, rt = self.request_data("tGetImagesFeedbackFolder")
        if folder is None:
            return None, rt
        elif folder[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(folder[19:-1]))
        else:
            return _byte2unicode(folder[4:-1]), rt

    def get_nr_of_selected_channels(self):
        data, rt = self.request_data("tGetNrOfSelectedChannels")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!i', data)[0], rt

    def get_selected_channels(self):
        data, rt = self.request_data("tGetSelectedChannels")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return ([struct.unpack('!i', data[x * 4:x * 4 + 4])[0]
                     for x in range(0, len(data) // 4)], rt)

    def get_raw_data_scale_factor(self):
        data, rt = self.request_data("tGetRawDataScaleFactor")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data)[0], rt

    def get_raw_data_wl1(self, channel, frame):
        channel = struct.pack('!i', channel)
        frame = struct.pack('!i', frame)
        data, rt = self.request_data("tGetRawDataWL1", channel, frame)
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data[8:])[0], rt

    def get_raw_data_wl2(self, channel, frame):
        channel = struct.pack('!i', channel)
        frame = struct.pack('!i', frame)
        data, rt = self.request_data("tGetRawDataWL2", channel, frame)
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data[8:])[0], rt

    def is_data_oxy_deoxy_converted(self):
        data, rt = self.request_data("tIsDataOxyDeoxyConverted")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return bool(struct.unpack('!i', data)[0]), rt

    def get_oxy_data_scale_factor(self):
        data, rt = self.request_data("tGetOxyDataScaleFactor")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data)[0], rt

    def get_data_oxy(self, channel, frame):
        channel = struct.pack('!i', channel)
        frame = struct.pack('!i', frame)
        data, rt = self.request_data("tGetDataOxy", channel, frame)
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data[8:])[0], rt

    def get_data_deoxy(self, channel, frame):
        channel = struct.pack('!i', channel)
        frame = struct.pack('!i', frame)
        data, rt = self.request_data("tGetDataDeOxy", channel, frame)
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data[8:])[0], rt

    def get_sampling_rate(self):
        data, rt = self.request_data("tGetSamplingRate")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data)[0], rt

    def get_number_of_classes(self):
        data, rt = self.request_data("tGetNumberOfClasses")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!i', data)[0], rt

    def get_current_classifier_output(self):
        data, rt = self.request_data("tGetCurrentClassifierOutput")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data)[0], rt

    def get_full_nr_of_predictors(self):
        data, rt = self.request_data("tGetFullNrOfPredictors")
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!i', data)[0], rt

    def get_value_of_design_matrix(self, predictor, frame, chromophore):
        predictor = struct.pack('!i', predictor)
        frame = struct.pack('!i', frame)
        chromophore = struct.pack('!i', chromophore)
        data, rt = self.request_data("tGetValueOfDesignMatrix", predictor,
                                     frame, chromophore)
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data[12:])[0], rt

    def get_prediction_of_channel(self, channel, chromophore):
        channel = struct.pack('!i', channel)
        chromophore = struct.pack('!i', chromophore)
        data, rt = self.request_data("tGetPredicitonOfChannel", channel, chromophore)
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data[8:])[0], rt

    def get_beta_of_channel(self, channel, beta, chromophore):
        channel = struct.pack('!i', channel)
        beta = struct.pack('!i', beta)
        chromophore = struct.pack('!i', chromophore)
        data, rt = self.request_data("tGetBetaOfChannel", channel, beta,
                                     chromophore)
        if data is None:
            return None, rt
        elif b"Wrong request!" in data:
            print("Warning: get_beta_of_channel - TSI error: {0}".format(data))
            return None, rt
        elif len(data) < 16:
            print("Warning: get_beta_of_channel received short response ({0} bytes): {1}".format(len(data), data))
            return None, rt
        else:
            return struct.unpack('!f', data[12:16])[0], rt #slices exactly 4 bytes instead of everything from byte 12 onwards, so struct.unpack always gets the right amount

    def get_tvalue_of_channel(self, channel, chromophore, contrast):
        sizecontrast = struct.pack('!i', len(contrast))
        contrast = arr.array('i', contrast)
        channel = struct.pack('!i', channel)
        chromophore = struct.pack('!i', chromophore)
        contrast = contrast.tobytes()
        data, rt = self.request_data("tGettValueOfChannel", channel,
                                     chromophore, sizecontrast, contrast)
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!f', data[12 + len(contrast):])[0], rt

    def get_protocol_condition(self, frame):
        frame = struct.pack('!i', frame)
        data, rt = self.request_data("tGetProtocolCondition", frame)
        if data is None:
            return None, rt
        elif data[:14] == b"Wrong request!":
            raise Exception("Wrong request!: '{0}'".format(data[19:-1]))
        else:
            return struct.unpack('!i', data[4:])[0], rt
