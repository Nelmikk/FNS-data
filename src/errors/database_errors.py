from src.models.database_models import Base, Base_shadow_table

class TableNotFound(Exception):
    def __init__(self,
                 _table_model: type[Base, Base_shadow_table]):
        super().__init__(f'Table was not found in DB using _table_model {_table_model}')