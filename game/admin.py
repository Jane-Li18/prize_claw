from django.contrib import admin
from .models import Prize, Game, Leaderboard

class PrizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'probability', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    actions = ['hard_delete_prizes', 'deactivate_prizes', 'activate_prizes']
    
    def deactivate_prizes(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_prizes.short_description = "Deactivate selected prizes"
    
    def activate_prizes(self, request, queryset):
        queryset.update(is_active=True)
    activate_prizes.short_description = "Activate selected prizes"
    
    def hard_delete_prizes(self, request, queryset):
        # This will delete from Django DB but not from Supabase
        queryset.delete()
    hard_delete_prizes.short_description = "Hard delete selected prizes (Django only)"

class GameAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'prize', 'won')
    list_filter = ('won',)
    search_fields = ('player_name', 'prize__name')

class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'score', 'created_at')
    ordering = ('-score', 'created_at')

admin.site.register(Prize, PrizeAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
