import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_engine_from_config,
)

from db.base import Model
from db.manager import DatabaseManager
from models.chat import Chat
from models.message import Message
from models.user import User, UserChat

# Alembic Config
manager = DatabaseManager()
config = context.config

config.set_main_option("sqlalchemy.url",
                       manager.direct_url.render_as_string(hide_password=False)
                       )

# Подключение логгера
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метадата для автогенерации
target_metadata = Model.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable: AsyncEngine = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=None,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())