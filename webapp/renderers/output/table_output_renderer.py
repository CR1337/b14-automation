from typing import Any
from webapp.renderers.renderer import Renderer
import streamlit as st


class TableOutputRenderer(Renderer):

    def render(self, app_io: Any):
        st.dataframe(
            data=app_io.value.get(),
            key=app_io.key
        )