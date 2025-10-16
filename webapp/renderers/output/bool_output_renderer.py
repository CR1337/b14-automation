from typing import Any
from webapp.renderers.renderer import Renderer
import streamlit as st
from webapp.localization import Localization


class BoolOutputRenderer(Renderer):

    def render(self, app_io: Any):
        st.text_input(
            label=app_io.name[self.language.key],
            value=Localization.get_translation("yes" if app_io.value else "no"),
            key=app_io.key,
            disabled=True
        )