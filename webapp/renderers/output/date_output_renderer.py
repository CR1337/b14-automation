from typing import Any
from datetime import date
from webapp.renderers.renderer import Renderer
import streamlit as st


class DateOutputRenderer(Renderer):

    def render(self, app_io: Any):
        st.text_input(
            label=app_io.name[self.language.key],
            value=date.strftime(app_io.value.get(), "%Y-%m:%d"),
            key=app_io.key,
            disabled=True
        )