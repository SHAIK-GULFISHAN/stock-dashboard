from django.contrib import admin
from .models import StockHolding


@admin.register(StockHolding)
class StockHoldingAdmin(admin.ModelAdmin):
    list_display = ('user', 'symbol', 'quantity', 'buy_price', 'created_at')
    list_filter = ('symbol', 'created_at')
    search_fields = ('user__username', 'symbol')
    readonly_fields = ('created_at',)