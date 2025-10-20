from typing import Any
import streamlit as st
from datetime import timedelta, time
from webapp.renderers.renderer import Renderer


class TimeInputRenderer(Renderer):

    def render(self, app_io: Any):
        return st.time_input(
            label="",
            value=app_io.value.get(),
            key=app_io.key,
            step=app_io.parameters.get("step", timedelta(minutes=15))
        ) or time(0, 0, 0, 0)     