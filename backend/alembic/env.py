import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# This is important: add the parent directory of 'backend' to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your models
from models import Base  # This will work now
from models.team import Team
from models.submission import Submission
from models.leaderboard import Leaderboard
from models.comparison import Comparison

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

def get_url():
    return "postgresql://{}:{}@{}:{}/{}".format(
        os.getenv("DB_USER", "postgres"),
        os.getenv("DB_PASSWORD", "nehruworkshop2025"),
        os.getenv("DB_HOST", "mydbinstance.cpi8oo84o2my.ap-south-1.rds.amazonaws.com"),
        os.getenv("DB_PORT", "5432"),
        os.getenv("DB_NAME", "masterdatabase")
    )

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()