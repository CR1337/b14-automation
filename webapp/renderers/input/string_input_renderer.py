from typing import Any
import streamlit as st
from webapp.renderers.renderer import Renderer


class StringInputRenderer(Renderer):

    def render(self, app_io: Any):
        value = None
        value_filename = app_io.parameters.get("value_from_file")
        if value_filename:
            with open(value_filename, 'r') as file:
                value = file.read()


        if app_io.parameters.get("multiline", False):
            app_io.value = st.text_area(
                label=app_io.name[self.language.key], 
                value=value or app_io.value, 
                max_chars=app_io.parameters.get("max_chars"),
                key=app_io.key,
                placeholder=app_io.parameters.get("placeholder")
            )
        else:
            app_io.value = st.text_input(
                label=app_io.name[self.language.key], 
                value=value or app_io.value, 
                max_chars=app_io.parameters.get("max_chars"),
                key=app_io.key,
                type=app_io.parameters.get("type", "default"),
                placeholder=app_io.parameters.get("placeholder")
            )