from django.db import models

class Student(models.Model):
    msv = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)  # Tên sinh viên

    def __str__(self):
        return self.name