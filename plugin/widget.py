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

    def get_head_prepends(self) -> typing.List[bs4.element.Tag]:
        script = self.soup.new_tag('script')
        script.append('''
            const currentUrl = new URL(window.location);
            const currentUrlSearchParams = new URLSearchParams(currentUrl.search);
            const currentRoomName = currentUrlSearchParams.get("roomName");
            // https://gist.github.com/johnelliott/cf77003f72f889abbc3f32785fa3df8d
            if (currentRoomName === null || !currentRoomName.match(new RegExp(/^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i))) {
                // https://gist.github.com/outbreak/316637cde245160c2579898b21837c1c
                const getRandomSymbol = (symbol) => {
                    var array;
                    if (symbol === "y") {
                    array = ["8", "9", "a", "b"];
                    return array[Math.floor(Math.random() * array.length)];
                    }
                    array = new Uint8Array(1);
                    window.crypto.getRandomValues(array);
                    return (array[0] % 16).toString(16);
                }
                const newRoomName = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, getRandomSymbol);
                currentUrlSearchParams.set("roomName", newRoomName);
                currentUrl.search = currentUrlSearchParams;
                window.location.replace(currentUrl.toString());
            }
        ''')
        return [script]

    def get_head_appends(self) -> typing.List[bs4.element.Tag]:
        return []

    def get_body_prepends(self) -> typing.List[bs4.element.Tag]:
        script = self.soup.new_tag('script')
        script.append(
            'const roomConnection = new RoomConnection(currentRoomName);',
        )
        return [script]

    def get_body_appends(self) -> typing.List[bs4.element.Tag]:
        return []
