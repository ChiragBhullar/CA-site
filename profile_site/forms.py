from django import forms

from .models import ContactSubmission, Service


class ContactForm(forms.ModelForm):
    """Enquiry form. `website` is a honeypot: real people never see or fill it."""

    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off", "aria-hidden": "true"}),
        label="Leave this field empty",
    )

    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "phone", "organisation", "service_interest", "message"]
        labels = {
            "organisation": "Company",
            "service_interest": "What do you need help with?",
            "message": "Your message",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Full name", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@company.com", "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"placeholder": "Optional", "autocomplete": "tel"}),
            "organisation": forms.TextInput(attrs={"placeholder": "Optional"}),
            "message": forms.Textarea(
                attrs={"rows": 5, "placeholder": "A short note on your requirement and timeline."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_interest"].queryset = Service.objects.filter(is_published=True)
        self.fields["service_interest"].empty_label = "Not sure yet"
        self.fields["service_interest"].required = False
        self.fields["phone"].required = False
        self.fields["organisation"].required = False

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("This enquiry could not be sent.")
        return ""

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 15:
            raise forms.ValidationError("Add a little more detail so we can route your enquiry to the right partner.")
        return message
