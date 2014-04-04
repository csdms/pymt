import os


def file_is_executable(path_to_file, mode=os.F_OK | os.X_OK):
    return os.path.isfile(path_to_file) and os.access(path_to_file, mode)


def find_executable_in_paths(prog, paths):
    for path in paths:
        path_to_file = os.path.join(path, prog)
        if file_is_executable(path_to_file):
            return path_to_file
    return None


def which(prog, mode=os.F_OK | os.X_OK, path=None):
    if os.path.isabs(prog) and file_is_executable(prog):
        return prog
    else:
        if path is None:
            try:
                path = os.environ['PATH'].split(os.pathsep)
            except KeyError:
                path = os.defpath.split(os.pathsep)
        return find_executable_in_paths(prog, path)
    return None
