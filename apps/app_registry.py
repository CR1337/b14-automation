from webapp.app import App
from typing import List

# from apps.template_app.template_app import TemplateAppFactory
from apps.text_generation_app.text_generation_app import TextGenerationAppFactory
from apps.oecd_inflation_app.oecd_inflation_app import OecdInflationAppFactory
from apps.eu_tables_by_topic_app.eu_tables_by_topic_app import EuTablesByTopicAppFactory
from apps.eu_tables_by_country_app.eu_tables_by_country_app import EuTablesByCountryAppFactory


apps: List[App] = [
    # TemplateAppFactory().create(),
    TextGenerationAppFactory().create(),
    OecdInflationAppFactory().create(),
    EuTablesByTopicAppFactory().create(),
    EuTablesByCountryAppFactory().create()
]
