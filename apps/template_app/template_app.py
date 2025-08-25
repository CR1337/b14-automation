import time

# You always have to import this.
from webapp.app import App, ValidatorSet


# Remember to rename the class in this file when you copy it to create a new app!


class TemplateApp(App):
    # This class represents an app. Here you initialize, run and destroy the app.
    # Next to this file you need two more files: `config.json` and `localization.json`.
    # The second one is optional but recommended.
    # 
    # The documentation for this you you can find in `doc/creating_a_new_app.md`

    def initialize(self, language: str):
        # Here you can initialize your app. You also have access to the language 
        # set in the streamlits sidebar. You can set the apps language property
        # if you want to use it. It defaults to `None`.
        self.language = language
    
    def run(self):
        # Here your app does all of its work. You can read user input with
        # `self.get_input` and set output values with `self.set_output`.
        #
        # While the app is busy you can display status messages.You can do that
        # with `self.messenger.set_message`. Note that this method does not take
        # a `str` but a `dict` that maps language codes to messages like this:
        # 
        # {
        #     "en": "Hello",
        #     "de": "Hallo"
        # } 
        #
        # If you are using the `localization.json` file you can get such a dict
        # with `self.get_translations`. 
        #
        # `self.get_translation` (without the `s` at the end) gives you the
        # string for the currently set laguage (`self.language`).
        #
        # If you want to use code shared acorss multiple apps put it into the
        # `lib` directory and import it from there.
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
        # Here you cleanup after your app. You can clear the status message
        # using `self.messenger.clear_message` for example.
        assert self.messenger is not None
        self.messenger.clear_message()

    @staticmethod
    def input_validators() -> ValidatorSet:
        # Here you can define input validators. For an input key you provide
        # a `Callable` that takes a value and returns a `bool`. It should return
        # `True` if the value is valid, else `False`.
        #
        # You don't have to provide a validator for each key. You can also
        # return an empty `dict`.
        return {
            "name": lambda n: n != "foo",  # The name cannot be "foo".
            "greeting": lambda g: g.startswith("H")  # The greeting has to start with a capital "H".
        }
    
    @staticmethod
    def output_validators() -> ValidatorSet:
        # Here you can define output validators. They work the same as input
        # validators but for outputs.
        return {}
    