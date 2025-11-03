from typing import Any
from datetime import datetime
from webapp.renderers.renderer import Renderer
import streamlit as st


class FileOutputRenderer(Renderer):

    def render(self, app_io: Any):
        filename = app_io.parameters.get("filename", "data.txt")
        if app_io.parameters.get("prefix_language", False):
            filename = f"{self.language}_{filename}"
        if app_io.parameters.get("prefix_datetime", False):
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        st.download_button(
            label=app_io.name[self.language.key],
            data=str(app_io.value.get()),
            file_name=filename,
            mime=app_io.parameters.get("mime", "text/plain"),
            key=app_io.key,
            use_container_width=True
        )