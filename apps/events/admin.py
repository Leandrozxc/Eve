from django.contrib import admin
from .models import Company, CompanyMember, Event, EventAssignment, AttendanceRecord, MemberAvailability, EventTask, ShiftSwapRequest

admin.site.register(Company)
admin.site.register(CompanyMember)
admin.site.register(Event)
admin.site.register(EventAssignment)
admin.site.register(AttendanceRecord)
admin.site.register(MemberAvailability)
admin.site.register(EventTask)
admin.site.register(ShiftSwapRequest)
