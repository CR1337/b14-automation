import os
import time
from datetime import date
from webapp.app import App
from webapp.github_storage import GithubStorage
from typing import Dict, Callable, Any

from lib.auto_text.erwerbslosigkeit import ErwerbslosigkeitTextGenerator


class TextGenerationApp(App):
    
    def run(self):
        assert self.messenger is not None
        self.messenger.set_message_key("initializing")
        topic_index = self.get_input("topic")
        match topic_index:
            case 0:  # unemploment rate
                storage = GithubStorage("data/erwerbslosigkeit_template.txt")
                success, template = storage.load_content()
                if not success:
                    with open(os.path.join("data", "erwerbslosigkeit_template.txt"), 'r') as file:
                        template = file.read()
                text_generator = ErwerbslosigkeitTextGenerator.construct(template)
            case _:
                raise ValueError(f"Invalid topic index: {topic_index}")
        time.sleep(2)

        self.messenger.set_message_key("loading_from_eurostat")
        date_ = self.get_input("date")
        assert isinstance(date_, date)
        year, month = date_.year, date_.month
        text_generator.request_data(year, month)
        time.sleep(1)

        self.messenger.set_message_key("creating_text")
        text = text_generator.generate()

        status = self.localization.get_translation("no_data" if text is None else "success")

        self.set_output("status", status)
        self.set_output("text", text)
        self.set_output("file", text)
        time.sleep(2)

    @staticmethod
    def input_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}
    
    @staticmethod
    def output_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}