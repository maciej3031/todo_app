from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
choice = Table('choice', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('question', Text, nullable=False),
    Column('choice_text', Text, nullable=False),
    Column('votes', Integer),
)

question = Table('question', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('question_text', Text, nullable=False),
    Column('pub_date', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['choice'].create()
    post_meta.tables['question'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['choice'].drop()
    post_meta.tables['question'].drop()
