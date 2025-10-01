
from webapp.app import App
from webapp.github_storage import GithubStorage
from typing import Dict, Callable, Any


class TextGenerationTemplateApp(App):

    TEMPLATE_FILENAME: str = "data/erwerbslosigkeit_template_test.txt"

    def initialize(self, language: str):
        assert self.messenger is not None
        self.language = language        
    
    def run(self):
        assert self.messenger is not None

        self.messenger.set_message({
            "de":"Aktualisiere Template...", 
            "en": "Updating template..."
        })


        template = self.get_input("template")
        storage = GithubStorage(self.TEMPLATE_FILENAME)
        success, status = storage.load_content()

        if not success:
            self.set_output("status", status)
            return
        
        assert isinstance(template, str)
        success = storage.store_content(template)
        if not success:
            self.set_output("status", "Error updating template.")

        if self.language == "de":
            self.set_output("status", "Template erfolgreich aktualisiert.")
        else:
            self.set_output("status", "Template successfully updated.")
        
    
    def destroy(self):
        assert self.messenger is not None
        self.messenger.clear_message()

    @staticmethod
    def input_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}
    
    @staticmethod
    def output_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}