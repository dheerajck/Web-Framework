from .database_folder.sql_setup import connect, disconnect


class BaseManager:
    @classmethod
    def _get_cursor_and_connection(cls):
        connection = connect()
        connection.autocommit = True
        return connection.cursor(), connection

    @classmethod
    def _new_execute_query(cls, cursor, query, parameters=None):

        if parameters == []:
            parameters = None
        print("\n\n__________________START ORM__________________\n\n")

        print(parameters)
        print("Current sql query", query, parameters)
        cursor.execute(query, parameters)

        if "SELECT" in query:
            # field_names = [desc[0] for desc in cursor.description]
            # print(field_names)
            pass

        print("\n\n__________________STOP ORM__________________\n\n")

        return cursor

    def __init__(self, model_class):
        self.model_class = model_class

    def select(
        self,
        field_names: list,
        conditions_dict: dict,
        ALL_OR=0,
        ALL_IN=0,
        order_by: tuple = (),
        chunk_size=2000,
    ):
        # Build SELECT query
        # print("check", ALL_OR, ALL_IN)
        LOGIC_SELECTOR = " AND "
        if ALL_OR == 1:
            LOGIC_SELECTOR = " OR "

        if len(field_names) == 0:
            fields_format = "*"
        else:
            fields_format = ', '.join(field_names)

        if len(conditions_dict) == 0:

            query = f"SELECT {fields_format} FROM {self.model_class.table_name} "

            if len(order_by) == 1:
                query += f"ORDER BY {order_by[0]} DESC"
                parameters = []

        elif ALL_IN == 1:

            conditions_column = conditions_dict.keys()

            """
            Temporary IN solution
            """
            # making element to tuple if its not tuple to make this work for now here

            conditions_value_placeholder = [f"({i} IN %s)" for i in conditions_column]
            conditions_value_placeholder = LOGIC_SELECTOR.join(conditions_value_placeholder)

            query = f"SELECT {fields_format} FROM {self.model_class.table_name} WHERE {conditions_value_placeholder}"
            parameters = []
            for values in conditions_dict.values():

                if isinstance(values, tuple):
                    if len(values) == 0:
                        return []
                    parameters.append(values)
                elif isinstance(values, list):
                    if len(values) == 0:
                        return []
                    values = tuple(values)
                    parameters.append(values)
                else:
                    value_to_append = ((values,),)
                    parameters.append(value_to_append)

            if len(order_by) == 1:
                query += f"ORDER BY {order_by[0]} DESC"

        else:
            # AND
            conditions_column = conditions_dict.keys()

            conditions_column = list(conditions_column)

            LOGIC_SELECTOR = " AND "
            if ALL_OR == 1:
                LOGIC_SELECTOR = " OR "

            conditions_value_placeholder = [f"{i}=%s" for i in conditions_column]
            conditions_value_placeholder = LOGIC_SELECTOR.join(conditions_value_placeholder)

            parameters = list(conditions_dict.values())
            query = f"SELECT {fields_format} FROM {self.model_class.table_name} WHERE {conditions_value_placeholder}"

            if len(order_by) == 1:
                query += f"ORDER BY {order_by[0]} DESC"

        new_cursor_object, connection = self._get_cursor_and_connection()

        self._new_execute_query(new_cursor_object, query, parameters)

        field_names = [desc[0] for desc in new_cursor_object.description]

        # Fetch data obtained with the previous query execution
        # and transform it into `model_class` objects.
        # The fetching is done by batches of `chunk_size` to
        # avoid to run out of memory.
        model_objects = list()
        is_fetching_completed = False

        while not is_fetching_completed:

            result = new_cursor_object.fetchmany(size=chunk_size)

            for row_values in result:
                keys, values = field_names, row_values
                row_data = dict(zip(keys, values))
                model_objects.append(self.model_class(**row_data))

            is_fetching_completed = len(result) < chunk_size

        disconnect(new_cursor_object, connection)
        return model_objects

    def create(self, new_data: dict):
        field_names = new_data.keys()
        field_names_formated = ",".join(field_names)

        parameters = field_name_values = new_data.values()
        parameters = list(parameters)
        values_placeholder_format = ", ".join([f'{", ".join(["%s"] * len(field_names))}'])
        query = f'''
        INSERT INTO {self.model_class.table_name}
        ({field_names_formated})
        VALUES ({values_placeholder_format})
        RETURNING id
        '''
        # id and 'id' will both return data correctly

        new_cursor_object, connection = self._get_cursor_and_connection()
        self._new_execute_query(new_cursor_object, query, parameters)
        # result of the sql query is obtained from the cursor which executed the sql statements
        value_returned = new_cursor_object.fetchone()
        disconnect(new_cursor_object, connection)
        assert type(value_returned) == tuple, "datatype errors"

        return value_returned[0]

    def update(self, new_data: dict, conditions_dict: dict):
        # Build UPDATE query and parameters
        field_names = new_data.keys()
        placeholder_format = ', '.join([f'{field_name} = %s' for field_name in field_names])
        query = f"UPDATE {self.model_class.table_name} SET {placeholder_format}"
        parameters = list(new_data.values())

        if len(conditions_dict) == 0:
            new_cursor_object, connection = self._get_cursor_and_connection()
            self._new_execute_query(new_cursor_object, query, parameters)
            disconnect(new_cursor_object, connection)
        else:
            conditions_column = conditions_dict.keys()

            conditions_column = list(conditions_column)

            conditions_value_placeholder = [f"{i}=%s" for i in conditions_column]
            conditions_value_placeholder = ", ".join(conditions_value_placeholder)
            query = (
                f"UPDATE {self.model_class.table_name} SET {placeholder_format} WHERE {conditions_value_placeholder}"
            )

            conditions_value_parameters = list(conditions_dict.values())
            parameters += conditions_value_parameters
            # Execute query
            new_cursor_object, connection = self._get_cursor_and_connection()
            self._new_execute_query(new_cursor_object, query, parameters)
            disconnect(new_cursor_object, connection)

    def insert_or_update_data(self, **kwargs):
        # Class.objects.insert_or_update_data(feild1=12,fiedl2=432, ..., keys=('keyname'))
        """
        kwargs['key'] specifies the key based on which u[date or insert should be done
        """

        key_name = kwargs['key']

        del kwargs['key']

        fields_skelton_list = list(kwargs.keys())

        field_names = ", ".join(fields_skelton_list)
        field_names = "(" + field_names + ")"
        print(field_names)

        values = list(kwargs.values()).copy()
        values_placeholder = ["%s" for i in values if i != 'key']
        values_placeholder = ", ".join(values_placeholder)
        values_placeholder = "(" + values_placeholder + ")"

        parameters = values
        parameters = parameters + parameters

        fields_skelton_with_formatting_s = [f'{i}=%s' for i in fields_skelton_list]
        update_conflict_field_formatting = ", ".join(fields_skelton_with_formatting_s)

        query = f'''INSERT INTO {self.model_class.table_name} {field_names} VALUES{values_placeholder} ON CONFLICT ({key_name})
        DO UPDATE SET {update_conflict_field_formatting}'''

        new_cursor_object, connection = self._get_cursor_and_connection()
        self._new_execute_query(new_cursor_object, query, parameters)
        disconnect(new_cursor_object, connection)
        return True

    def bulk_insert(self, rows: list):
        print(rows)

        # Build INSERT query and parameters:
        field_names = rows[0].keys()
        assert all(row.keys() == field_names for row in rows[1:])  # confirm that all rows have the same fields

        fields_format = ", ".join(field_names)
        values_placeholder_format = ", ".join(
            [f'({", ".join(["%s"] * len(field_names))})'] * len(rows)
        )  # https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries

        query = f"INSERT INTO {self.model_class.table_name} ({fields_format}) " f"VALUES {values_placeholder_format}"

        parameters = list()
        for row in rows:
            row_values = [row[field_name] for field_name in field_names]
            parameters += row_values

        # Execute query
        new_cursor_object, connection = self._get_cursor_and_connection()
        self._new_execute_query(new_cursor_object, query, parameters)
        disconnect(new_cursor_object, connection)

    def select_one(self, field_name: list, conditions_dict: dict, OR=0):
        if len(field_name) == 0:
            field_name = "*"

        field_name = ", ".join(field_name)
        logical_AND_OR = "AND"
        if OR:
            logical_AND_OR = "OR"
        conditions_value_placeholder = [f"({i} = %s)" for i in conditions_dict.keys()]
        # only do AND check, OR is not added with select_one
        conditions_value_placeholder = logical_AND_OR.join(conditions_value_placeholder)
        query = f"SELECT {field_name} FROM {self.model_class.table_name} WHERE {conditions_value_placeholder}"
        parameters = list(conditions_dict.values())
        new_cursor_object, connection = self._get_cursor_and_connection()
        self._new_execute_query(new_cursor_object, query, parameters)

        field_values = new_cursor_object.fetchone()
        disconnect(new_cursor_object, connection)

        return field_values

    # Important currently deletes only based on one field
    def delete(self, **kwargs):
        # kwargs.keys()[0] are not subscriptable, need to covert to list
        # field_name = next(iter(kwargs.keys()))
        # field_value_of_row_to_be_delete = next(iter(kwargs.values()))
        # making iterator of dictionary items to use next()
        field_name, field_value = next(iter(kwargs.items()))
        # Build DELETE query
        query = f"DELETE FROM {self.model_class.table_name} WHERE {field_name}=%s"
        parameters = [field_value]

        # Execute query
        new_cursor_object, connection = self._get_cursor_and_connection()
        self._new_execute_query(new_cursor_object, query, parameters)
        disconnect(new_cursor_object, connection)

    def raw_sql_query(self, query, parameters=[], chunk_size=2000):
        new_cursor_object, connection = self._get_cursor_and_connection()
        self._new_execute_query(new_cursor_object, query, parameters)

        field_names = [desc[0] for desc in new_cursor_object.description]

        # Fetch data obtained with the previous query execution
        # and transform it into `model_class` objects.
        # The fetching is done by batches of `chunk_size` to
        # avoid to run out of memory.
        model_objects = list()
        is_fetching_completed = False
        while not is_fetching_completed:

            result = new_cursor_object.fetchmany(size=chunk_size)

            for row_values in result:

                keys, values = field_names, row_values
                row_data = dict(zip(keys, values))
                model_objects.append(self.model_class(**row_data))

            is_fetching_completed = len(result) < chunk_size

        disconnect(new_cursor_object, connection)
        return model_objects


# ----------------------- Model ----------------------- #
class MetaModel(type):
    manager_class = BaseManager

    def _get_manager(cls):
        print(f"\n\n__________________calling manager class of the class {cls}__________________\n\n")
        # print(f"class is {cls}")
        # <class 'webapp.orm.models.Mails'>
        print(cls.manager_class(model_class=cls))
        print("\n\n__________________DONE__________________\n\n")
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls):
        print()
        # print(f"called manager using _get_manager method{cls}")
        return cls._get_manager()


class BaseModel(metaclass=MetaModel):
    table_name = ""

    def __init__(self, **row_data):

        # print(row_data)
        for field_name, value in row_data.items():

            setattr(self, field_name, value)

    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self.__dict__.items()])
        return f"<{self.__class__.__name__}: ({attrs_format})>\n"


if __name__ == "__main__":
    pass
