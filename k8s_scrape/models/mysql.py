from datetime import datetime

from peewee import *

db = MySQLDatabase('k8s_stackoverflow_analysis', user='root', host='localhost', port=3306)


class StackoverflowPost(Model):
    id = IntegerField(primary_key=True)
    title = CharField()
    url = CharField()
    tag_array = CharField(null=True)
    content = TextField(null=True)
    content_clean = TextField(null=True)
    content_html = TextField(null=True)
    votes = IntegerField(null=True)
    answers = IntegerField(default=0)
    views = IntegerField(default=0)
    accepted = BooleanField(default=False)
    detailed = BooleanField(default=False)
    definitive = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'stackoverflow_posts'


class StackoverflowTag(Model):
    id = AutoField(primary_key=True)
    name = CharField()

    class Meta:
        database = db
        table_name = 'stackoverflow_tags'


class StackoverflowPostTag(Model):
    id = AutoField(primary_key=True)
    post_id = ForeignKeyField(StackoverflowPost)
    tag_id = ForeignKeyField(StackoverflowTag)

    class Meta:
        database = db
        table_name = 'stackoverflow_posts_tags'
