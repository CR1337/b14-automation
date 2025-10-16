from typing import Any
import streamlit as st
import pandas as pd
from webapp.renderers.renderer import Renderer


class TableInputRenderer(Renderer):

    def render(self, app_io: Any):
        file = st.file_uploader(
            label=app_io.name[self.language.key],
            type=["csv"],
            accept_multiple_files=False,
            key=app_io.key
        )
        if file:
            app_io.value = pd.read_csv(
                file,
                sep=app_io.parameters.get("sep"),
                delimiter=app_io.parameters.get("delimiter")
            )