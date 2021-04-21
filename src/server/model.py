from peewee import SqliteDatabase, Model, AutoField, CharField, FloatField, BlobField, ForeignKeyField

db = SqliteDatabase('osv.sqlite')


class User(Model):
    id = AutoField()
    name = CharField(unique=True)

    class Meta:
        database = db

class SingleMin(Model):
    user_id = ForeignKeyField(User, field=User.id, backref='singlemin')
    single_min_tpl = BlobField()
    threshold = FloatField()

    class Meta:
        database = db

class MultiMean(Model):
    user_id = ForeignKeyField(User, field=User.id, backref='multimean')
    signatures = BlobField()
    threshold = FloatField()

    class Meta:
        database = db

class EB_DBA(Model):
    user_id = ForeignKeyField(User, field=User.id, backref='eb_dba')
    eb_dba_tpl = BlobField()
    threshold = FloatField()

    class Meta:
        database = db

class LS_DBA(Model):
    user_id = ForeignKeyField(User, field=User.id, backref='ls_dba')
    eb_dba_tpl = BlobField()
    ls = BlobField()
    threshold = FloatField()

    class Meta:
        database = db


if __name__ == '__main__':
    db.connect()
    db.create_tables([User, SingleMin, MultiMean, EB_DBA, LS_DBA])
