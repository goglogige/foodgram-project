from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'flatpages/author.html'


class AboutTechView(TemplateView):
    template_name = 'flatpages/tech.html'