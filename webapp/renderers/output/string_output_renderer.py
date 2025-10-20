from typing import Any
from webapp.renderers.renderer import Renderer
import streamlit as st


class StringOutputRenderer(Renderer):

    def render(self, app_io: Any):
        if app_io.parameters.get("multiline", False):
            st.text_area(
                label=app_io.name[self.language.key],
                value=str(app_io.value.get()),
                key=app_io.key,
                disabled=True,
                height="content"  # type: ignore
            )
        else:
            st.text_input(
                label=app_io.name[self.language.key],
                value=str(app_io.value.get()),
                key=app_io.key,
                disabled=True
            )