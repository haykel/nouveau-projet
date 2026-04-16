import math
from django.conf import settings
from screening.models import Provider


RELEVANT_SPECIALTIES = [
    "Neuropediatre",
    "Pedopsychiatre",
    "Psychologue du developpement",
    "Orthophoniste",
    "Psychomotricien",
    "Pediatre du developpement",
]


class ProviderMatcherService:
    def find_nearby(self, lat, lng, radius_km=None, limit=5):
        if lat is None or lng is None:
            return []

        if radius_km is None:
            radius_km = settings.PROVIDER_SEARCH_RADIUS_KM

        providers = Provider.objects.all()
        results = []

        for provider in providers:
            dist = self._haversine(lat, lng, provider.lat, provider.lng)
            if dist <= radius_km:
                provider.distance_km = round(dist, 1)
                results.append(provider)

        results.sort(key=lambda p: (
            0 if p.specialty in RELEVANT_SPECIALTIES else 1,
            p.distance_km,
        ))

        return results[:limit]

    def _haversine(self, lat1, lng1, lat2, lng2):
        R = 6371
        lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2
        )
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
