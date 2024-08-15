from django.db import models
from user.models import User, Department
from datetime import datetime



class Day(models.Model):
    CATEGORIES = [
        ('weekend','Weekend'),
        ('public_holiday','Public Holiday')
    ]
    date = models.DateField(null=False, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, null=False, blank=False)

    def __str__(self):
        return self.category + self.date.strftime('%Y-%m-%d')



class InconvenienceRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('manager_approved', 'Manager Approved'),
        ('work_done', 'Work Done'),
        ('hr_approval', 'HR Approval'),
        ('completed', 'Completed'),
        ('rejected','Rejected')
    ]
    request_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='inconvenience_requests')
    department_rep = models.ForeignKey(User, on_delete=models.PROTECT, related_name='department_representative_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    line_manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='line_manager_requests',null=True, blank=True)
    hr = models.ForeignKey(User, on_delete=models.PROTECT, related_name='hr_requests', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def generate_request_id(self):
        current_year = datetime.now().year
        last_request = InconvenienceRequest.objects.order_by('id').last()
        if not last_request:
            new_id = 1
        else:
            new_id = last_request.id + 1
        return f"IAR/{current_year}/{new_id:04d}"
    
    def __str__(self):
        return f"Request {self.id} by {self.department_rep}"
    

    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = self.generate_request_id()

        super().save(*args, **kwargs)

    def transition_status(self, new_status):
        valid_transitions = {
            'draft': ['submitted'],
            'submitted': ['manager_approved','rejected'],
            'manager_approved': ['work_done'],
            'work_done': ['hr_approval'],
            'hr_approval': ['completed'],
        }

        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")

        self.status = new_status
        self.save()

        # Additional actions can be taken here, such as sending notifications
        if new_status == 'submitted':
            self.notify_line_manager()
        elif new_status == 'manager_approval':
            self.notify_hr()
        elif new_status == 'hr_approval':
            self.notify_completion()

    def notify_line_manager(self):
        # Logic to notify the line manager
        pass

    def notify_hr(self):
        # Logic to notify HR
        pass

    def notify_completion(self):
        # Logic to notify about completion
        pass



class InconvenienceRequestLine(models.Model):
    RESPONSE_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    inconvenience_request = models.ForeignKey(InconvenienceRequest, on_delete=models.CASCADE, related_name='lines')
    job_description = models.CharField()   
    employee = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inconvenience_request_lines')
    days = models.ManyToManyField(Day, related_name='inconvenience_request_lines')
    no_of_weekend = models.IntegerField(null=True, blank=True)
    no_of_ph = models.IntegerField(null=True, blank=True)
    no_of_days = models.IntegerField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    response = models.CharField(max_length=20, choices=RESPONSE_CHOICES, null=True, blank=True)
    response_time = models.DateTimeField(null=True, blank=True)
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, null=True, blank=True, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Line {self.id} - Request {self.inconvenience_request.id}"
    
    def save(self, *args, **kwargs):
        if self.pk is not None:  # Existing instance
            self.update_calculations()
            super().save(*args, **kwargs)

        else:  # New instance
            super().save(*args, **kwargs)  # Save first to ensure pk is set
            self.update_calculations()

    def update_calculations(self):
        # Update no_of_weekend, no_of_ph, no_of_days, and amount
        self.no_of_weekend = self.calculate_no_of_weekends()
        self.no_of_ph = self.calculate_no_of_public_holidays()
        self.no_of_days = self.days.count()
        self.amount = self.calculate_amount()

    def calculate_no_of_weekends(self):
        return sum(1 for day in self.days.all() if day.category=='weekend')  # Assuming weekends are Saturday (5) and Sunday (6)

    def calculate_no_of_public_holidays(self):
        return sum(1 for day in self.days.all() if day.category=='public_holiday')  # Assuming Day model has an 'is_public_holiday' field

    def calculate_amount(self):
        return (self.no_of_weekend * 3500) + (self.no_of_ph * 15000)


