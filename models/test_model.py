from models.base_model import SQLModel


class Test(SQLModel):
    sql_create = '''
        CREATE TABLE `test` (
            `id` INT NOT NULL AUTO_INCREMENT,
            PRIMARY KEY (`id`)
        )
    '''
