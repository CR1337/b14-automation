from typing import Any
import streamlit as st
from webapp.renderers.renderer import Renderer


class BoolInputRenderer(Renderer):

    def render(self, app_io: Any):
        return st.checkbox(
            label=app_io.name[self.language.key],
            value=bool(app_io.value.get()),
            key=app_io.key
        )
