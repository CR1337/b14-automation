from typing import Any
import streamlit as st
from datetime import date
from webapp.renderers.renderer import Renderer


class DateInputRenderer(Renderer):

    def render(self, app_io: Any):
        app_io.value = st.date_input(
            label=app_io.name[self.language.key],
            value=app_io.value,
            min_value=app_io.parameters.get("min_value"),
            max_value=app_io.parameters.get("max_value"),
            format=app_io.parameters.get("format", "YYYY-MM-DD"),
            key=app_io.key
        ) or date.today()  