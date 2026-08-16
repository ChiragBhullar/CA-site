from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Ordered(models.Model):
    """Shared ordering + published flag for all content models."""

    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")
    is_published = models.BooleanField(default=True, help_text="Untick to hide from the site without deleting.")

    class Meta:
        abstract = True
        ordering = ["order", "pk"]


class KeyFigure(Ordered):
    """Short numeric facts, e.g. '2019 - Year the firm was incorporated'."""

    value = models.CharField(max_length=24, help_text="e.g. '20+', '2019', '9'")
    label = models.CharField(max_length=80, help_text="e.g. 'Professionals across the practice'")

    class Meta(Ordered.Meta):
        verbose_name = "key figure"

    def __str__(self):
        return f"{self.value} - {self.label}"


class Service(Ordered):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    summary = models.CharField(max_length=300, help_text="One line shown in listings.")
    intro = models.TextField(blank=True, help_text="Opening paragraphs on the service page. Separate with a blank line.")
    deliverables = models.TextField(blank=True, help_text="One deliverable per line.")
    icon = models.CharField(
        max_length=24, default="audit",
        choices=[("audit", "Audit"), ("tax", "Tax"), ("risk", "Risk"), ("governance", "Governance"),
                 ("finance", "Corporate finance"), ("outsourcing", "Outsourcing"),
                 ("analytics", "Analytics"), ("digital", "Digital")],
        help_text="Line icon shown on the service card.",
    )
    is_featured = models.BooleanField(default=False, help_text="Show on the home page.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:140]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("profile_site:service_detail", args=[self.slug])

    def __str__(self):
        return self.title

    @property
    def intro_paragraphs(self):
        return [p.strip() for p in self.intro.split("\n\n") if p.strip()]

    @property
    def deliverable_list(self):
        return [line.strip() for line in self.deliverables.splitlines() if line.strip()]


class IndustrySegment(Ordered):
    name = models.CharField(max_length=80)

    class Meta(Ordered.Meta):
        verbose_name = "industry segment"

    def __str__(self):
        return self.name


class PresenceCity(Ordered):
    name = models.CharField(max_length=80)
    is_direct = models.BooleanField(default=True, help_text="Untick if covered through associates.")

    class Meta(Ordered.Meta):
        verbose_name = "presence city"
        verbose_name_plural = "presence cities"

    def __str__(self):
        return self.name


class Client(Ordered):
    class Tier(models.TextChoices):
        MAJOR = "major", "Major engagement"
        OTHER = "other", "Other client"

    name = models.CharField(max_length=160)
    listing = models.CharField(
        max_length=80, blank=True, help_text="Exchange listing or note, e.g. 'BSE, NSE listed'."
    )
    tier = models.CharField(max_length=8, choices=Tier.choices, default=Tier.OTHER)

    class Meta(Ordered.Meta):
        ordering = ["tier", "order", "name"]

    def __str__(self):
        return self.name


class TeamMember(Ordered):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    designation = models.CharField(max_length=120, help_text="e.g. 'Partner'")
    focus = models.CharField(max_length=200, help_text="Practice areas.")
    experience_years = models.PositiveSmallIntegerField(null=True, blank=True)
    location = models.CharField(max_length=80, blank=True)
    bio = models.TextField(help_text="Two or three short paragraphs. Separate with a blank line.")
    key_skills = models.TextField(blank=True, help_text="One skill per line.")
    sectors = models.TextField(blank=True, help_text="One sector per line.")
    qualification = models.CharField(max_length=240, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    photo = models.ImageField(upload_to="team/", blank=True, help_text="Square image, at least 600x600.")
    static_photo = models.CharField(
        max_length=200, blank=True,
        help_text="Bundled fallback image, e.g. 'site/img/team/anuj-kumar.jpg'.",
    )
    is_lead = models.BooleanField(default=False, help_text="Feature this person first.")

    class Meta(Ordered.Meta):
        ordering = ["-is_lead", "order", "pk"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("profile_site:team_detail", args=[self.slug])

    def __str__(self):
        return self.name

    @property
    def initials(self):
        parts = [p for p in self.name.replace("CA ", "").split() if p]
        return "".join(p[0] for p in parts[:2]).upper()

    @property
    def skill_list(self):
        return [line.strip() for line in self.key_skills.splitlines() if line.strip()]

    @property
    def sector_list(self):
        return [line.strip() for line in self.sectors.splitlines() if line.strip()]

    @property
    def bio_paragraphs(self):
        return [p.strip() for p in self.bio.split("\n\n") if p.strip()]


class Office(Ordered):
    city = models.CharField(max_length=80)
    address = models.TextField(help_text="Street address. Line breaks are preserved.")
    is_primary = models.BooleanField(default=False)

    class Meta(Ordered.Meta):
        ordering = ["-is_primary", "order", "city"]

    def __str__(self):
        return self.city


class ContactSubmission(models.Model):
    """Every enquiry from the website form. Reviewed in the admin."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CONVERTED = "converted", "Converted"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    organisation = models.CharField(max_length=160, blank=True)
    service_interest = models.ForeignKey(
        Service, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="enquiries", verbose_name="service of interest",
    )
    message = models.TextField()

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW, db_index=True)
    internal_notes = models.TextField(blank=True, help_text="Not shown on the website.")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    source_page = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "contact enquiry"
        verbose_name_plural = "contact enquiries"

    def __str__(self):
        return f"{self.name} - {self.created_at:%d %b %Y}"


class FirmValue(Ordered):
    """The values row on the home and about pages."""

    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True)
    icon = models.CharField(
        max_length=24, default="quality",
        choices=[("quality", "Quality"), ("reliability", "Reliability"), ("response", "Responsiveness"),
                 ("governance", "Governance"), ("people", "Our people"), ("partnership", "Partnership")],
    )

    class Meta(Ordered.Meta):
        verbose_name = "firm value"

    def __str__(self):
        return self.name


class Insight(models.Model):
    """Short updates and notes. Optional - the section hides itself when empty."""

    class Category(models.TextChoices):
        DIRECT_TAX = "direct-tax", "Direct Tax"
        INDIRECT_TAX = "indirect-tax", "GST & Indirect Tax"
        AUDIT = "audit", "Audit & Assurance"
        REGULATORY = "regulatory", "Regulatory"
        ADVISORY = "advisory", "Advisory"
        FIRM = "firm", "Firm News"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.FIRM)
    published_on = models.DateField(help_text="Date shown on the card.")
    excerpt = models.CharField(max_length=300, help_text="One or two lines shown in listings.")
    body = models.TextField(help_text="Full note. Separate paragraphs with a blank line.")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_on", "-pk"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("profile_site:insight_detail", args=[self.slug])

    def __str__(self):
        return self.title

    @property
    def body_paragraphs(self):
        return [p.strip() for p in self.body.split("\n\n") if p.strip()]
