import time
import io
import zipfile
from webapp.app import App
from typing import Dict, Callable, Any

from lib.eu_tables_by_topic.eu_tables_by_topic import build_tables


class EuTablesByTopicApp(App):

    def initialize(self, language: str):
        assert self.messenger is not None
        self.language = language
        self.messenger.set_message(self.get_translations("initializing"))
        time.sleep(1)
    
    def run(self):
        assert self.messenger is not None
        self.messenger.set_message(self.get_translations("generating_tables"))

        language = self.get_input("language_selection")
        match language:
            case 0:  # german
                language_id = "de"
            case _:  # else english
                language_id = "en" 
                
        tables = build_tables(language_id)

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for table_id, file_bytes in tables.items():
                filename = f"{table_id}.xlsx"
                zf.writestr(filename, file_bytes)

        zip_buffer.seek(0)
        zip_bytes = zip_buffer.getvalue()

        self.set_output("status", self.get_translation("status_success"))
        self.set_output("file", zip_bytes)
        
    
    def destroy(self):
        assert self.messenger is not None
        self.messenger.clear_message()

    @staticmethod
    def input_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}
    
    @staticmethod
    def output_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}
    