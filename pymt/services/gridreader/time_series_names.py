import collections
import re

_TIME_SERIES_NAME_RE_PATTERN = r"(?P<name>[a-zA-Z_]+)@t=(?P<time_stamp>\d+)$"
_TIME_SERIES_NAME_RE = re.compile(_TIME_SERIES_NAME_RE_PATTERN)


class Error(Exception):
    pass


class TimeSeriesNameError(Error):
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return "invalid time series name: %s" % self._name


class TimeStampError(Error):
    def __init__(self, time_stamp):
        self._time_stamp = time_stamp

    def __str__(self):
        return "invalid time stamp: %s" % self._time_stamp


def time_stamp_as_string(time_stamp):
    if isinstance(time_stamp, str):
        try:
            return str(int(time_stamp))
        except ValueError:
            raise TimeStampError(time_stamp)
    elif isinstance(time_stamp, int):
        return str(time_stamp)
    else:
        raise TimeStampError(time_stamp)


def split(name):
    match = _TIME_SERIES_NAME_RE.match(name)
    if match is not None:
        return match.group("name"), int(match.group("time_stamp"))
    else:
        raise TimeSeriesNameError(name)


def unsplit(name, time_stamp):
    return name + "@t=" + time_stamp_as_string(time_stamp)


def extract_time_stamps_from_names(names, ordering="ascending", prefix=""):
    if ordering not in ["ascending", "descending", None]:
        raise TypeError("ordering not understood: %s" % ordering)

    time_stamps = collections.defaultdict(list)

    for name in names:
        if name.startswith(prefix):
            try:
                (base, time_stamp) = split(name)
            except TimeSeriesNameError:
                pass
            else:
                time_stamps[base].append(time_stamp)

    if ordering is not None:
        for name in time_stamps:
            time_stamps[name].sort(reverse=(ordering == "descending"))

    return time_stamps


def sort_time_series_names(names, ordering="ascending", prefix=""):
    ordered_names = dict()

    time_stamps = extract_time_stamps_from_names(
        names, ordering=ordering, prefix=prefix
    )
    for (name, stamps) in time_stamps.items():
        ordered_names[name] = [unsplit(name, stamp) for stamp in stamps]

    return ordered_names


def get_time_series_names(names):
    unique_names = set()

    for name in names:
        try:
            unique_names.add(split(name)[0])
        except TimeSeriesNameError:
            pass

    return unique_names
