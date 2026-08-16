import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import (
    Client, ContactSubmission, FirmValue, IndustrySegment, Insight, KeyFigure,
    Office, PresenceCity, Service, TeamMember,
)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "email_link", "service_interest", "status", "created_at")
    list_filter = ("status", "service_interest", "created_at")
    search_fields = ("name", "email", "phone", "organisation", "message")
    date_hierarchy = "created_at"
    list_per_page = 40
    ordering = ("-created_at",)
    readonly_fields = ("name", "email", "phone", "organisation", "service_interest",
                       "message", "created_at", "source_page", "ip_address")
    fieldsets = (
        ("Enquiry", {"fields": ("name", "email", "phone", "organisation", "service_interest", "message")}),
        ("Follow-up", {"fields": ("status", "internal_notes")}),
        ("Metadata", {"classes": ("collapse",), "fields": ("created_at", "source_page", "ip_address")}),
    )
    actions = ("mark_contacted", "mark_closed", "export_csv")

    @admin.display(description="Email", ordering="email")
    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)

    @admin.action(description="Mark selected as contacted")
    def mark_contacted(self, request, queryset):
        updated = queryset.update(status=ContactSubmission.Status.CONTACTED)
        self.message_user(request, f"{updated} enquiry(ies) marked as contacted.")

    @admin.action(description="Mark selected as closed")
    def mark_closed(self, request, queryset):
        updated = queryset.update(status=ContactSubmission.Status.CLOSED)
        self.message_user(request, f"{updated} enquiry(ies) marked as closed.")

    @admin.action(description="Export selected to CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="enquiries.csv"'
        writer = csv.writer(response)
        writer.writerow(["Received", "Name", "Email", "Phone", "Company", "Interest", "Status", "Message"])
        for row in queryset:
            writer.writerow([
                row.created_at.strftime("%Y-%m-%d %H:%M"), row.name, row.email, row.phone,
                row.organisation, row.service_interest or "", row.get_status_display(), row.message,
            ])
        return response

    def has_add_permission(self, request):
        return False


class PublishedAdmin(admin.ModelAdmin):
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)


@admin.register(KeyFigure)
class KeyFigureAdmin(PublishedAdmin):
    list_display = ("value", "label", "order", "is_published")


@admin.register(Service)
class ServiceAdmin(PublishedAdmin):
    list_display = ("title", "icon", "is_featured", "order", "is_published")
    list_editable = ("is_featured", "order", "is_published")
    list_filter = ("is_featured", "is_published")
    search_fields = ("title", "summary", "intro")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Listing", {"fields": ("title", "slug", "summary", "icon", "is_featured")}),
        ("Detail page", {"fields": ("intro", "deliverables")}),
        ("Display", {"fields": ("order", "is_published")}),
    )


@admin.register(FirmValue)
class FirmValueAdmin(PublishedAdmin):
    list_display = ("name", "icon", "order", "is_published")
    search_fields = ("name", "description")


@admin.register(PresenceCity)
class PresenceCityAdmin(PublishedAdmin):
    list_display = ("name", "is_direct", "order", "is_published")
    list_filter = ("is_direct", "is_published")
    search_fields = ("name",)


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_on", "is_published")
    list_filter = ("category", "is_published", "published_on")
    search_fields = ("title", "excerpt", "body")
    date_hierarchy = "published_on"
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Note", {"fields": ("title", "slug", "category", "published_on", "excerpt")}),
        ("Body", {"fields": ("body",)}),
        ("Display", {"fields": ("is_published",)}),
    )


@admin.register(IndustrySegment)
class IndustrySegmentAdmin(PublishedAdmin):
    list_display = ("name", "order", "is_published")
    search_fields = ("name",)


@admin.register(Client)
class ClientAdmin(PublishedAdmin):
    list_display = ("name", "listing", "tier", "order", "is_published")
    list_filter = ("tier", "is_published")
    search_fields = ("name", "listing")


@admin.register(TeamMember)
class TeamMemberAdmin(PublishedAdmin):
    list_display = ("name", "designation", "experience_years", "is_lead", "order", "is_published")
    list_filter = ("is_lead", "is_published")
    search_fields = ("name", "focus", "bio")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Identity", {"fields": ("name", "slug", "designation", "focus", "experience_years",
                                 "location", "qualification", "email", "phone")}),
        ("Photo", {"fields": ("photo", "static_photo"),
                   "description": "Upload a square photo. If empty, the bundled image or initials are used."}),
        ("Profile", {"fields": ("bio", "key_skills", "sectors")}),
        ("Display", {"fields": ("is_lead", "order", "is_published")}),
    )


@admin.register(Office)
class OfficeAdmin(PublishedAdmin):
    list_display = ("city", "is_primary", "order", "is_published")
    list_filter = ("is_primary", "is_published")
