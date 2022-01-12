from orm_manager import BaseModel, BaseManager


class Groups(BaseModel):
    manager_class = BaseManager
    table_name = "groups"


if __name__ == "__main__":
    Groups.objects.create(new_data={'group_mail': "hello@tes1212t.asd"})
