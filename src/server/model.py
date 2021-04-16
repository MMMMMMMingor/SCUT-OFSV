from peewee import SqliteDatabase, Model, AutoField, CharField, BlobField, ForeignKeyField

db = SqliteDatabase('osv.sqlite')


class User(Model):
    id = AutoField()
    name = CharField(unique=True)
    signatures = BlobField()

    class Meta:
        database = db

class SingleMin(Model):
    user_id = ForeignKeyField(User, field=User.id, backref='singlemintpl')
    single_min_tpl = BlobField()

    class Meta:
        database = db

class EB_DBA(Model):
    user_id = ForeignKeyField(User, field=User.id, backref='eb_dba')
    eb_dba_tpl = BlobField()

    class Meta:
        database = db

class LS_DBA(Model):
    user_id = ForeignKeyField(User, field=User.id, backref='ls_dba')
    eb_dba_tpl = BlobField()
    ls = BlobField()

    class Meta:
        database = db


if __name__ == '__main__':
    db.connect()
    db.create_tables([User, SingleMin, EB_DBA, LS_DBA])
