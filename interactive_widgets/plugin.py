import binascii
import bs4
import hashlib
import mkdocs
import os
import pathlib
import re
import shlex
import typing

from .button import ButtonWidget
from .image_viewer import ImageViewerWidget
from .terminal import TerminalWidget
from .text_editor import TextEditorWidget
from .text_viewer import TextViewerWidget


log = mkdocs.plugins.log.getChild('interactive-widgets')


class Plugin(mkdocs.plugins.BasePlugin):

    config_scheme = (
        ('backend_type', mkdocs.config.config_options.Type(str, default='docker')),
    )

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

        # for index, widget_element in enumerate(soup.find_all(['x-button', 'x-image-viewer', 'x-terminal', 'x-text-editor', 'x-text-viewer'])):
        #     if widget_element.name == 'x-button':
        #         print(index, widget_element)
        #     # self.replace_button(index, widget_element)
        # for index, widget_element in enumerate(soup.find_all('x-image-viewer')):
        #     print(index, widget_element)
        #     # self.replace_image_viewer(index, widget_element)
        # for index, widget_element in enumerate(soup.find_all('x-terminal')):
        #     print(index, widget_element)
        #     # self.replace_terminal(index, widget_element)
        # for index, widget_element in enumerate(soup.find_all('x-text-editor')):
        #     print(index, widget_element)
        #     # self.replace_text_editor(index, widget_element)
        # for index, widget_element in enumerate(soup.find_all('x-text-viewer')):
        #     print(index, widget_element)
        #     # self.replace_text_viewer(index, widget_element)

        # print(page.__dict__)
        # page_file: mkdocs.structure.files.File = page.file
        # print(page_file)
        # print(html, page, args, kwargs)
        return soup.encode_contents(formatter='html5').decode()
