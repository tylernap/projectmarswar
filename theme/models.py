from django.conf import settings
from django.db import models
from django.utils.datastructures import OrderedSet
from django.utils.translation import gettext_lazy as _

from cms.models import CMSPlugin


SIZE_CHOICES = getattr(
    settings,
    'DJANGOCMS_TAILWIND_BUTTON_SIZES',
    ["normal", "text-xl", "text-2xl", "text-5xl"]
)
SIZE_CHOICES = tuple((entry, entry) for entry in SIZE_CHOICES)

class TailwindButton(CMSPlugin):
    label = models.CharField(
        verbose_name=_("Label"),
        blank=True,
        max_length=255,
        help_text=_("The text displayed inside the button")
    )
    link = models.CharField(
        verbose_name=_("Link"),
        blank=True,
        max_length=1000,
        help_text=_("The URL that the button points to")
    )
    size = models.CharField(
        verbose_name=_("Size"),
        choices=SIZE_CHOICES,
        default=SIZE_CHOICES[0][0],
        max_length=255,
        help_text=_("The size of the text in the button")
    )

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
        on_delete=models.CASCADE,
    )