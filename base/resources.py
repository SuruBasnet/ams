from import_export import resources
from .models import Artist

class ArtistResource(resources.ModelResource):
    class Meta:
        model = Artist