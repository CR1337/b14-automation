# Creating a new App

## Introduction
Welcome to the documentation for creating a new app within our Streamlit webapp framework. This guide will walk you through the process of creating a new app, from setting up the necessary files to registering your app in the system. Each app follows a schema where it takes inputs, processes them, and generates outputs. To create a new app, you need to create four files in a specific directory structure and register the app in the central registry.

## App Skeleton
To create a new app, follow these steps:

1. Create a new directory under `apps` with the name of your app (e.g., `apps/my_new_app`).
2. Within this directory, create the following files:
   - `__init__.py`: An empty file to make the directory a Python package.
   - `{APP_NAME}.py`: The main Python file containing the app logic (e.g., `my_new_app.py`).
   - `config.json`: The configuration file defining the inputs and outputs of the app.
   - `localization.json`: The file containing translations for different languages.

Alternatively, you can copy the directory `apps/template_app` and rename the files accordingly. This provides a good starting point.

## Configuration
The `config.json` file defines the inputs and outputs of your app. Below is a detailed explanation of each input and output type, their parameters, and how they appear in the browser.

### Input Types

#### Boolean (bool)
- **Appearance**: Checkbox.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "agree",
      "name": {
          "de": "Zustimmen",
          "en": "Agree"
      },
      "type": "bool"
  }
  ```

#### Integer (int)
- **Appearance**: Number input field.
- **Parameters**:
  - `min_value`: Minimum value (default: None).
  - `max_value`: Maximum value (default: None).
  - `step`: Increment/decrement step (default: 1).
  - `format`: Format string (default: None).
- **Example**:
  ```json
  {
      "key": "age",
      "name": {
          "de": "Alter",
          "en": "Age"
      },
      "type": "int",
      "parameters": {
          "min_value": 0,
          "max_value": 120,
          "step": 1
      }
  }
  ```

#### Float (float)
- **Appearance**: Number input field with decimal support.
- **Parameters**:
  - `min_value`: Minimum value (default: None).
  - `max_value`: Maximum value (default: None).
  - `step`: Increment/decrement step (default: 0.001).
  - `format`: Format string (default: None).
- **Example**:
  ```json
  {
      "key": "temperature",
      "name": {
          "de": "Temperatur",
          "en": "Temperature"
      },
      "type": "float",
      "parameters": {
          "min_value": -100.0,
          "max_value": 100.0,
          "step": 0.1
      }
  }
  ```

#### String (str)
- **Appearance**: Text input field or textarea (if `multiline` is true).
- **Parameters**:
  - `multiline`: Whether to use a textarea (default: False).
  - `max_chars`: Maximum number of characters (default: None).
  - `placeholder`: Placeholder text (default: None).
  - `type`: Input type (default: "default", can be "password" for password fields).
- **Example**:
  ```json
  {
      "key": "comment",
      "name": {
          "de": "Kommentar",
          "en": "Comment"
      },
      "type": "str",
      "parameters": {
          "multiline": true,
          "max_chars": 500,
          "placeholder": "Enter your comment here..."
      }
  }
  ```

#### Filename (filename)
- **Appearance**: Text input field.
- **Parameters**: Same as String.
- **Example**:
  ```json
  {
      "key": "file_path",
      "name": {
          "de": "Dateipfad",
          "en": "File Path"
      },
      "type": "filename",
      "parameters": {
          "placeholder": "Enter file path..."
      }
  }
  ```

#### URL (url)
- **Appearance**: Text input field.
- **Parameters**: Same as String.
- **Example**:
  ```json
  {
      "key": "website",
      "name": {
          "de": "Website",
          "en": "Website"
      },
      "type": "url",
      "parameters": {
          "placeholder": "https://example.com"
      }
  }
  ```

#### Datetime (datetime)
- **Appearance**: Date and time picker.
- **Parameters**:
  - `min_value`: Minimum datetime (default: None).
  - `max_value`: Maximum datetime (default: None).
  - `format`: Format string (default: "YYYY-MM-DD").
  - `step`: Time increment step (default: timedelta(minutes=15)).
- **Example**:
  ```json
  {
      "key": "event_time",
      "name": {
          "de": "Ereigniszeit",
          "en": "Event Time"
      },
      "type": "datetime",
      "parameters": {
          "format": "YYYY-MM-DD HH:mm"
      }
  }
  ```

#### Date (date)
- **Appearance**: Date picker.
- **Parameters**:
  - `min_value`: Minimum date (default: None).
  - `max_value`: Maximum date (default: None).
  - `format`: Format string (default: "YYYY-MM-DD").
- **Example**:
  ```json
  {
      "key": "birth_date",
      "name": {
          "de": "Geburtsdatum",
          "en": "Birth Date"
      },
      "type": "date",
      "parameters": {
          "format": "YYYY-MM-DD"
      }
  }
  ```

#### Time (time)
- **Appearance**: Time picker.
- **Parameters**:
  - `step`: Time increment step (default: timedelta(minutes=15)).
- **Example**:
  ```json
  {
      "key": "alarm_time",
      "name": {
          "de": "Weckzeit",
          "en": "Alarm Time"
      },
      "type": "time",
      "parameters": {
          "step": timedelta(minutes=1)
      }
  }
  ```

#### Selection (selection)
- **Appearance**: Dropdown list.
- **Parameters**:
  - `options`: Dictionary mapping language codes to lists of options.
- **Example**:
  ```json
  {
      "key": "color",
      "name": {
          "de": "Farbe",
          "en": "Color"
      },
      "type": "selection",
      "parameters": {
          "options": {
              "de": ["Rot", "Grün", "Blau"],
              "en": ["Red", "Green", "Blue"]
          }
      }
  }
  ```

#### File (file)
- **Appearance**: File upload widget.
- **Parameters**:
  - `type`: List of allowed file extensions (default: None).
  - `encoding`: Encoding to use when reading the file (default: "utf-8").
- **Example**:
  ```json
  {
      "key": "data_file",
      "name": {
          "de": "Datendatei",
          "en": "Data File"
      },
      "type": "file",
      "parameters": {
          "type": ["csv", "txt"],
          "encoding": "utf-8"
      }
  }
  ```

#### Binary File (binary_file)
- **Appearance**: File upload widget.
- **Parameters**:
  - `type`: List of allowed file extensions (default: None).
- **Example**:
  ```json
  {
      "key": "image_file",
      "name": {
          "de": "Bilddatei",
          "en": "Image File"
      },
      "type": "binary_file",
      "parameters": {
          "type": ["png", "jpg"]
      }
  }
  ```

#### Table (table)
- **Appearance**: File upload widget for CSV files.
- **Parameters**:
  - `sep`: Delimiter to use when reading the CSV file (default: ",").
  - `delimiter`: Alternative delimiter (default: None).
- **Example**:
  ```json
  {
      "key": "data_table",
      "name": {
          "de": "Datentabelle",
          "en": "Data Table"
      },
      "type": "table",
      "parameters": {
          "sep": ",",
          "delimiter": ";"
      }
  }
  ```

### Output Types

#### Boolean (bool)
- **Appearance**: Disabled text input showing "Ja" or "Nein" (German) or "Yes" or "No" (English).
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "success",
      "name": {
          "de": "Erfolg",
          "en": "Success"
      },
      "type": "bool"
  }
  ```

#### Integer (int)
- **Appearance**: Disabled text input showing the integer value.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "result",
      "name": {
          "de": "Ergebnis",
          "en": "Result"
      },
      "type": "int"
  }
  ```

#### Float (float)
- **Appearance**: Disabled text input showing the float value.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "score",
      "name": {
          "de": "Punktzahl",
          "en": "Score"
      },
      "type": "float"
  }
  ```

#### String (str)
- **Appearance**: Disabled text input or textarea (if `multiline` is true).
- **Parameters**:
  - `multiline`: Whether to use a textarea (default: False).
- **Example**:
  ```json
  {
      "key": "message",
      "name": {
          "de": "Nachricht",
          "en": "Message"
      },
      "type": "str",
      "parameters": {
          "multiline": true
      }
  }
  ```

#### Filename (filename)
- **Appearance**: Disabled text input showing the filename.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "output_file",
      "name": {
          "de": "Ausgabedatei",
          "en": "Output File"
      },
      "type": "filename"
  }
  ```

#### URL (url)
- **Appearance**: Disabled text input showing the URL.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "link",
      "name": {
          "de": "Link",
          "en": "Link"
      },
      "type": "url"
  }
  ```

#### Datetime (datetime)
- **Appearance**: Disabled text input showing the datetime in "YYYY-MM-DD HH:MM" format.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "event_time",
      "name": {
          "de": "Ereigniszeit",
          "en": "Event Time"
      },
      "type": "datetime"
  }
  ```

#### Date (date)
- **Appearance**: Disabled text input showing the date in "YYYY-MM-DD" format.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "due_date",
      "name": {
          "de": "Fälligkeitsdatum",
          "en": "Due Date"
      },
      "type": "date"
  }
  ```

#### Time (time)
- **Appearance**: Disabled text input showing the time in "HH:MM" format.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "alarm_time",
      "name": {
          "de": "Weckzeit",
          "en": "Alarm Time"
      },
      "type": "time"
  }
  ```

#### Selection (selection)
- **Appearance**: Disabled text input showing the selected option.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "selected_color",
      "name": {
          "de": "Ausgewählte Farbe",
          "en": "Selected Color"
      },
      "type": "selection"
  }
  ```

#### File (file)
- **Appearance**: Download button.
- **Parameters**:
  - `filename`: Default filename for the download (default: "data.txt").
  - `prefix_language`: Whether to prefix the filename with the language code (default: False).
  - `prefix_datetime`: Whether to prefix the filename with the current datetime (default: False).
  - `mime`: MIME type of the file (default: "text/plain").
- **Example**:
  ```json
  {
      "key": "data_file",
      "name": {
          "de": "Datendatei",
          "en": "Data File"
      },
      "type": "file",
      "parameters": {
          "filename": "output.txt",
          "prefix_language": true,
          "prefix_datetime": true,
          "mime": "text/plain"
      }
  }
  ```

#### Binary File (binary_file)
- **Appearance**: Download button.
- **Parameters**:
  - `filename`: Default filename for the download (default: "data.bin").
  - `prefix_language`: Whether to prefix the filename with the language code (default: False).
  - `prefix_datetime`: Whether to prefix the filename with the current datetime (default: False).
  - `mime`: MIME type of the file (default: "application/octet-stream").
- **Example**:
  ```json
  {
      "key": "image_file",
      "name": {
          "de": "Bilddatei",
          "en": "Image File"
      },
      "type": "binary_file",
      "parameters": {
          "filename": "image.png",
          "prefix_language": false,
          "prefix_datetime": true,
          "mime": "image/png"
      }
  }
  ```

#### Table (table)
- **Appearance**: Dataframe display.
- **Parameters**: None.
- **Example**:
  ```json
  {
      "key": "data_table",
      "name": {
          "de": "Datentabelle",
          "en": "Data Table"
      },
      "type": "table"
  }
  ```

## Localization
The `localization.json` file contains translations for different languages. Here is an example structure:

```json
{
    "reading_name": {
        "de": "Lese Namen...",
        "en": "Reading names..."
    },
    "creating_greeting": {
        "de": "Erstelle Begrüßung...",
        "en": "Creating greeting..."
    },
    "hello": {
        "de": "Hallo, {name}",
        "en": "Hello, {name}"
    }
}
```

### Using Translations
In your app code, you can retrieve translations using the following methods:
- `self.get_translations("key")`: Returns a dictionary of translations for the given key.
- `self.get_translation("key")`: Returns the translation for the current language.

Example usage in the `run` method:

```python
self.messenger.set_message(self.get_translations("reading_name"))
```

## Initialization
The `initialize` method in your app class is called when the app starts. Here, you can perform setup tasks such as setting the app's language.

```python
def initialize(self, language: str):
    # Set the app's language
    self.language = language
```

## App Runtime
The `run` method contains the main logic of your app. Here, you can:
1. Get user inputs with `self.get_input("key")`.
2. Process the inputs.
3. Set outputs with `self.set_output("key", value)`.
4. Display status messages with `self.messenger.set_message`.

Example:

```python
def run(self):
    assert self.messenger is not None
    self.messenger.set_message(self.get_translations("reading_name"))
    name = self.get_input("name")
    greeting = self.get_translation("hello").format(name=name)
    self.set_output("greeting", greeting)
```

## Destruction
The `destroy` method is called when the app is terminated. Here, you can perform cleanup tasks such as clearing messages.

```python
def destroy(self):
    assert self.messenger is not None
    self.messenger.clear_message()
```

## Validators
Validators are used to ensure that inputs and outputs meet certain criteria. You can define validators in the `input_validators` and `output_validators` static methods.

Example:

```python
@staticmethod
def input_validators() -> ValidatorSet:
    return {
        "name": lambda n: n != "foo",
        "greeting": lambda g: g.startswith("H")
    }

@staticmethod
def output_validators() -> ValidatorSet:
    return {}
```

## Registration
To register your new app, you need to:
1. Import your app class in `apps/app_registry.py`.
2. Add the app class to the `app_classes` list.

Example:

```python
from apps.my_new_app.my_new_app import MyNewApp

app_classes: List[Type[App]] = [
    ...,
    MyNewApp
]
```

After registering, the app factory will create instances of your app.
