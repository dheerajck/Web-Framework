from .database_folder.sql_setup import connect, disconnect
from ..clean_print_function.print_enable_and_disable_function import enablePrint, blockPrint


class BaseManager:
    @classmethod
    def _get_cursor(cls):
        connection = connect()
        connection.autocommit = True
        return connection.cursor()

    @classmethod
    def _execute_query(cls, query, params=None):
        # blockPrint()
        cursor = cls._get_cursor()

        print("\n\n__________________START ORM__________________\n\n")

        print(params)
        print("Current sql query", query, params)
        cursor.execute(query, params)

        if "SELECT" in query:
            # print(cursor)

            field_names = [desc[0] for desc in cursor.description]
        #     print(field_names)
        print("\n\n__________________STOP ORM__________________\n\n")

        # to fetch data/ result cursor is passed to the method
        # enablePrint()
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
            # cursor.execute(query)

            query = f"SELECT {fields_format} FROM {self.model_class.table_name} "

            if len(order_by) == 1:
                query += f"ORDER BY {order_by[0]} DESC"

            used_cursor_object = self._execute_query(query)
        elif ALL_IN == 1:

            conditions_column = conditions_dict.keys()
            # print('entered here')
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
            used_cursor_object = self._execute_query(query, parameters)

        else:
            # AND
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
            if len(order_by) == 1:
                query += f"ORDER BY {order_by[0]} DESC"
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
        # print("start")
        while not is_fetching_completed:
            # print(is_fetching_completed)
            result = used_cursor_object.fetchmany(size=chunk_size)

            # print(len(result))
            # print()
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
        # print("fetching done")
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
        VALUES ({values_placeholder_format})
        RETURNING id
        '''
        # id and 'id' both are returning data correctly

        returned_created_row_id_cursor = self._execute_query(query, params)
        # result of the sql query is obtained from the cursor which executed the sql statements
        value_returned = returned_created_row_id_cursor.fetchone()
        assert type(value_returned) == tuple, "datatype errors"
        print("tuple")

        print(value_returned, type(value_returned))
        return value_returned[0]

    # def bulk_insert(self, rows: list):
    #     pass

    def update(self, new_data: dict, conditions_dict: dict):
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
        # print(values_placeholder)

        # print("///////////////////////////////////////////////////////////////////////////////////////////////")
        # print(list(kwargs.values()).copy())

        # print("kwargs is", kwargs)
        # print()
        # print()
        # print()
        parameters = values
        parameters = parameters + parameters

        # fields_skelton_list
        fields_skelton_with_formatting_s = [f'{i}=%s' for i in fields_skelton_list]
        update_conflict_field_formatting = ", ".join(fields_skelton_with_formatting_s)

        query = f'''INSERT INTO {self.model_class.table_name} {field_names} VALUES{values_placeholder} ON CONFLICT ({key_name})
        DO UPDATE SET {update_conflict_field_formatting}'''
        # print(query)
        # print("///////////////////////////////////////////////////////////////////////////////////////////////")

        self._execute_query(query, parameters)
        return True

    def bulk_insert(self, rows: list):
        print(rows)

        # Build INSERT query and params:
        field_names = rows[0].keys()
        assert all(row.keys() == field_names for row in rows[1:])  # confirm that all rows have the same fields

        fields_format = ", ".join(field_names)
        values_placeholder_format = ", ".join(
            [f'({", ".join(["%s"] * len(field_names))})'] * len(rows)
        )  # https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries

        query = f"INSERT INTO {self.model_class.table_name} ({fields_format}) " f"VALUES {values_placeholder_format}"
        print(rows)
        print("done row")
        params = list()
        for row in rows:
            print('start')
            row_values = [row[field_name] for field_name in field_names]
            print(row_values)
            params += row_values

        # Execute query
        self._execute_query(query, params)

    def select_one(self, field_name: list, conditions_dict: dict):
        if len(field_name) == 0:
            field_name = "*c"

        field_name = ", ".join(field_name)
        conditions_value_placeholder = [f"({i} = %s)" for i in conditions_dict.keys()]
        conditions_value_placeholder = ", ".join(conditions_value_placeholder)
        query = f"SELECT {field_name} FROM {self.model_class.table_name} WHERE {conditions_value_placeholder}"
        parameters = list(conditions_dict.values())
        used_cursor = self._execute_query(query, parameters)
        field_values = used_cursor.fetchone()

        # fetch one also returns a list and it contains every element specified in the select like ["name", "password"]
        # print(field_values, 111111111112)
        # print(field_values[0]) will throw error if result is empty
        # print(field_values[0])
        # first index contain first field name, if email and id in select list, field_values[0] gives email field_values[1] gives id
        # return field_values[0]
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
        parameter = [field_value]

        # Execute query
        self._execute_query(query, parameter)

    def raw_sql_query(self, query, paramaters=[], chunk_size=2000):
        if paramaters == []:
            used_cursor_object = self._execute_query(query)
        else:
            used_cursor_object = self._execute_query(query, paramaters)

        field_names = [desc[0] for desc in used_cursor_object.description]
        # print(field_names)
        # print("_______________________________++++++++++++++++==")

        # Fetch data obtained with the previous query execution
        # and transform it into `model_class` objects.
        # The fetching is done by batches of `chunk_size` to
        # avoid to run out of memory.
        model_objects = list()
        is_fetching_completed = False
        # print("start")
        while not is_fetching_completed:
            # print(is_fetching_completed)
            result = used_cursor_object.fetchmany(size=chunk_size)

            # print(len(result))
            # print()
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
        # print("fetching done")
        return model_objects


# ----------------------- Model ----------------------- #
class MetaModel(type):
    manager_class = BaseManager

    def _get_manager(cls):
        print(f"\n\n__________________calling manager class of the class {cls}__________________\n\n")
        # print(f"class is {cls}")
        # <class 'webapp.orm.models.Mails'>
        print(cls.manager_class(model_class=cls))
        print(f"\n\n__________________DONE__________________\n\n")
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls):
        print()
        # print(f"called manager using _get_manager method{cls}")
        return cls._get_manager()


class BaseModel(metaclass=MetaModel):
    table_name = ""

    def __init__(self, **row_data):
        # print()
        # print()
        # print(row_data, 1111111111111111111111111111111111111111111)

        for field_name, value in row_data.items():

            setattr(self, field_name, value)

    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self.__dict__.items()])
        return f"<{self.__class__.__name__}: ({attrs_format})>\n"


if __name__ == "__main__":
    emplyee = 1
    employees_data = [
        {"first_name": "Yan", "last_name": "KIKI", "salary": 10000},
        {"first_name": "Yoweri", "last_name": "ALOH", "salary": 15000},
    ]
    employee.objects.bulk_insert(rows=employees_data)
    '''
    join sample data
    user_id = get_user_from_environ(environ)
    Usersent_table_name = UserSent.objects.model_class.table_name
    Userinbox_table_name = UserInbox.objects.model_class.table_name
    inbox = Mails.objects.select(
        {f"{Usersent_table_name}.user_id as A", f"{Userinbox_table_name}.user_id as B"},
        {f"{Userinbox_table_name}.user_id": user_id},
        0,  # 0 => AND
        1,  # 1 => field IN tuples , 0 => field=value
        ("created_date",),  # order by created_date descending order
        join_model=[(Userinbox_table_name, "id", "mail_id"), (Usersent_table_name, "mail_id", "mail_id")],
    )
    # print(len(inbox), type(inbox)) # 0 => <class 'list'>

    '''
    user_id = get_user_from_environ(environ)
    Usersent_table_name = UserSent.objects.model_class.table_name
    Userinbox_table_name = UserInbox.objects.model_class.table_name
    inbox = Mails.objects.select(
        {f"{Usersent_table_name}.user_id as A", f"{Userinbox_table_name}.user_id as B"},
        {f"{Userinbox_table_name}.user_id": user_id},
        0,  # 0 => AND
        1,  # 1 => field IN tuples , 0 => field=value
        ("created_date",),  # order by created_date descending order
        join_model=[(Userinbox_table_name, "id", "mail_id"), (Usersent_table_name, "mail_id", "mail_id")],
    )
    # print(len(inbox), type(inbox)) # 0 => <class 'list'>
