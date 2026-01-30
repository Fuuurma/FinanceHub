from django.db import models
from datetime import datetime


class TaskFailure(models.Model):
    task_name = models.CharField(max_length=255)
    args = models.TextField(blank=True, null=True)
    kwargs = models.TextField(blank=True, null=True)
    exception = models.TextField()
    traceback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    retried = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        db_table = "task_failures"

    def __str__(self):
        return f"{self.task_name} - {self.created_at}"
