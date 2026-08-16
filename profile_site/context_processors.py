"""Values every template needs: the services dropdown and whether Insights exist."""

from .models import Insight, Service


def site_globals(request):
    return {
        "nav_services": Service.objects.filter(is_published=True).only("title", "slug"),
        "has_insights": Insight.objects.filter(is_published=True).exists(),
    }
