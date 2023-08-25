from peewee import *
from k8s_scrape.models import sqlite_models


class StackoverflowPostTag(Model):
    id = AutoField(primary_key=True)
    post_id = ForeignKeyField(sqlite_models.StackoverflowPost)
    tag_id = ForeignKeyField(sqlite_models.StackoverflowTag)

    class Meta:
        database = sqlite_models.db
        table_name = 'stackoverflow_post_tags'
