import binascii
import bs4
import hashlib
import mkdocs
import os
import pathlib
import re
import typing


class Widget:

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        self.config = config
        assert os.sep == '/', 'Assumption: posix paths for os.path'
        self.url = pathlib.PurePosixPath('/') / url
        self.soup = soup
        self.index = index
        self.tag = tag

    def _hash_inputs(self, *args) -> str:
        return hashlib.sha256(b'-'.join([
            binascii.hexlify(arg.encode("utf-8"))
            for arg in args
        ])).hexdigest()

    def _sanitize_javascript(self, data: str) -> str:
        return re.sub(r'[^0-9a-zA-Z\.\-]', lambda match: f'\\u{{{hex(ord(match.group(0)))[2:]}}}', data)

    def _relative(self, file: pathlib.PurePosixPath) -> pathlib.PurePosixPath:
        return pathlib.PurePosixPath(os.path.relpath(file, self.url))
