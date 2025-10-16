from typing import Any
import streamlit as st
from webapp.renderers.renderer import Renderer


class FloatInputRenderer(Renderer):

    def render(self, app_io: Any):
        app_io.value = st.number_input(
            label=app_io.name[self.language.key], 
            value=app_io.value, 
            min_value=app_io.parameters.get("min_value"),
            max_value=app_io.parameters.get("max_value"),
            step=app_io.parameters.get("step", 0.001),
            format=app_io.parameters.get("format")
        )
