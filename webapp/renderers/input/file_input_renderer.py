from typing import Any
import streamlit as st
from webapp.renderers.renderer import Renderer
from webapp.app_io.app_io_type import AppIOType


class FileInputRenderer(Renderer):

    def render(self, app_io: Any):
        file = st.file_uploader(
            label=app_io.name[self.language.key],
            type=app_io.parameters.get("type"),
            accept_multiple_files=False,
            key=app_io.key
        )
        if file:
            if app_io.type == AppIOType.FILE:
                app_io.value = file.getvalue().decode(app_io.parameters.get("encoding", "utf-8"))
            else:
                app_io.value = file.getvalue()