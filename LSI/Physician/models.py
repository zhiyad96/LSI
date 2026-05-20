from django.db import models

class PatientMaster(models.Model):
    mrn = models.CharField(max_length=20, unique=True)
    patient_name = models.CharField(max_length=150)
    age = models.SmallIntegerField()
    gender = models.CharField(max_length=10)
    nationality = models.CharField(max_length=80)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=10, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patient_master'

    def __str__(self):
        return f"{self.patient_name} ({self.mrn})"
