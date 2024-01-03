from django.db import models


# Create your models here.
class Client(models.Model):
    company_name = models.CharField(max_length=255)
    gst_no = models.CharField(max_length=20)
    email_id = models.EmailField()
    contact_no = models.CharField(max_length=15)
    contact_person_name = models.CharField(max_length=100)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField()

    def __str__(self):
        return self.company_name
    
class File(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='files', default=1)

    def __str__(self):
        return self.title

    
    
class Job(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    )

    job_number = models.CharField(max_length=20)
    project_name = models.CharField(max_length=255)
    po_date = models.DateField()
    project_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    file = models.ManyToManyField(File, related_name='jobs')


    def __str__(self):
        return f"{self.job_number} - {self.project_name}"
    
    def delete(self, *args, **kwargs):
        # Delete associated files and then delete the Job
        for file_obj in self.files.all():
            file_obj.file.delete(save=False)  # Delete the file from storage
            file_obj.delete()  # Delete the File instance
        super().delete(*args, **kwargs)

    