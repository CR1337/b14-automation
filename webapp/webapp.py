import os
import streamlit as st
from apps.app_registry import apps
from webapp.authentication import Authentication
from webapp.app import App
from webapp.app_messenger import AppMessenger, MESSENGERS
from streamlit_autorefresh import st_autorefresh
from webapp.localization import Localization
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
            st.session_state["language"] = "de"
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
            st.header(self._localization.get("language", language), divider="gray")
            language_keys = self._localization.get_all_languages()
            flags_names = (
                (
                    self._localization.get_language_flag(lang),
                    self._localization.get_language_name(lang),
                )
                for lang in language_keys
            )
            language_options = [f"{flag} {name}" for flag, name in flags_names]
            language_index = language_keys.index(language)

            selection = st.selectbox(
                label=self._localization.get("language", language),
                options=language_options,
                index=language_index,
                label_visibility="hidden",
            )
            selection_index = language_options.index(selection)
            new_language = language_keys[selection_index]
            if new_language != language:
                st.session_state["language"] = new_language
                st.rerun()

            st.header(self._localization.get("apps", language), divider="gray")
            for app in apps:
                if app.authentication_required and not Authentication.is_authenticated():
                    continue
                if st.button(
                    label=app.name[language],
                    key=app.key,
                    disabled=st.session_state["busy"],
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state["selected_app"] = app
                    st.rerun()

            st.header(self._localization.get("administration", language), divider="gray")
            if Authentication.is_authenticated():
                st.write(self._localization.get("logged_in", language))
                if st.button(
                    label=self._localization.get("logout", language),
                    key="logout_button",
                    use_container_width=True,
                    type="primary"
                ):
                    Authentication.invalidate()
                    st.rerun()
            else:
                if st.button(
                    label=self._localization.get("login", language),
                    key="login_button",
                    use_container_width=True,
                    type="primary"
                ):
                    self._authentication_dialog()

    @st.dialog(" ")
    def _authentication_dialog(self):
        language = st.session_state["language"]
        password = st.text_input(self._localization.get("password", language), type="password")
        if st.button(self._localization.get("login", language), type="primary"):
            Authentication.authenticate(password)
            del password
            st.rerun()

    def _render_app(self):
        language = st.session_state["language"]
        selected_app = st.session_state["selected_app"]
        st.header(selected_app.name[language], divider="gray")
        match st.session_state["app_data"][selected_app.key]["state"]:
            case "input":
                self._render_app_input(selected_app)
            case "busy":
                self._render_app_busy(selected_app)
            case "output":
                self._render_app_output(selected_app)
            case _:
                pass

    def _run_app(self, app: App, messenger: AppMessenger, language: str):
        app.set_messenger(messenger)

        for func, stage, args, kwargs in zip(
            (app.initialize, app.run, app.destroy),
            ("initialize", "run", "destroy"),
            ((language,), (), ()),
            ({}, {}, {}),
        ):
            try:
                func(*args, **kwargs)
            except Exception as e:
                result = AppResult(stage, False, e, app.to_dict())
                messenger.set_is_done()
                return result

        result = AppResult("done", True, None, app.to_dict())
        messenger.set_is_done()
        return result

    def _render_app_input(self, app: App):
        language = st.session_state["language"]
        valid_input, value_changed = app.render_input(language)
        if value_changed:
            st.rerun()
        st.divider()
        if st.button(
            self._localization.get("run_app", language),
            key=f"start_{app.key}",
            disabled=not valid_input,
            use_container_width=True,
            type="primary",
        ):
            messenger = AppMessenger()
            MESSENGERS[app.key] = messenger
            st.session_state["app_data"][app.key]["state"] = "busy"

            thread = ThreadWithResult(
                target=self._run_app, args=(app, messenger, language)
            )
            thread.start()
            st.session_state["app_data"][app.key]["future"] = thread

            st.rerun()

    def _render_app_busy(self, app: App):
        language = st.session_state["language"]
        st.session_state["busy"] = True
        messenger = MESSENGERS[app.key]
        st_autorefresh(interval=self.BUSY_REFRESH_RATE, key="autorefresh")
        st.markdown(
            f"""
            <div>
                <strong>{self.HOUR_GLASSES[st.session_state["tick"] % 2]} {messenger.get_message(language)}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if messenger.is_done:
            st.session_state["busy"] = False
            st.session_state["app_data"][app.key]["state"] = "output"
            st.rerun()

    def _render_app_output(self, app: App):
        language = st.session_state["language"]

        result = st.session_state["app_data"][app.key]["future"].result()

        if result.success:
            app.render_output(language)
        else:
            st.markdown(
                body=f":red[{self._localization.get('unexpected_error_message', language)}]"
            )
            st.json(result.to_dict())

        st.divider()
        if st.button(
            self._localization.get("restart", language),
            key=f"restart_{app.key}",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["app_data"][app.key]["state"] = "input"

            st.rerun()
