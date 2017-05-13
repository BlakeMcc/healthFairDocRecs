from django.contrib import admin
from screener.models import *


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    pass

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    pass
