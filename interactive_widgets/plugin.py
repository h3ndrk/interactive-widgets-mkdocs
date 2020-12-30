import binascii
import bs4
import hashlib
import json
import mkdocs
import os
import pathlib
import re
import shlex
import shutil
import typing

from .button import ButtonWidget
from .image_viewer import ImageViewerWidget
from .terminal import TerminalWidget
from .text_editor import TextEditorWidget
from .text_viewer import TextViewerWidget


log = mkdocs.plugins.log.getChild('interactive-widgets')


class Plugin(mkdocs.plugins.BasePlugin):

    config_scheme = (
        ('backend_host', mkdocs.config.config_options.Type(str, default='*')),
        ('backend_port', mkdocs.config.config_options.Type(int, default=80)),
        ('backend_type', mkdocs.config.config_options.Type(str, default='docker')),
        ('backend_logging_level', mkdocs.config.config_options.Choice(
            ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='DEBUG',
        )),
    )

    def on_config(self, config: mkdocs.config.base.Config, *args, **kwargs):
        config['site_dir_parent'] = pathlib.Path(config['site_dir'])
        config['site_dir'] = pathlib.Path(config['site_dir']) / 'static'
        return config

    def on_pre_build(self, *args, **kwargs):
        self.backend_configuration = {
            'host': self.config['backend_host'],
            'port': self.config['backend_port'],
            'logger_name': 'Server',
            'logging_level': self.config['backend_logging_level'],
            'context': {
                'type': self.config['backend_type'],
                'logger_name': f'{self.config["backend_type"].capitalize()}Context',
            },
            'pages': {},
        }
        self.static_files = set()
        # with (pathlib.Path(__file__).parent/'static/test.txt').open()as f:
        #     print(f.read())

    def on_post_page(self, output: str, page: mkdocs.structure.pages.Page, *args, **kwargs):
        log.info(
            f'Building {page} with backend type: {self.config["backend_type"]}',
        )
        soup = bs4.BeautifulSoup(output, 'html.parser')

        widgets = [
            {
                'x-button': ButtonWidget,
                'x-image-viewer': ImageViewerWidget,
                'x-terminal': TerminalWidget,
                'x-text-editor': TextEditorWidget,
                'x-text-viewer': TextViewerWidget,
            }[tag.name](
                self.config,
                pathlib.PurePosixPath(page.url),
                soup,
                index,
                tag,
            )
            for index, tag in enumerate(soup.find_all([
                'x-button',
                'x-image-viewer',
                'x-terminal',
                'x-text-editor',
                'x-text-viewer',
            ]))
        ]

        if len(widgets) > 0:
            page_url = str(pathlib.PurePosixPath('/') / page.url)
            self.backend_configuration['pages'][page_url] = {
                'type': self.config['backend_type'],
                'logger_name_page': 'Page',
                'logger_name_room_connection': 'RoomConnection',
                'logger_name_room': f'{self.config["backend_type"].capitalize()}Room',
                'executors': {},
            }

            for widget in widgets:
                log.info(f'Processing {widget}...')
                widget.tag.replace_with(widget.get_replacement())
                for tag in widget.get_body_prepends():
                    if tag not in soup.body:
                        soup.body.insert(0, tag)
                for tag in widget.get_body_appends():
                    if tag not in soup.body:
                        soup.body.append(tag)
                for tag in widget.get_head_appends():
                    if tag not in soup.head:
                        soup.head.append(tag)
                self.backend_configuration['pages'][page_url]['executors'][widget.name] = widget.get_backend_configuration(
                )
                self.static_files |= set(widget.get_static_files())

            return soup.encode_contents(formatter='html5').decode()

        # print(page.__dict__)
        # page_file: mkdocs.structure.files.File = page.file
        # print(page_file)
        # print(html, page, args, kwargs)
        log.info(f'No widgets in {page}, building as static page')
        return output

    def on_post_build(self, config: mkdocs.config.base.Config, *args, **kwargs):
        log.info('Writing configuration.json...')
        with (config['site_dir_parent'] / 'configuration.json').open('w') as f:
            json.dump(self.backend_configuration, f, indent=2)
        log.info(f'Copying static files...')
        for static_file in self.static_files:
            source_static_file = pathlib.Path(
                __file__).parent / 'static' / pathlib.Path(static_file)
            target_static_file = config['site_dir'] / pathlib.Path(static_file)
            target_static_file.parent.mkdir(parents=True, exist_ok=True)
            if source_static_file.is_file():
                shutil.copy(
                    source_static_file,
                    target_static_file,
                )
            else:
                shutil.copytree(
                    source_static_file,
                    target_static_file,
                    dirs_exist_ok=True,
                )
