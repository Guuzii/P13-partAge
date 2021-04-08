from django.contrib import admin

from mission.models.mission_category import MissionCategory
from mission.models.mission import Mission


class CustomMissionCategoryAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class CustomMissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description', 'created_at', 'updated_at', 'category', 'status', 'bonus_reward',)
    list_editable = ('status',)
    list_filter = ('created_at', 'updated_at', 'status',)
    readonly_fields = ['created_at', 'bearer_user', 'bonus_reward']
    search_fields = ('title', 'category','status')
    ordering = ('-updated_at', '-created_at',)
    filter_horizontal = ()
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(MissionCategory, CustomMissionCategoryAdmin)
admin.site.register(Mission, CustomMissionAdmin)
