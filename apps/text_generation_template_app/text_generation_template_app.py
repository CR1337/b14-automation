
from webapp.app import App
from webapp.github_storage import GithubStorage
from typing import Dict, Callable, Any


class TextGenerationTemplateApp(App):

    TEMPLATE_FILENAME: str = "data/erwerbslosigkeit_template.txt"
    
    def run(self):
        assert self.messenger is not None

        self.messenger.set_message_key("updating_template")

        template = self.get_input("template")
        storage = GithubStorage(self.TEMPLATE_FILENAME)
        success, status = storage.load_content()

        if not success:
            self.set_output("status", status)
            return
        
        assert isinstance(template, str)
        success = storage.store_content(template)

        status = self.localization.get_translation("success" if success else "error")
        self.set_output("status", status)

    @staticmethod
    def input_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}
    
    @staticmethod
    def output_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}