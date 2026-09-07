from django.db import models
from django.contrib.auth.models import User
from helpdesk.models import Ticket
from admin_automation.models import InternalLetter
from workflow.models import LeaveRequest, PurchaseRequest, MissionRequest
from meetings.models import Meeting
from documents.models import Document

class Dashboard(models.Model):
    # فقط برای آمار کلی
    pass
