from webapp.app import App
from typing import List, Type

from webapp.app_factory import AppFactory

# Here you have to import your App:
from apps.text_generation_app.text_generation_app import TextGenerationApp
from apps.oecd_inflation_app.oecd_inflation_app import OecdInflationApp
from apps.eu_tables_by_topic_app.eu_tables_by_topic_app import EuTablesByTopicApp
from apps.eu_tables_by_country_app.eu_tables_by_country_app import EuTablesByCountryApp

# Next you add the App to this List:
app_classes: List[Type[App]] = [
    TextGenerationApp,
    OecdInflationApp,
    EuTablesByTopicApp,
    EuTablesByCountryApp
]

apps: List[App] = [
    AppFactory().create(
        app_class, 
        app_class.input_validators(),
        app_class.output_validators()
    )
    for app_class in app_classes
]