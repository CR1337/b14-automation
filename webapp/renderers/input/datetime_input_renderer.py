from typing import Any
import streamlit as st
from datetime import datetime, timedelta, date, time
from webapp.renderers.renderer import Renderer


class DatetimeInputRenderer(Renderer):

    def render(self, app_io: Any):
        columns = st.columns(2)
        date_ = columns[0].date_input(
            label=app_io.name[self.language.key],
            value=app_io.value.get(),
            min_value=app_io.parameters.get("min_value"),
            max_value=app_io.parameters.get("max_value"),
            format=app_io.parameters.get("format", "YYYY-MM-DD"),
            key=app_io.key
        ) or date.today()
        time_ = columns[0].time_input(
            label="",
            value=app_io.value.get(),
            key=app_io.key,
            step=app_io.parameters.get("step", timedelta(minutes=15))
        ) or time(0, 0, 0, 0)
        date_time = datetime.combine(date_, time_)
        return date_time