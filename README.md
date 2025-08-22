# Wolt Delivery Telegram Bot

Python Telegram bot that monitors the delivery availability status of Wolt restaurant and sends notifications about it.

## Features

- Querying Wolt to understand if the restaurant is currently available for deliveries
- Sends a Telegram message to the bot channel
- configurable for other restaurants

### Usage

1. **Clone the Template:**
   Clone this repository and rename the project directory to your desired project name:

2. **Install Dependencies:**
   Initialize a virtual environment and install all project dependencies using `uv`:

   ```sh
   uv venv
   uv pip install -r pyproject.toml
   ```

3. **Install Pre-Commit Hooks:**
   Set up the pre-commit hooks to automate code quality checks before each commit:

   ```sh
   pre-commit install
   ```

4. **Developing:**

   Continue building your awesome bot within the `src/` directory.

5. **Run the Bot**

   ```sh
   cd src
   python main.py
   ```

   Alternatively, you can use the pre-configured VS Code debug settings in [launch.json](.vscode/launch.json) for a seamless debugging experience.

## Docker

You can also run the bot using Docker:

1. **Build the Docker Image:**

   ```sh
   docker build -t wolt-restaurant-notifier .
   ```

2. **Run the Container:**

   ```sh
   docker run -it \
     -v $(pwd)/config:/app/config \
     wolt-restaurant-notifier
   ```

   - `-v $(pwd)/config:/app/config`: Mounts your local config directory, allowing you to modify the configuration without rebuilding the image

3. **Environment Variables:**
   You can also pass environment variables to override config settings:

   ```sh
   docker run -v $(pwd)/config:/app/config \
     -e TELEGRAM__TOKEN="your_token" \
     -e TELEGRAM__CHAT_ID="your_chat_id" \
     wolt-restaurant-notifier
   ```

---

## Settings

This template features a modern configuration system using [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) (see [settings.py](src/settings.py)).

- **Multi-source loading:** Settings are loaded in the following order of precedence:

  1. Direct class initialization
  2. TOML config file (e.g., [config/config.example.toml](config/config.example.toml))
  3. environment variables (including `.env`).

- **Sectioned & Nested:** Settings are organized into logical sections (e.g., `core`, `logging`) for clarity and scalability. Deeply nested environment variables are supported using the `SECTION__PROPERTY` naming convention (e.g., `CORE__APP_NAME`).
- **Auto-discovery:** The config system can automatically find the first TOML file in your [config/](config) directory, making it easy to switch environments or configurations.
- **Type-safe:** All settings are validated and parsed using Pydantic models, ensuring type safety and clear error messages.

Example usage:

```python
from src.settings import settings
print(settings.core.app_name)
print(settings.logging.min_log_level)
```

---

## Logging

Logging is handled via a flexible, colorized, and extensible system (see [logging_setup.py](src/logging_setup.py)).

- **Colorful output:** Uses [colorlog](https://pypi.org/project/colorlog/) for beautiful, readable terminal logs.
- **Configurable handlers:** Supports both stream and file handlers, with easy configuration via settings.
- **Validation:** Log level and handler configuration are validated using Pydantic, with clear error messages for misconfiguration.
- **Extensible:** The handler system is built on an abstract base class, making it easy to add new handler types if needed.

Example usage:

```python
from src.logging_setup import setup_logger, SetupLoggerParams, LoggerHandlerType
from src.settings import settings

setup_logger(
    SetupLoggerParams(
        level=settings.logging.min_log_level,
        handler_types={LoggerHandlerType.STREAM},
        file_path=settings.logging.log_file_path,
    )
)
```

---

## License

This project is open-sourced under the terms of the [LICENSE](LICENSE).
