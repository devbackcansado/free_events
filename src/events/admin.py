from django.contrib import admin

# Register your models here.
from events.models import Event, Subscription, SubscriptionStatus


admin.site.register(Event)
admin.site.register(Subscription)
admin.site.register(SubscriptionStatus)
