from django.contrib import admin
from .models import * 
# Register your models here.
class instrauseradmin(admin.ModelAdmin):
    list_display = ["id","username","email","created_at"]
    search_fields = ["username","email"]
    list_display_links = ["username"]
    list_per_page = 10  
    list_filter = ["created_at"]
    list_order_by_desc = ["created_at"]

class instrapostadmin(admin.ModelAdmin):
    list_display = ["id","caption"]

admin.site.register(instrauser,instrauseradmin)
admin.site.register(instrapost,instrapostadmin)
admin.site.register(followusers)
admin.site.register(notification)
admin.site.register(like_unlike)
admin.site.register(instrareels)
admin.site.register(instrastory)
admin.site.register(chatroom)
admin.site.register(all_messages)
admin.site.register(add_comments)