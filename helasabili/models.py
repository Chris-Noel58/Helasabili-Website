"""
Models for reading from the external Helasabili database.
These models map to existing tables in the Helasabili database.
"""

from django.db import models


class HelasabiliInventory(models.Model):
    """
    Model mapping to the Inventories table in the Helasabili database.
    Retrieves product names as land/property listings.
    """
    id = models.BigIntegerField(primary_key=True, db_column='id')
    product_name = models.CharField(max_length=255, db_column='ProductName')

    class Meta:
        managed = False  # Don't let Django manage this table
        db_table = 'Inventories'  # Map to the actual table name in the database
        app_label = 'helasabili'
        verbose_name = 'Helasabili Inventory Item'
        verbose_name_plural = 'Helasabili Inventory Items'

    def __str__(self):
        return self.product_name
