from typing import Any
import streamlit as st
from webapp.renderers.renderer import Renderer


class SelectionInputRenderer(Renderer):

    def render(self, app_io: Any):
        options = app_io.parameters.get("options", {"de": [], "en": []})[self.language.key]
        try:
            index = app_io.value.get()
        except ValueError:
            index = 0
        selection = st.selectbox(
            label=app_io.name[self.language.key],
            options=options,
            index=index,
            key=app_io.key
        )
        if selection is None:
            return index
        return options.index(selection)