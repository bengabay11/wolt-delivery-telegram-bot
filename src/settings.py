from pathlib import Path

from pydantic import BaseModel, ConfigDict
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


def find_first_toml(search_dir: Path, patterns: list[str] | None = None) -> Path:
    """Search for the first TOML file in the specified directory.

    Args:
        search_dir (Path): The directory to search for TOML files.
        patterns (list[str], optional): List of glob patterns to match files,
        Defaults to ["*.toml"].

    Returns:
        Path: The path to the first TOML file found.

    Raises:
        `FileNotFoundError`: If the directory does not exist or no matching TOML file is found.

    """
    if patterns is None:
        patterns = ["*.toml"]

    if not search_dir.exists():
        msg = f"Config directory '{search_dir}' does not exist."
        raise FileNotFoundError(msg)

    for pattern in patterns:
        for toml_path in search_dir.glob(pattern):
            if toml_path.is_file():
                return toml_path
    msg = f"No TOML file found in {search_dir} matching {patterns}"
    raise FileNotFoundError(msg)


class RestaurantSettings(BaseModel):
    """Restaurant settings."""

    slug: str
    message: str
    check_interval_seconds: int = 60 * 15  # 15 minutes
    sleep_after_check_seconds: int = 60 * 60 * 2  # 2 hours


class TelegramSettings(BaseModel):
    """Telegram settings."""

    bot_token: str
    chat_id: str


class LoggingSettings(BaseModel):
    """Logging-related settings."""

    min_log_level: str = "INFO"
    log_file_path: Path | None = None

    model_config = ConfigDict(extra="forbid")


class AppCoreSettings(BaseModel):
    """Core application settings."""

    app_name: str = "Restaurant Telegram Notifier"
    environment: str = "Production"

    model_config = ConfigDict(extra="forbid")


class AppSettings(BaseSettings):
    """Application settings loaded from environment, `toml` file, and class initialization.

    Settings are loaded in the following order of precedence
    (as defined in `settings_customise_sources`):
    1. Initialization arguments (init settings)
    2. `toml` configuration file
    3. Environment variables (including `.env` file)

    NOTE: For deeply nested environment variables, use the `{SECTION}__{PROPERTY}`
    naming convention (e.g., `CORE__APP_NAME`).
    The delimiter defined in `model_config.env_nested_delimiter`
    """

    core: AppCoreSettings
    logging: LoggingSettings
    restaurant: RestaurantSettings
    telegram: TelegramSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Important for deeply nested env vars.
        # Properties should be named as `{SECTION}__{PROPERTY}` in `.env`.
        # For example: `CORE__APP_NAME`.
        env_nested_delimiter="__",
        toml_file=find_first_toml(Path(__file__).parent.parent / "config"),
        extra="forbid",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Customize the order of settings sources.(init > toml > env)
        return (init_settings, TomlConfigSettingsSource(settings_cls), env_settings)
