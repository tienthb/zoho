
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["src/config/config.ini"],
    load_dotenv=True,
    environments=True
)