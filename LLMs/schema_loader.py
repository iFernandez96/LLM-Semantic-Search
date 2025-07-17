import importlib

def load_schema(schema_name):
    try:
        module = importlib.import_module(f'LLMs.schemas.{schema_name}')
        return module.SCHEMA
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Schema '{schema_name}' is invalid or improperly defined.\n{e}")