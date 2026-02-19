from tortoise.models import Model
from tortoise import fields

class Admin(Model):
    id= fields.UUIDField(pk=True)
    name = fields.CharField(max_length=20)
    email = fields.CharField(max_length=75, unique=True)
    password = fields.TextField()

    class Meta:
        table = "Admins"

