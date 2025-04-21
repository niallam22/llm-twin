import typing  # Added import
import uuid
from typing import Type, TypeVar

import asyncpg
from pydantic import UUID4, BaseModel, ConfigDict, Field

from .. import logger_utils
from .supabase_client import SupabaseClient

# Generic type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


logger = logger_utils.get_logger(__name__)


# BaseDocument removed - contained MongoDB-specific logic


class UserDocument(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    username: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    async def save(cls: Type[T], instance: T, db_client: SupabaseClient) -> T:
        """Saves (inserts or updates) a UserDocument instance to the database."""

        try:
            table_name = "users"
            # Assuming 'id' is the conflict target as 'platform_user_id' is not in the model
            # If 'platform_user_id' should be used, the model needs updating.
            conflict_target = "id"
            data = instance.model_dump(exclude_unset=True)

            # Ensure id is present
            if "id" not in data:
                data["id"] = uuid.uuid4()  # Should be set by default_factory, but ensure

            columns = list(data.keys())
            insert_cols = ", ".join(columns)
            insert_placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))

            # Build UPDATE SET clause excluding conflict target ('id') and 'created_at', 'updated_at'
            update_set_parts = []
            update_params = []
            param_index = len(columns) + 1
            for i, col in enumerate(columns):
                if col not in ("id", "created_at", "updated_at"):
                    update_set_parts.append(f"{col} = ${param_index}")
                    update_params.append(data[col])
                    param_index += 1
            update_set_clause = ", ".join(update_set_parts)

            sql = f"""
            INSERT INTO {table_name} ({insert_cols})
            VALUES ({insert_placeholders})
            ON CONFLICT ({conflict_target}) DO UPDATE SET {update_set_clause}
            RETURNING *;
            """
            params = list(data.values()) + update_params

            record = await db_client.fetch_one(sql, params)

            if record:
                # Update instance with potentially new/updated fields from DB (like created_at, updated_at)
                # Use construct to avoid re-validation if possible, or just update fields
                updated_data = {**instance.model_dump(), **dict(record)}
                return cls(**updated_data)  # Re-create instance with DB data
            else:
                logger.warning(f"Failed to save or retrieve record for UserDocument with id {getattr(instance, 'id', 'unknown')}")
                return instance  # Return original instance on failure

        except asyncpg.PostgresError as e:
            logger.error(f"Database error saving UserDocument with id {getattr(instance, 'id', 'unknown')}: {e}")
            # Re-raise or handle as appropriate
            raise Exception(f"Failed to save UserDocument: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error saving UserDocument with id {getattr(instance, 'id', 'unknown')}: {e}")
            raise  # Re-raise unexpected errors

    @classmethod
    async def find_one(cls: Type["UserDocument"], db_client: SupabaseClient, **kwargs) -> typing.Optional["UserDocument"]:
        """Finds a single UserDocument instance based on keyword arguments."""
        if not kwargs:
            logger.warning(f"find_one called without any criteria for {cls.__name__}.")
            return None

        # Define table name and mappings specific to the class
        table_name = "users"
        db_column_map = {}  # No mapping needed for UserDocument based on save method

        try:
            conditions = []
            params = []
            valid_keys_provided = False
            param_index = 1
            for key, value in kwargs.items():
                if key not in cls.model_fields:
                    logger.warning(f"Invalid filter key '{key}' provided for {cls.__name__}. Skipping.")
                    continue  # Skip keys not present in the model

                valid_keys_provided = True
                db_key = db_column_map.get(key, key)  # Map to DB column name for WHERE clause
                conditions.append(f"{db_key} = ${param_index}")
                params.append(value)
                param_index += 1

            if not valid_keys_provided:  # If all kwargs were invalid keys or no kwargs given initially
                logger.error(f"find_one for {cls.__name__} called with no valid criteria: {kwargs}")
                return None

            where_clause = " AND ".join(conditions)
            sql = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT 1;"
            logger.debug(f"Executing SQL for {cls.__name__}: {sql} with params: {params}")

            record = await db_client.fetch_one(sql, params)

            if record:
                try:
                    record_dict = dict(record)
                    # Map DB keys back to model keys for instantiation
                    model_data = {}
                    reverse_db_map = {v: k for k, v in db_column_map.items()}
                    for db_key, value in record_dict.items():
                        model_key = reverse_db_map.get(db_key, db_key)
                        # Only include keys that are actual model fields
                        if model_key in cls.model_fields:
                            model_data[model_key] = value

                    if not model_data:
                        logger.error(f"DB record {record_dict} for {cls.__name__} resulted in empty model data after mapping.")
                        return None

                    instance = cls(**model_data)
                    logger.info(f"Found {cls.__name__} with criteria: {kwargs}")
                    return instance
                except Exception as e:  # Catch Pydantic validation errors etc.
                    logger.error(f"Error instantiating {cls.__name__} from DB record {record_dict} (mapped: {model_data}): {e}")
                    return None
            else:
                logger.info(f"No {cls.__name__} found with criteria: {kwargs}")
                return None

        except asyncpg.PostgresError as e:
            logger.error(f"Database error finding {cls.__name__} with criteria {kwargs}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding {cls.__name__} with criteria {kwargs}: {e}")
            return None

    @classmethod
    async def get_or_create(
        cls: Type["UserDocument"], db_client: SupabaseClient, defaults: typing.Optional[dict] = None, **kwargs
    ) -> "UserDocument":
        """Finds a user based on kwargs or creates one if not found, using defaults for creation."""
        # Attempt to find the user first using the existing static method
        existing_user = await cls.find_one(db_client=db_client, **kwargs)
        if existing_user is not None:
            logger.info(f"Found existing UserDocument with criteria: {kwargs}")
            return existing_user

        # If not found, prepare data for creation
        logger.info(f"No UserDocument found with criteria: {kwargs}. Creating new one.")
        create_data = kwargs.copy()
        if defaults:
            # Ensure defaults don't overwrite explicit kwargs provided in the call
            for key, value in defaults.items():
                create_data.setdefault(key, value)  # Use setdefault

        # Instantiate and save the new user
        try:
            # Pydantic will validate required fields (username) during instantiation
            new_user = cls(**create_data)

            # Use the existing static save method. cls is passed implicitly.
            saved_user = await cls.save(new_user, db_client)
            logger.info(f"Successfully created and saved new UserDocument with data: {create_data}")
            return saved_user
        except (TypeError, ValueError) as e:  # Catch Pydantic validation errors (TypeError/ValueError)
            # Log a more specific error if possible, indicating missing fields might be the cause
            error_msg = f"Failed to instantiate UserDocument. Check required fields (userrname). Data: {create_data}, Error: {e}"
            logger.error(error_msg)
            # Re-raise as ValueError for consistent error handling upstream
            raise ValueError(error_msg) from e
        except Exception as e:  # Catch potential errors from cls.save
            logger.error(f"Error saving new UserDocument with data {create_data}: {e}")
            # Propagate the exception from save
            raise


class RepositoryDocument(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    link: str
    content: dict  # TODO: Consider if JSON type is better for Postgres
    owner_id: str = Field(alias="owner_id")  # TODO: Alias might not be needed depending on Supabase mapping

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    async def save(cls: Type[T], instance: T, db_client: SupabaseClient) -> T:
        """Saves (inserts or updates) a RepositoryDocument instance to the database."""
        try:
            table_name = "repositories"
            # DB schema has 'url' unique constraint, model has 'link'
            conflict_target_db = "url"
            # DB schema has 'owner_platform_user_id', model has 'owner_id'
            db_column_map = {"link": "url", "owner_id": "owner_platform_user_id"}

            data = instance.model_dump(exclude_unset=True)

            # Ensure id is present
            if "id" not in data:
                data["id"] = uuid.uuid4()

            # Map model fields to DB columns for SQL construction
            columns_model = list(data.keys())
            columns_db = [db_column_map.get(col, col) for col in columns_model]
            insert_cols = ", ".join(columns_db)
            insert_placeholders = ", ".join(f"${i + 1}" for i in range(len(columns_db)))

            # Build UPDATE SET clause excluding conflict target ('url') and 'id', 'created_at', 'updated_at'
            update_set_parts = []
            update_params = []
            param_index = len(columns_db) + 1
            for i, col_db in enumerate(columns_db):
                # Use DB column name for exclusion check
                if col_db not in (conflict_target_db, "id", "created_at", "updated_at"):
                    update_set_parts.append(f"{col_db} = ${param_index}")
                    # Use original model data value for the parameter
                    update_params.append(data[columns_model[i]])
                    param_index += 1
            update_set_clause = ", ".join(update_set_parts)

            sql = f"""
            INSERT INTO {table_name} ({insert_cols})
            VALUES ({insert_placeholders})
            ON CONFLICT ({conflict_target_db}) DO UPDATE SET {update_set_clause}
            RETURNING *;
            """
            params = list(data.values()) + update_params

            record = await db_client.fetch_one(sql, params)

            if record:
                # Map DB record back to model fields if necessary
                record_dict = dict(record)
                model_data = {**instance.model_dump()}  # Start with current model data
                # Update with DB values, mapping DB names back to model names
                reverse_db_map = {v: k for k, v in db_column_map.items()}
                for db_key, value in record_dict.items():
                    model_key = reverse_db_map.get(db_key, db_key)
                    if model_key in instance.model_fields:
                        model_data[model_key] = value
                return cls(**model_data)
            else:
                logger.warning(f"Failed to save or retrieve record for RepositoryDocument with link {getattr(instance, 'link', 'unknown')}")
                return instance

        except asyncpg.PostgresError as e:
            logger.error(f"Database error saving RepositoryDocument with link {getattr(instance, 'link', 'unknown')}: {e}")
            raise Exception(f"Failed to save RepositoryDocument: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error saving RepositoryDocument with link {getattr(instance, 'link', 'unknown')}: {e}")
            raise

    @classmethod
    async def find_one(cls: Type["RepositoryDocument"], db_client: SupabaseClient, **kwargs) -> typing.Optional["RepositoryDocument"]:
        """Finds a single RepositoryDocument instance based on keyword arguments."""
        if not kwargs:
            logger.warning(f"find_one called without any criteria for {cls.__name__}.")
            return None

        # Define table name and mappings specific to the class
        table_name = "repositories"
        db_column_map = {"link": "url", "owner_id": "owner_platform_user_id"}  # From save method

        try:
            conditions = []
            params = []
            valid_keys_provided = False
            param_index = 1
            for key, value in kwargs.items():
                if key not in cls.model_fields:
                    logger.warning(f"Invalid filter key '{key}' provided for {cls.__name__}. Skipping.")
                    continue  # Skip keys not present in the model

                valid_keys_provided = True
                db_key = db_column_map.get(key, key)  # Map to DB column name for WHERE clause
                conditions.append(f"{db_key} = ${param_index}")
                params.append(value)
                param_index += 1

            if not valid_keys_provided:  # If all kwargs were invalid keys or no kwargs given initially
                logger.error(f"find_one for {cls.__name__} called with no valid criteria: {kwargs}")
                return None

            where_clause = " AND ".join(conditions)
            sql = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT 1;"
            logger.debug(f"Executing SQL for {cls.__name__}: {sql} with params: {params}")

            record = await db_client.fetch_one(sql, params)

            if record:
                try:
                    record_dict = dict(record)
                    # Map DB keys back to model keys for instantiation
                    model_data = {}
                    reverse_db_map = {v: k for k, v in db_column_map.items()}
                    for db_key, value in record_dict.items():
                        model_key = reverse_db_map.get(db_key, db_key)
                        # Only include keys that are actual model fields
                        if model_key in cls.model_fields:
                            model_data[model_key] = value

                    if not model_data:
                        logger.error(f"DB record {record_dict} for {cls.__name__} resulted in empty model data after mapping.")
                        return None

                    instance = cls(**model_data)
                    logger.info(f"Found {cls.__name__} with criteria: {kwargs}")
                    return instance
                except Exception as e:  # Catch Pydantic validation errors etc.
                    logger.error(f"Error instantiating {cls.__name__} from DB record {record_dict} (mapped: {model_data}): {e}")
                    return None
            else:
                logger.info(f"No {cls.__name__} found with criteria: {kwargs}")
                return None

        except asyncpg.PostgresError as e:
            logger.error(f"Database error finding {cls.__name__} with criteria {kwargs}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding {cls.__name__} with criteria {kwargs}: {e}")
            return None

    @classmethod
    async def bulk_insert(cls: Type["RepositoryDocument"], instances: typing.List["RepositoryDocument"], db_client: SupabaseClient) -> None:
        """Efficiently inserts multiple RepositoryDocument instances into the database."""
        if not instances:
            logger.info("bulk_insert called with empty list for RepositoryDocument.")
            return

        try:
            table_name = "repositories"
            conflict_target_db = "url"  # As per instructions
            # Map model field names to database column names
            db_column_map = {"link": "url", "owner_id": "owner_platform_user_id"}

            # Get columns from the first instance, excluding 'id'
            first_instance_data = instances[0].model_dump()
            model_columns = [col for col in first_instance_data.keys() if col != "id"]

            if not model_columns:
                logger.warning("No columns determined for bulk insert of RepositoryDocument (excluding id).")
                return

            # Map to DB column names for the SQL query, ensuring they are strings
            db_columns = [db_column_map.get(col, col) for col in model_columns]
            # Filter out potential None values just in case, though unlikely with model keys
            db_columns = [col for col in db_columns if isinstance(col, str)]
            insert_cols_sql = ", ".join(f'"{c}"' for c in db_columns)  # Quote column names for safety

            num_columns = len(db_columns)
            num_rows = len(instances)

            # Create placeholders for all rows: ($1,$2), ($3,$4), ...
            all_rows_placeholders = []
            param_index = 1
            for _ in range(num_rows):
                row_placeholders = ", ".join(f"${param_index + i}" for i in range(num_columns))
                all_rows_placeholders.append(f"({row_placeholders})")
                param_index += num_columns
            values_sql = ", ".join(all_rows_placeholders)

            # Prepare flat list of parameters in the correct order
            params = []
            for instance in instances:
                instance_data = instance.model_dump()
                for model_col in model_columns:  # Iterate using model columns to ensure correct order
                    params.append(instance_data.get(model_col))

            sql = f"""
            INSERT INTO {table_name} ({insert_cols_sql})
            VALUES {values_sql}
            ON CONFLICT ({conflict_target_db}) DO NOTHING;
            """

            logger.debug(f"Executing bulk insert for {num_rows} RepositoryDocuments. SQL: {sql[:500]}...")  # Log truncated SQL
            await db_client.execute(sql, params)
            logger.info(f"Successfully executed bulk insert for {num_rows} RepositoryDocuments.")

        except asyncpg.PostgresError as e:
            logger.error(f"Database error during bulk insert for RepositoryDocument: {e}")
            # Depending on requirements, might log failed IDs or re-raise
            raise Exception(f"Failed bulk insert for RepositoryDocument: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during bulk insert for RepositoryDocument: {e}")
            raise


class PostDocument(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    platform: str
    content: dict  # TODO: Consider if JSON type is better for Postgres
    author_id: str = Field(alias="author_id")  # TODO: Alias might not be needed

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    async def save(cls: Type[T], instance: T, db_client: SupabaseClient) -> T:
        """Saves (inserts or updates) a PostDocument instance to the database."""
        try:
            table_name = "posts"
            # DB schema has unique constraint on (platform, platform_post_id), model lacks platform_post_id.
            # Instructions mention 'url' example, but model lacks it. Using 'id' as fallback conflict target.
            conflict_target = "id"
            # DB schema has 'author_platform_user_id', model has 'author_id'
            db_column_map = {"author_id": "author_platform_user_id"}

            data = instance.model_dump(exclude_unset=True)

            # Ensure id is present
            if "id" not in data:
                data["id"] = uuid.uuid4()

            # Map model fields to DB columns for SQL construction
            columns_model = list(data.keys())
            columns_db = [db_column_map.get(col, col) for col in columns_model]
            insert_cols = ", ".join(columns_db)
            insert_placeholders = ", ".join(f"${i + 1}" for i in range(len(columns_db)))

            # Build UPDATE SET clause excluding conflict target ('id') and 'created_at', 'updated_at'
            update_set_parts = []
            update_params = []
            param_index = len(columns_db) + 1
            for i, col_db in enumerate(columns_db):
                if col_db not in (conflict_target, "created_at", "updated_at"):  # Exclude 'id' implicitly as it's the conflict target
                    update_set_parts.append(f"{col_db} = ${param_index}")
                    update_params.append(data[columns_model[i]])
                    param_index += 1
            update_set_clause = ", ".join(update_set_parts)

            sql = f"""
            INSERT INTO {table_name} ({insert_cols})
            VALUES ({insert_placeholders})
            ON CONFLICT ({conflict_target}) DO UPDATE SET {update_set_clause}
            RETURNING *;
            """
            params = list(data.values()) + update_params

            record = await db_client.fetch_one(sql, params)

            if record:
                # Map DB record back to model fields
                record_dict = dict(record)
                model_data = {**instance.model_dump()}
                reverse_db_map = {v: k for k, v in db_column_map.items()}
                for db_key, value in record_dict.items():
                    model_key = reverse_db_map.get(db_key, db_key)
                    if model_key in instance.model_fields:
                        model_data[model_key] = value
                return cls(**model_data)
            else:
                logger.warning(f"Failed to save or retrieve record for PostDocument with id {getattr(instance, 'id', 'unknown')}")
                return instance

        except asyncpg.PostgresError as e:
            logger.error(f"Database error saving PostDocument with id {getattr(instance, 'id', 'unknown')}: {e}")
            raise Exception(f"Failed to save PostDocument: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error saving PostDocument with id {getattr(instance, 'id', 'unknown')}: {e}")
            raise

    @classmethod
    async def find_one(cls: Type["PostDocument"], db_client: SupabaseClient, **kwargs) -> typing.Optional["PostDocument"]:
        """Finds a single PostDocument instance based on keyword arguments."""
        if not kwargs:
            logger.warning(f"find_one called without any criteria for {cls.__name__}.")
            return None

        # Define table name and mappings specific to the class
        table_name = "posts"
        db_column_map = {"author_id": "author_platform_user_id"}  # From save method

        try:
            conditions = []
            params = []
            valid_keys_provided = False
            param_index = 1
            for key, value in kwargs.items():
                if key not in cls.model_fields:
                    logger.warning(f"Invalid filter key '{key}' provided for {cls.__name__}. Skipping.")
                    continue  # Skip keys not present in the model

                valid_keys_provided = True
                db_key = db_column_map.get(key, key)  # Map to DB column name for WHERE clause
                conditions.append(f"{db_key} = ${param_index}")
                params.append(value)
                param_index += 1

            if not valid_keys_provided:  # If all kwargs were invalid keys or no kwargs given initially
                logger.error(f"find_one for {cls.__name__} called with no valid criteria: {kwargs}")
                return None

            where_clause = " AND ".join(conditions)
            sql = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT 1;"
            logger.debug(f"Executing SQL for {cls.__name__}: {sql} with params: {params}")

            record = await db_client.fetch_one(sql, params)

            if record:
                try:
                    record_dict = dict(record)
                    # Map DB keys back to model keys for instantiation
                    model_data = {}
                    reverse_db_map = {v: k for k, v in db_column_map.items()}
                    for db_key, value in record_dict.items():
                        model_key = reverse_db_map.get(db_key, db_key)
                        # Only include keys that are actual model fields
                        if model_key in cls.model_fields:
                            model_data[model_key] = value

                    if not model_data:
                        logger.error(f"DB record {record_dict} for {cls.__name__} resulted in empty model data after mapping.")
                        return None

                    instance = cls(**model_data)
                    logger.info(f"Found {cls.__name__} with criteria: {kwargs}")
                    return instance
                except Exception as e:  # Catch Pydantic validation errors etc.
                    logger.error(f"Error instantiating {cls.__name__} from DB record {record_dict} (mapped: {model_data}): {e}")
                    return None
            else:
                logger.info(f"No {cls.__name__} found with criteria: {kwargs}")
                return None

        except asyncpg.PostgresError as e:
            logger.error(f"Database error finding {cls.__name__} with criteria {kwargs}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding {cls.__name__} with criteria {kwargs}: {e}")
            return None

    @classmethod
    async def bulk_insert(cls: Type["PostDocument"], instances: typing.List["PostDocument"], db_client: SupabaseClient) -> None:
        """Efficiently inserts multiple PostDocument instances into the database."""
        if not instances:
            logger.info("bulk_insert called with empty list for PostDocument.")
            return

        try:
            table_name = "posts"
            # TODO: Verify 'url' is the correct conflict target for 'posts' table as model lacks it. Following instructions.
            conflict_target_db = "url"
            # Map model field names to database column names
            db_column_map = {"author_id": "author_platform_user_id"}

            # Get columns from the first instance, excluding 'id'
            first_instance_data = instances[0].model_dump()
            model_columns = [col for col in first_instance_data.keys() if col != "id"]

            if not model_columns:
                logger.warning("No columns determined for bulk insert of PostDocument (excluding id).")
                return

            # Map to DB column names for the SQL query
            db_columns = [db_column_map.get(col, col) for col in model_columns]
            insert_cols_sql = ", ".join(f'"{c}"' for c in db_columns)  # Quote column names

            num_columns = len(db_columns)
            num_rows = len(instances)

            # Create placeholders for all rows: ($1,$2), ($3,$4), ...
            all_rows_placeholders = []
            param_index = 1
            for _ in range(num_rows):
                row_placeholders = ", ".join(f"${param_index + i}" for i in range(num_columns))
                all_rows_placeholders.append(f"({row_placeholders})")
                param_index += num_columns
            values_sql = ", ".join(all_rows_placeholders)

            # Prepare flat list of parameters in the correct order
            params = []
            for instance in instances:
                instance_data = instance.model_dump()
                for model_col in model_columns:
                    params.append(instance_data.get(model_col))

            sql = f"""
            INSERT INTO {table_name} ({insert_cols_sql})
            VALUES {values_sql}
            ON CONFLICT ({conflict_target_db}) DO NOTHING;
            """

            logger.debug(f"Executing bulk insert for {num_rows} PostDocuments. SQL: {sql[:500]}...")
            await db_client.execute(sql, params)
            logger.info(f"Successfully executed bulk insert for {num_rows} PostDocuments.")

        except asyncpg.PostgresError as e:
            logger.error(f"Database error during bulk insert for PostDocument: {e}")
            raise Exception(f"Failed bulk insert for PostDocument: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during bulk insert for PostDocument: {e}")
            raise


class ArticleDocument(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    platform: str
    link: str
    content: str
    author_id: UUID4 = Field(alias="author_id")
    collection_id: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    async def save(cls: Type[T], instance: T, db_client: SupabaseClient) -> T:
        """Saves (inserts or updates) an ArticleDocument instance to the database."""
        try:
            table_name = "articles"
            # DB schema has 'url' unique constraint, model has 'link'
            conflict_target_db = "url"
            # DB schema has 'author_platform_user_id', model has 'author_id'
            db_column_map = {"link": "url"}

            data = instance.model_dump(exclude_unset=True)

            # Ensure id is present
            if "id" not in data:
                data["id"] = uuid.uuid4()

            # Map model fields to DB columns for SQL construction
            columns_model = list(data.keys())
            columns_db = [db_column_map.get(col, col) for col in columns_model]
            insert_cols = ", ".join(columns_db)
            insert_placeholders = ", ".join(f"${i + 1}" for i in range(len(columns_db)))

            # Build UPDATE SET clause excluding conflict target ('url') and 'id', 'created_at', 'updated_at'
            update_set_parts = []
            update_params = []
            param_index = len(columns_db) + 1
            for i, col_db in enumerate(columns_db):
                if col_db not in (conflict_target_db, "id", "created_at", "updated_at"):
                    update_set_parts.append(f"{col_db} = ${param_index}")
                    update_params.append(data[columns_model[i]])
                    param_index += 1
            update_set_clause = ", ".join(update_set_parts)

            sql = f"""
            INSERT INTO {table_name} ({insert_cols})
            VALUES ({insert_placeholders})
            ON CONFLICT ({conflict_target_db}) DO UPDATE SET {update_set_clause}
            RETURNING *;
            """
            params = list(data.values()) + update_params

            record = await db_client.fetch_one(sql, params)

            if record:
                # Map DB record back to model fields
                record_dict = dict(record)
                model_data = {**instance.model_dump()}
                reverse_db_map = {v: k for k, v in db_column_map.items()}
                for db_key, value in record_dict.items():
                    model_key = reverse_db_map.get(db_key, db_key)
                    if model_key in instance.model_fields:
                        model_data[model_key] = value
                return cls(**model_data)
            else:
                logger.warning(f"Failed to save or retrieve record for ArticleDocument with link {getattr(instance, 'link', 'unknown')}")
                return instance

        except asyncpg.PostgresError as e:
            logger.error(f"Database error saving ArticleDocument with link {getattr(instance, 'link', 'unknown')}: {e}")
            raise Exception(f"Failed to save ArticleDocument: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error saving ArticleDocument with link {getattr(instance, 'link', 'unknown')}: {e}")
            raise

    @classmethod
    async def find_one(cls: Type["ArticleDocument"], db_client: SupabaseClient, **kwargs) -> typing.Optional["ArticleDocument"]:
        """Finds a single ArticleDocument instance based on keyword arguments."""
        if not kwargs:
            logger.warning(f"find_one called without any criteria for {cls.__name__}.")
            return None

        # Define table name and mappings specific to the class
        table_name = "articles"
        db_column_map = {"link": "url", "author_id": "author_platform_user_id"}  # From save method

        try:
            conditions = []
            params = []
            valid_keys_provided = False
            param_index = 1
            for key, value in kwargs.items():
                if key not in cls.model_fields:
                    logger.warning(f"Invalid filter key '{key}' provided for {cls.__name__}. Skipping.")
                    continue  # Skip keys not present in the model

                valid_keys_provided = True
                db_key = db_column_map.get(key, key)  # Map to DB column name for WHERE clause
                conditions.append(f"{db_key} = ${param_index}")
                params.append(value)
                param_index += 1

            if not valid_keys_provided:  # If all kwargs were invalid keys or no kwargs given initially
                logger.error(f"find_one for {cls.__name__} called with no valid criteria: {kwargs}")
                return None

            where_clause = " AND ".join(conditions)
            sql = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT 1;"
            logger.debug(f"Executing SQL for {cls.__name__}: {sql} with params: {params}")

            record = await db_client.fetch_one(sql, params)

            if record:
                try:
                    record_dict = dict(record)
                    # Map DB keys back to model keys for instantiation
                    model_data = {}
                    reverse_db_map = {v: k for k, v in db_column_map.items()}
                    for db_key, value in record_dict.items():
                        model_key = reverse_db_map.get(db_key, db_key)
                        # Only include keys that are actual model fields
                        if model_key in cls.model_fields:
                            model_data[model_key] = value

                    if not model_data:
                        logger.error(f"DB record {record_dict} for {cls.__name__} resulted in empty model data after mapping.")
                        return None

                    instance = cls(**model_data)
                    logger.info(f"Found {cls.__name__} with criteria: {kwargs}")
                    return instance
                except Exception as e:  # Catch Pydantic validation errors etc.
                    logger.error(f"Error instantiating {cls.__name__} from DB record {record_dict} (mapped: {model_data}): {e}")
                    return None
            else:
                logger.info(f"No {cls.__name__} found with criteria: {kwargs}")
                return None

        except asyncpg.PostgresError as e:
            logger.error(f"Database error finding {cls.__name__} with criteria {kwargs}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding {cls.__name__} with criteria {kwargs}: {e}")
            return None

    @classmethod
    async def bulk_insert(cls: Type["ArticleDocument"], instances: typing.List["ArticleDocument"], db_client: SupabaseClient) -> None:
        """Efficiently inserts multiple ArticleDocument instances into the database."""
        if not instances:
            logger.info("bulk_insert called with empty list for ArticleDocument.")
            return

        try:
            table_name = "articles"
            conflict_target_db = "url"  # As per instructions
            # Map model field names to database column names
            db_column_map = {"link": "url", "author_id": "author_platform_user_id"}

            # Get columns from the first instance, excluding 'id'
            first_instance_data = instances[0].model_dump()
            model_columns = [col for col in first_instance_data.keys() if col != "id"]

            if not model_columns:
                logger.warning("No columns determined for bulk insert of ArticleDocument (excluding id).")
                return

            # Map to DB column names for the SQL query
            db_columns = [db_column_map.get(col, col) for col in model_columns]
            insert_cols_sql = ", ".join(f'"{c}"' for c in db_columns)  # Quote column names

            num_columns = len(db_columns)
            num_rows = len(instances)

            # Create placeholders for all rows: ($1,$2), ($3,$4), ...
            all_rows_placeholders = []
            param_index = 1
            for _ in range(num_rows):
                row_placeholders = ", ".join(f"${param_index + i}" for i in range(num_columns))
                all_rows_placeholders.append(f"({row_placeholders})")
                param_index += num_columns
            values_sql = ", ".join(all_rows_placeholders)

            # Prepare flat list of parameters in the correct order
            params = []
            for instance in instances:
                instance_data = instance.model_dump()
                for model_col in model_columns:
                    params.append(instance_data.get(model_col))

            sql = f"""
            INSERT INTO {table_name} ({insert_cols_sql})
            VALUES {values_sql}
            ON CONFLICT ({conflict_target_db}) DO NOTHING;
            """

            logger.debug(f"Executing bulk insert for {num_rows} ArticleDocuments. SQL: {sql[:500]}...")
            await db_client.execute(sql, params)
            logger.info(f"Successfully executed bulk insert for {num_rows} ArticleDocuments.")

        except asyncpg.PostgresError as e:
            logger.error(f"Database error during bulk insert for ArticleDocument: {e}")
            raise Exception(f"Failed bulk insert for ArticleDocument: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during bulk insert for ArticleDocument: {e}")
            raise
