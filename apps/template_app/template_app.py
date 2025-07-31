import time
from webapp.app import App
from webapp.app_factory import AppFactory


class TemplateApp(App):

    def initialize(self, language: str):
        self.language = language
    
    def run(self):
        assert self.messenger is not None
        self.messenger.set_message(self.get_translations("reading_name"))
        time.sleep(2)
        name = self.get_input("name")
        self.messenger.set_message(self.get_translations("creating_greeting"))
        time.sleep(2)
        greeting = self.get_translation("hello").format(name=name)
        self.messenger.set_message(self.get_translations("outputting_greeting"))
        time.sleep(2)
        self.set_output("greeting", greeting)
    
    def destroy(self):
        assert self.messenger is not None
        self.messenger.clear_message()


class TemplateAppFactory(AppFactory):

    def create(self) -> App:
        self.add_input_validator("name", lambda n: n != "foo")
        self.add_input_validator("greeting", lambda g: g.startswith("H"))
        return TemplateApp(*self.config_from_file())
