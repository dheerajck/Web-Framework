from orm_manager import BaseModel, BaseManager


class Groups(BaseModel):
    manager_class = BaseManager
    table_name = "groups"


if __name__ == "__main__":
    Groups.objects.update(new_data={'group_mail': "A"}, conditions_dict={'id': 1})
    a = Groups.objects.select({}, {'id': 1})
    print(a)
    # Groups.objects.create(new_data={'group_mail': "1"})
    # a = Groups.objects.select({}, {'id': 2})

    # print(1)
    # print(a)
    # print(vars(a[0]))

    # a = Groups.objects.select({}, {'id': 2})

    # print(1)
    # print(a)
    # print("_________________________________________________________-----")
    # print('first printing')
    # print(a[0].group_mail)
    # print(a)
    # print("_________________________________________________________-----")
    # print(vars(a[0]))

    # Groups.objects.update(new_data={'group_mail': "a1"})

    # a = Groups.objects.select({}, {})

    # print("_________________________________________________________-----")
    # print(a[0].group_mail)
    # print(a)
    # print("_________________________________________________________-----")
    # print(vars(a[0]))
