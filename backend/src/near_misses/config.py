import json
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/near_misses"

    # In ECS, the task definition injects DB_HOST/DB_PORT/DB_NAME/DB_USER as
    # plain env vars and the master password as a Secrets Manager-backed
    # secret (DB_SECRET_JSON, a JSON blob with a "password" field — the
    # format AWS's manage_master_user_password produces). When db_host is
    # set, database_url above is overridden by assembling it from these
    # instead of relying on a single hand-provided DATABASE_URL. Locally
    # (docker-compose), none of these are set and database_url is used as-is.
    db_host: str | None = None
    db_port: int = 5432
    db_name: str | None = None
    db_user: str | None = None
    db_secret_json: str | None = None

    s3_bucket: str = "near-misses-raw-archive"
    s3_endpoint_url: str | None = None  # set to localstack URL in dev
    aws_region: str = "us-west-2"

    ntsb_api_base: str = "https://data.ntsb.gov/carol-main-public/api/Query/Main"
    aviationweather_api_base: str = "https://aviationweather.gov/api/data"
    # 2.5+ feed, not "all": low-magnitude (<2.5) quakes are numerous and not
    # worth tracking on this map — see UsgsClient's own client-side filter,
    # which enforces the cutoff exactly regardless of this feed's boundary.
    usgs_api_base: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson"
    nws_api_base: str = "https://api.weather.gov"
    nws_user_agent: str = "near-misses-incident-map (https://incidents.tashton.com)"
    fra_api_base: str = "https://data.transportation.gov/resource/85tf-25kj.json"

    poll_interval_minutes: int = 5
    scheduler_enabled: bool = True

    @model_validator(mode="after")
    def _assemble_database_url_from_aws_secret(self) -> "Settings":
        if self.db_host and self.db_secret_json:
            password = json.loads(self.db_secret_json)["password"]
            self.database_url = (
                f"postgresql+psycopg://{self.db_user}:{quote_plus(password)}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        return self


settings = Settings()
