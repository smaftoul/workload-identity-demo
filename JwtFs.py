#!/usr/bin/env python
# run with python3 JwtFs.py /mnt/jwtfs /path/to/private.pem
from __future__ import print_function, absolute_import, division

import logging

from errno import ENOENT
from stat import S_IFDIR, S_IFREG

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context

import psutil
import datetime
import requests
from pathlib import Path
from authlib.jose import jwt

attrs = [
    "cmdline",
    "cpu_percent",
    "cpu_times",
    "create_time",
    "cwd",
    "exe",
    "gids",
    "memory_full_info",
    "memory_info",
    "memory_percent",
    "name",
    "nice",
    "num_ctx_switches",
    "num_fds",
    "num_threads",
    "pid",
    "ppid",
    "status",
    "terminal",
    "threads",
    "uids",
    "username",
]


def claimFromProcess(pid):
    process_info = psutil.Process(pid).as_dict(attrs=attrs)
    claim = {
        "aud": ["platform"],
        "iss": "https://some-address",
        "sub": "some-workload",
        "weather": {
            "paris": requests.get("http://wttr.in/Paris?format=j1").json()[
                "current_condition"
            ][0]["weatherDesc"][0]["value"],
        },
        "process": process_info,
        "iat": int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()),
        "exp": int(
            (
                datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(days=1)
            ).timestamp()
        ),
    }
    return claim


class JwtFs(LoggingMixIn, Operations):
    "Filesystem that provide workload identity as a JWT."

    def __init__(self, key_file, *args, **kwargs):
        self.key_data = Path(key_file).read_text(encoding="utf-8")
        self.out = {}
        super(JwtFs, self).__init__(*args, **kwargs)

    def getattr(self, path, fh=None):
        if path == "/":
            st = dict(st_mode=(S_IFDIR | 0o755), st_nlink=2)
        elif path == "/jwt":
            _, _, pid = fuse_get_context()
            self.out.update(
                {
                    pid: jwt.encode(
                        header={"alg": "RS256"},
                        payload=claimFromProcess(pid),
                        key=self.key_data,
                    )
                }
            )
            size = len(self.out[pid])
            st = dict(st_mode=(S_IFREG | 0o444), st_size=size)
        else:
            raise FuseOSError(ENOENT)
        st["st_ctime"] = st["st_mtime"] = st["st_atime"] = 0
        return st

    def read(self, path, size, offset, fh):
        if path == "/jwt":
            _, _, pid = fuse_get_context()
            if pid not in self.out:
                self.out.update(
                    {
                        pid: jwt.encode(
                            header={"alg": "RS256"},
                            payload=claimFromProcess(pid),
                            key=self.key_data,
                        )
                    }
                )
            return self.out[pid][offset : offset + size]
        raise RuntimeError("unexpected path: %r" % path)

    def readdir(self, path, fh):
        return [".", "..", "jwt"]

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("mount")
    parser.add_argument("key_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(
        JwtFs(key_file=args.key_file),
        args.mount,
        foreground=True,
        ro=True,
        allow_other=True,
        nothreads=True,
    )
