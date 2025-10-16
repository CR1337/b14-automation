from typing import Any
from datetime import datetime
from webapp.renderers.renderer import Renderer
import streamlit as st


class DatetimeOutputRenderer(Renderer):

    def render(self, app_io: Any):
        st.text_input(
            label=app_io.name[self.language.key],
            value=datetime.strftime(app_io.value, "%Y-%m-%d %H:%M"),
            key=app_io.key,
            disabled=True
        )