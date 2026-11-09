"""
Database routers for multi-database support.
Ensures the helasabili database is read-only and prevents any write operations.
"""


class HelasabiliRouter:
    """
    A router to control all database operations on models for the helasabili app.
    This ensures the external Helasabili database is read-only.
    """

    def db_for_read(self, model, **hints):
        """
        Route read operations on helasabili models to the 'helasabili' database.
        """
        if model._meta.app_label == 'helasabili':
            return 'helasabili'
        return None

    def db_for_write(self, model, **hints):
        """
        Prevent writes to helasabili models - only allow reads.
        """
        if model._meta.app_label == 'helasabili':
            return None  # Prevent writes to external database
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models are in the helasabili app or both in default.
        """
        if obj1._meta.app_label == 'helasabili' and obj2._meta.app_label == 'helasabili':
            return True
        if obj1._meta.app_label != 'helasabili' and obj2._meta.app_label != 'helasabili':
            return None
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations are never applied to the helasabili database.
        """
        if app_label == 'helasabili':
            return False
        return None
