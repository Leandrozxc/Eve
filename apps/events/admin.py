from django.contrib import admin
from .models import Company, CompanyMember, Event, EventAssignment

admin.site.register(Company)
admin.site.register(CompanyMember)
admin.site.register(Event)
admin.site.register(EventAssignment)
