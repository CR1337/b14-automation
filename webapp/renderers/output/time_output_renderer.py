from typing import Any
from datetime import time
from webapp.renderers.renderer import Renderer
import streamlit as st


class TimeOutputRenderer(Renderer):

    def render(self, app_io: Any):
        st.text_input(
            label=app_io.name[self.language.key],
            value=time.strftime(app_io.value, "%H:%M"),
            key=app_io.key,
            disabled=True
        )