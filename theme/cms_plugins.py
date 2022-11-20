from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import gettext_lazy as _

from .models import TailwindButton


@plugin_pool.register_plugin
class TailwindButtonPlugin(CMSPluginBase):
    model = TailwindButton
    name = _("Tailwind Button")
    render_template = "plugins/button.html"

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        return context