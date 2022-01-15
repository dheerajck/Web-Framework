from .database_folder.sql_setup import connect, disconnect


class BaseManager:
    @classmethod
    def _get_cursor(cls):
        connection = connect()
        connection.autocommit = True
        return connection.cursor()

    @classmethod
    def _execute_query(cls, query, params=None):
        cursor = cls._get_cursor()

        print("_______________________________++++++++++++++++==")
        # print("Current sql query", query, params)
        cursor.execute(query, params)

        if "SELECT" in query:
            # print(cursor)

            field_names = [desc[0] for desc in cursor.description]
        #     print(field_names)
        # print("_______________________________++++++++++++++++==")
        return cursor

    def __init__(self, model_class):
        self.model_class = model_class

    def select(self, field_names: set, conditions_dict: dict, ALL_OR=0, chunk_size=2000):
        # Build SELECT query

        if len(field_names) == 0:
            fields_format = "*"
        else:
            fields_format = ', '.join(field_names)

        query = f"SELECT {fields_format} FROM {self.model_class.table_name}"

        cursor = self._get_cursor()

        if len(conditions_dict) == 0:
            # cursor.execute(query)
            used_cursor_object = self._execute_query(query)
        else:
            conditions_column = conditions_dict.keys()
            # print()
            # print(conditions_dict)
            # print(conditions_column)
            # print()
            conditions_column = list(conditions_column)
            # print(conditions_column)

            # conditions_value_placeholder = "=%s, ".join(conditions_column)
            LOGIC_SELECTOR = " AND "
            if ALL_OR == 1:
                LOGIC_SELECTOR = " OR "

            conditions_value_placeholder = [f"{i}=%s" for i in conditions_column]
            conditions_value_placeholder = LOGIC_SELECTOR.join(conditions_value_placeholder)

            conditions_value_parameters = list(conditions_dict.values())
            query = f"SELECT {fields_format} FROM {self.model_class.table_name} WHERE {conditions_value_placeholder}"

            # # Execute query
            # cursor = self._get_cursor()

            # # this works
            # cursor.execute(query, conditions_value_parameters)

            used_cursor_object = self._execute_query(query, conditions_value_parameters)

        # print("_______________________________++++++++++++++++==")
        # print(query)
        field_names = [desc[0] for desc in used_cursor_object.description]
        # print(field_names)
        # print("_______________________________++++++++++++++++==")

        # Fetch data obtained with the previous query execution
        # and transform it into `model_class` objects.
        # The fetching is done by batches of `chunk_size` to
        # avoid to run out of memory.
        model_objects = list()
        is_fetching_completed = False
        # print(is_fetching_completed)
        while not is_fetching_completed:
            # print(is_fetching_completed)
            result = used_cursor_object.fetchmany(size=chunk_size)

            # print("result", result)
            # print('start')
            for row_values in result:
                # print("current resultdata", row_values)
                keys, values = field_names, row_values
                # print(keys, values)
                row_data = dict(zip(keys, values))
                # print(row_data)
                # print(self.model_class(**row_data))
                model_objects.append(self.model_class(**row_data))
            is_fetching_completed = len(result) < chunk_size
            # print('stop')

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

    def update(self, new_data: dict, conditions_dict):
        # Build UPDATE query and params
        field_names = new_data.keys()
        placeholder_format = ', '.join([f'{field_name} = %s' for field_name in field_names])
        query = f"UPDATE {self.model_class.table_name} SET {placeholder_format}"
        params = list(new_data.values())

        if len(conditions_dict) == 0:
            self._execute_query(query, params)
        else:
            conditions_column = conditions_dict.keys()
            print()
            print(conditions_dict)
            print(conditions_column)
            print()
            conditions_column = list(conditions_column)
            print(conditions_column)

            # conditions_value_placeholder = "=%s, ".join(conditions_column)
            conditions_value_placeholder = [f"{i}=%s" for i in conditions_column]
            conditions_value_placeholder = ", ".join(conditions_value_placeholder)
            query = (
                f"UPDATE {self.model_class.table_name} SET {placeholder_format} WHERE {conditions_value_placeholder}"
            )

            conditions_value_parameters = list(conditions_dict.values())
            params += conditions_value_parameters
            # Execute query
            self._execute_query(query, params)

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
        print(values_placeholder)

        print("///////////////////////////////////////////////////////////////////////////////////////////////")
        print(list(kwargs.values()).copy())

        print("kwargs is", kwargs)
        print()
        print()
        print()
        parameters = values
        parameters = parameters + parameters

        # fields_skelton_list
        fields_skelton_with_formatting_s = [f'{i}=%s' for i in fields_skelton_list]
        update_conflict_field_formatting = ", ".join(fields_skelton_with_formatting_s)

        query = f'''INSERT INTO {self.model_class.table_name} {field_names} VALUES{values_placeholder} ON CONFLICT ({key_name})
        DO UPDATE SET {update_conflict_field_formatting}'''
        print(query)
        print("///////////////////////////////////////////////////////////////////////////////////////////////")

        self._execute_query(query, parameters)
        return True

    # currently deletes only based on one field
    def delete(self, **kwargs):
        # kwargs.keys()[0] are not subscriptable, need to covert to list
        # field_name = next(iter(kwargs.keys()))
        # field_value_of_row_to_be_delete = next(iter(kwargs.values()))
        # making iterator of dictionary items to use next()
        field_name, field_value = next(iter(kwargs.items()))
        # Build DELETE query
        query = f"DELETE FROM {self.model_class.table_name} WHERE {field_name}=%s"
        parameter = [field_value]

        # Execute query
        self._execute_query(query, parameter)


# ----------------------- Model ----------------------- #
class MetaModel(type):
    manager_class = BaseManager

    def _get_manager(cls):
        print(f"class is {cls}")
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls):
        print("called manager using _get_manager method")
        return cls._get_manager()


class BaseModel(metaclass=MetaModel):
    table_name = ""

    def __init__(self, **row_data):
        print(row_data, 1)

        for field_name, value in row_data.items():

            setattr(self, field_name, value)

    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self.__dict__.items()])
        return f"<{self.__class__.__name__}: ({attrs_format})>\n"
