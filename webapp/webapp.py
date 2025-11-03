import os
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from apps.app_registry import apps
from webapp.authentication import Authentication
from webapp.app import App
from webapp.app_messenger import AppMessenger, MESSENGERS
from streamlit_autorefresh import st_autorefresh
from webapp.localization import Localization, LANGUAGES
from webapp.thread import ThreadWithResult
from webapp.app_result import AppResult


class WebApp:
    LOCALIZATION_FILENAME: str = os.path.join("localization", "localization.json")
    BUSY_REFRESH_RATE: int = 500  # ms
    HOUR_GLASSES: str = "⌛⏳"

    _localization: Localization

    def __init__(self):
        self._localization = Localization(self.LOCALIZATION_FILENAME)

    def run(self):
        self._initialize_session_state()
        self._render_sidebar()
        self._render_app()
        self._tick()

    def _tick(self):
        st.session_state["tick"] += 1

    def _initialize_session_state(self):
        if st.session_state.get("language") is None:
            st.session_state["language"] = LANGUAGES["de"]
        if st.session_state.get("tick") is None:
            st.session_state["tick"] = 0
        if st.session_state.get("selected_app") is None:
            st.session_state["selected_app"] = apps[0]
        if st.session_state.get("app_data") is None:
            st.session_state["app_data"] = {}
        if st.session_state.get("busy") is None:
            st.session_state["busy"] = False

        for app in apps:
            if st.session_state["app_data"].get(app.key) is None:
                st.session_state["app_data"][app.key] = {
                    "state": "input",
                    "message": None,
                    "future": None,
                }

    def _render_sidebar(self):
        language = st.session_state["language"]
        with st.sidebar:
            st.header(self._localization.get_translation("language"), divider="gray")
            # language_keys = Localization.get_all_languages()
            # flags_names = (
            #     (
            #         Localization.get_language_flag(lang),
            #         Localization.get_language_name(lang),
            #     )
            #     for lang in language_keys
            # )

            language_options = [f"{language.flag} {language.name}" for language in LANGUAGES.values()]

            # language_options = [f"{flag} {name}" for flag, name in flags_names]
            language_index = list(LANGUAGES.values()).index(language)

            selection = st.selectbox(
                label=self._localization.get_translation("language"),
                options=language_options,
                index=language_index,
                label_visibility="hidden",
            )
            selection_index = language_options.index(selection)
            new_language = list(LANGUAGES.values())[selection_index]
            if new_language != language:
                st.session_state["language"] = new_language
                st.rerun()

            st.header(self._localization.get_translation("apps"), divider="gray")
            for app in apps:
                if app.authentication_required and not Authentication.is_authenticated():
                    continue
                if st.button(
                    label=app.name[language.key],
                    key=app.key,
                    disabled=st.session_state["busy"],
                    use_container_width=True,
                    type="secondary" if app.authentication_required else "primary",
                ):
                    st.session_state["selected_app"] = app
                    st.rerun()

            st.header(self._localization.get_translation("administration"), divider="gray")
            if Authentication.is_authenticated():
                st.write(self._localization.get_translation("logged_in"))
                if st.button(
                    label=self._localization.get_translation("logout"),
                    key="logout_button",
                    use_container_width=True,
                    type="primary"
                ):
                    Authentication.invalidate()
                    st.rerun()
            else:
                if st.button(
                    label=self._localization.get_translation("login"),
                    key="login_button",
                    use_container_width=True,
                    type="primary"
                ):
                    self._authentication_dialog()

    @st.dialog(" ")
    def _authentication_dialog(self):
        password = st.text_input(self._localization.get_translation("password"), type="password")
        if st.button(self._localization.get_translation("login"), type="primary"):
            Authentication.authenticate(password)
            del password
            st.rerun()

    def _render_app(self):
        language = st.session_state["language"]
        selected_app = st.session_state["selected_app"]
        st.header(selected_app.name[language.key], divider="gray")
        match st.session_state["app_data"][selected_app.key]["state"]:
            case "input":
                self._render_app_input(selected_app)
            case "busy":
                self._render_app_busy(selected_app)
            case "output":
                self._render_app_output(selected_app)
            case _:
                pass

    def _run_app(self, app: App, messenger: AppMessenger) -> AppResult:
        app.set_messenger(messenger)

        try:
            app.run()
        except Exception as e:
            result = AppResult("run", False, e, app.to_dict())
            messenger.set_is_done()
            return result

        result = AppResult("done", True, None, app.to_dict())
        messenger.set_is_done()
        messenger.clear_message_key()
        return result

    def _render_app_input(self, app: App):
        valid_input, value_changed = app.render_input()
        if value_changed:
            st.rerun()
        st.divider()
        if st.button(
            self._localization.get_translation("run_app"),
            key=f"start_{app.key}",
            disabled=not valid_input,
            use_container_width=True,
            type="primary",
        ):
            messenger = AppMessenger(app.localization)
            MESSENGERS[app.key] = messenger
            st.session_state["app_data"][app.key]["state"] = "busy"

            thread = ThreadWithResult(
                target=self._run_app, args=(app, messenger)
            )
            add_script_run_ctx(thread, get_script_run_ctx())
            thread.start()
            st.session_state["app_data"][app.key]["future"] = thread

            st.rerun()

    def _render_app_busy(self, app: App):
        st.session_state["busy"] = True
        messenger = MESSENGERS[app.key]
        st_autorefresh(interval=self.BUSY_REFRESH_RATE, key="autorefresh")
        st.markdown(
            f"""
            <div>
                <strong>{self.HOUR_GLASSES[st.session_state["tick"] % 2]} {messenger.message}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if messenger.is_done:
            st.session_state["busy"] = False
            st.session_state["app_data"][app.key]["state"] = "output"
            st.rerun()

    def _render_app_output(self, app: App):
        result = st.session_state["app_data"][app.key]["future"].result()

        if result.success:
            app.render_output()
        else:
            st.markdown(
                body=f":red[{self._localization.get_translation('unexpected_error_message')}]"
            )
            st.json(result.to_dict())

        st.divider()
        if st.button(
            self._localization.get_translation("restart"),
            key=f"restart_{app.key}",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["app_data"][app.key]["state"] = "input"

            st.rerun()
