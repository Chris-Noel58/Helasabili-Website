from django.contrib import admin
from .models import HelasabiliInventory


@admin.register(HelasabiliInventory)
class HelasabiliInventoryAdmin(admin.ModelAdmin):
    """
    Read-only admin interface for viewing Helasabili Inventory items.
    """
    list_display = ('id', 'product_name')
    search_fields = ('product_name',)
    readonly_fields = ('id', 'product_name')
    
    def has_add_permission(self, request):
        """Disable adding new items"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting items"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow viewing but not editing"""
        return True
