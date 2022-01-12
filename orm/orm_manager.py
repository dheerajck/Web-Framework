from database_folder.sql_setup import connect, disconnect


class BaseManager:
    # @classmethod
    # def set_connection(cls, database_settings):
    #     connection = connect()
    #     connection.autocommit = True
    #     cls.connection = connection

    @classmethod
    def _get_cursor(cls):
        connection = connect()
        connection.autocommit = True
        return connection.cursor()
        return cls.connection.cursor()

    @classmethod
    def _execute_query(cls, query, params=None):
        cursor = cls._get_cursor()
        cursor.execute(query, params)

    def __init__(self, model_class):
        self.model_class = model_class

    def select(self, *field_names, chunk_size=2000):
        # Build SELECT query
        fields_format = ', '.join(field_names)
        query = f"SELECT {fields_format} FROM {self.model_class.table_name}"

        # Execute query
        cursor = self._get_cursor()
        cursor.execute(query)

        # Fetch data obtained with the previous query execution
        # and transform it into `model_class` objects.
        # The fetching is done by batches of `chunk_size` to
        # avoid to run out of memory.
        model_objects = list()
        is_fetching_completed = False
        while not is_fetching_completed:
            result = cursor.fetchmany(size=chunk_size)
            for row_values in result:
                keys, values = field_names, row_values
                row_data = dict(zip(keys, values))
                model_objects.append(self.model_class(**row_data))
            is_fetching_completed = len(result) < chunk_size

        return model_objects

    def create(self, new_data: dict):
        field_names = new_data.keys()
        field_names_formated = ",".join(field_names)

        params = field_name_values = new_data.values()
        params = list(params)
        values_placeholder_format = ", ".join([f'{", ".join(["%s"] * len(field_names))}'])
        query = f'''
        INSERT INTO {self.model_class.table_name}
        ({field_names_formated})
        VALUES ({values_placeholder_format})'''

        self._execute_query(query, params)

    # def bulk_insert(self, rows: list):
    #     pass

    def update(self, new_data: dict):
        # Build UPDATE query and params
        field_names = new_data.keys()
        placeholder_format = ', '.join([f'{field_name} = %s' for field_name in field_names])
        query = f"UPDATE {self.model_class.table_name} SET {placeholder_format}"
        params = list(new_data.values())

        # Execute query
        self._execute_query(query, params)

    def delete(self):
        # Build DELETE query
        query = f"DELETE FROM {self.model_class.table_name} "

        # Execute query
        self._execute_query(query)


# ----------------------- Model ----------------------- #
class MetaModel(type):
    manager_class = BaseManager

    def _get_manager(cls):
        print(f"class is {cls}")
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls):
        return cls._get_manager()


class BaseModel(metaclass=MetaModel):
    table_name = ""

    def __init__(self, **row_data):
        for field_name, value in row_data.items():
            setattr(self, field_name, value)

    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self.__dict__.items()])
        return f"<{self.__class__.__name__}: ({attrs_format})>"
