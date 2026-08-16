import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .models import (
    Client, FirmValue, IndustrySegment, Insight, KeyFigure, Office, PresenceCity,
    Service, TeamMember,
)

logger = logging.getLogger(__name__)


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _notify(submission):
    """Email the partners. A mail failure must never lose the saved enquiry."""
    if not settings.CONTACT_NOTIFY_EMAILS:
        return
    lines = [
        f"Name:     {submission.name}",
        f"Email:    {submission.email}",
        f"Phone:    {submission.phone or '-'}",
        f"Company:  {submission.organisation or '-'}",
        f"Interest: {submission.service_interest or 'Not specified'}",
        "",
        submission.message,
    ]
    try:
        send_mail(
            subject=f"Website enquiry - {submission.name}",
            message="\n".join(lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.CONTACT_NOTIFY_EMAILS,
            fail_silently=False,
        )
    except Exception:
        logger.exception("Could not email enquiry #%s", submission.pk)


def home(request):
    featured = Service.objects.filter(is_published=True, is_featured=True)[:6]
    return render(request, "site/home.html", {
        "nav": "home",
        "key_figures": KeyFigure.objects.filter(is_published=True),
        "featured_services": featured or Service.objects.filter(is_published=True)[:6],
        "values": FirmValue.objects.filter(is_published=True),
        "major_clients": Client.objects.filter(is_published=True, tier=Client.Tier.MAJOR)[:9],
        "lead": TeamMember.objects.filter(is_published=True).first(),
        "segments": IndustrySegment.objects.filter(is_published=True),
        "latest_insights": Insight.objects.filter(is_published=True)[:3],
    })


def about(request):
    return render(request, "site/about.html", {
        "nav": "about",
        "key_figures": KeyFigure.objects.filter(is_published=True),
        "values": FirmValue.objects.filter(is_published=True),
        "cities": PresenceCity.objects.filter(is_published=True),
        "offices": Office.objects.filter(is_published=True),
        "team": TeamMember.objects.filter(is_published=True)[:3],
    })


def services(request):
    return render(request, "site/services.html", {
        "nav": "services",
        "services": Service.objects.filter(is_published=True),
        "segments": IndustrySegment.objects.filter(is_published=True),
    })


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_published=True)
    return render(request, "site/service_detail.html", {
        "nav": "services",
        "service": service,
        "other_services": Service.objects.filter(is_published=True).exclude(pk=service.pk),
    })


def clients(request):
    return render(request, "site/clients.html", {
        "nav": "clients",
        "major_clients": Client.objects.filter(is_published=True, tier=Client.Tier.MAJOR),
        "other_clients": Client.objects.filter(is_published=True, tier=Client.Tier.OTHER),
        "segments": IndustrySegment.objects.filter(is_published=True),
    })


def team(request):
    return render(request, "site/team.html", {
        "nav": "team",
        "team": TeamMember.objects.filter(is_published=True),
    })


def team_detail(request, slug):
    member = get_object_or_404(TeamMember, slug=slug, is_published=True)
    return render(request, "site/team_detail.html", {
        "nav": "team",
        "member": member,
        "colleagues": TeamMember.objects.filter(is_published=True).exclude(pk=member.pk),
    })


def insights(request):
    return render(request, "site/insights.html", {
        "nav": "insights",
        "insights": Insight.objects.filter(is_published=True),
    })


def insight_detail(request, slug):
    insight = get_object_or_404(Insight, slug=slug, is_published=True)
    return render(request, "site/insight_detail.html", {
        "nav": "insights",
        "insight": insight,
        "more": Insight.objects.filter(is_published=True).exclude(pk=insight.pk)[:3],
    })


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.source_page = request.POST.get("source_page", "")[:200]
            submission.ip_address = _client_ip(request)
            submission.save()
            _notify(submission)
            return redirect("profile_site:enquiry_received")
        messages.error(request, "Please check the highlighted fields and send again.")
    else:
        initial = {}
        slug = request.GET.get("service")
        if slug:
            match = Service.objects.filter(slug=slug, is_published=True).first()
            if match:
                initial["service_interest"] = match
        form = ContactForm(initial=initial)

    return render(request, "site/contact.html", {
        "nav": "contact",
        "form": form,
        "offices": Office.objects.filter(is_published=True),
        "lead": TeamMember.objects.filter(is_published=True).first(),
    })


def enquiry_received(request):
    return render(request, "site/enquiry_received.html", {"nav": "contact"})
