from tortoise.models import Model
from tortoise import fields

class Audio(Model):
    audio_id=fields.UUIDField(pk=True)
    audio_path=fields.TextField(null=False)
    user=fields.ForeignKeyField("models.User", related_name="audio_files")
    size_of_audio=fields.TextField()
    category=fields.TextField(null=True)
    format_type=fields.TextField()
    duration=fields.TextField()  # 8:980
    transcripted=fields.BooleanField(default=False)
    summary_created=fields.BooleanField(default=False)
    transcript=fields.TextField(null=True)
    transcript_created_at=fields.DateField(null=True)
    summary=fields.TextField(null=True)
    summary_created_at=fields.DateField(null=True)

    class Meta:
        table = "Audio_info"

    
    