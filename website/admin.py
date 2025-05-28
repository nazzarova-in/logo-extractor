from django.contrib import admin
from .models import WebsiteURL, TLD

@admin.register(WebsiteURL)
class WebsiteURLAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'tld')

admin.site.register(TLD)

