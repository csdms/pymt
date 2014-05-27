from scipy import interpolate

from .time_series_names import sort_time_series_names


def get_time_series_values(field, ordering='ascending', prefix=''):
    values = defaultdict(list)

    names = sort_time_series_names(field, ordering=ordering, prefix=prefix)

    for (var_name, ordered_names) in names.items():
        for name in ordered_names:
            values[var_name].append(field.get_values(name))

    return values


def get_field_values(fields, names):
    values = []
    for name in names:
        values.append(fields.get_values(name))
    return values


def create_interpolators(times, fields, prefix='', kind='linear'):
    interpolators = {}

    names = sort_time_series_names(fields.keys(), prefix=prefix,
                                   ordering='ascending')

    for (var_name, ordered_names) in names.items():
        interpolators[var_name] = create_interpolator(fields,
                                                      zip(ordered_names, times),
                                                      kind=kind)

    return interpolators


def create_interpolator(fields, time_stamps, kind='linear'):
    names, times = zip(*time_stamps)

    values = get_field_values(fields, names)
    return interpolate.interp1d(times, values, axis=0, kind=kind)
