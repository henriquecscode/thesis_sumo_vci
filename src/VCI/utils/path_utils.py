import os

# Returns the basename of a file without extensions
def true_basename(path: str) -> tuple[str, str]:
    full_exts =[]
    basename, ext = os.path.splitext(os.path.basename(path))
    full_exts.append(ext)
    while ext:
        basename, ext = os.path.splitext(basename)
        full_exts.append(ext)
    full_exts_str = ''.join(reversed(full_exts))
    return (basename, full_exts_str)