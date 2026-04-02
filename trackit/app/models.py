from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DEV', 'Developer'),
        ('REPORTER', 'Reporter'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    developers = models.ManyToManyField(
        User,
        blank=True,
        related_name="projects",
        limit_choices_to={"role": "DEV"},
    )


class Bug(models.Model):
    STATUS = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    PRIORITY = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='OPEN')
    priority = models.CharField(max_length=10, choices=PRIORITY)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned')


class Comment(models.Model):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
