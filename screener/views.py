import json
import logging

from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import View, TemplateView

from screener.models import *

logger = logging.getLogger('screener')

# TODO: Implement querying APIs
# params is a dict of the parameters to pass the API
# should return a dict for rendering as JSON or context dict in template
def query_providers(params):
    return None

# TODO: Implement querying provider APIs for detail info, Vital Signs, etc.
def query_provider_detail(npi):
    return None


class HomeView(TemplateView):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    # Submits params to APIs, creates Screen objects with those params, redirects
    def post(self, request, *args, **kwargs):
        post_args = request.POST.dict()
        if not 'params' in post_args:
            return render(
                request,
                self.template_name,
                {'message': 'Must include search terms for providers'}
            )
        params = post_args.get('params')
        screen_obj = Screen.objects.create(
            slug=Screen.make_slug(),
            params=params,
            phone=post_args.get('phone'),
            email=post_args.get('email')
        )

        return HttpResponseRedirect(
            reverse('screen',
            kwargs={'slug': screen_obj.slug})
        )


class ScreenView(TemplateView):
    template_name = 'screener.html'

    def dispatch(self, request, *args, **kwargs):
        return super(ScreenView, self).dispatch(request, *args, **kwargs)

    # Renders template based on pre-created slug
    def get(self, request, *args, **kwargs):
        screen_obj = Screen.objects.filter(slug=kwargs['slug'])
        if screen_obj is None:
            return HttpResponseBadRequest()

        provider_info = query_providers(screen_obj.params)
        return render(request, self.template_name, provider_info)

    # Updates the Screen object with new saved params
    def put(self, request, *args, **kwargs):
        put_args = request.PUT.dict()
        if not 'params' in put_args:
            return HttpResponseBadRequest()

        screen_obj = Screen.objects.filter(slug=kwargs['slug'])
        if screen_obj is None:
            return JsonResponse({'message': 'not found'})
        screen_obj.params = put_args['params']
        screen_obj.save()

        return JsonResponse({
            'id': screen_obj.id,
            'slug': screen_obj.slug,
            'params': screen_obj.params
        })

    # Submits params to APIs, returns results
    def post(self, request, *args, **kwargs):
        post_args = request.POST.dict()
        if not 'params' in post_args:
            return HttpResponseBadRequest()
        params = post_args.get('params')
        providers = query_providers(params)

        if request.GET.get('format') == 'json':
            return JsonResponse(providers)
        return render(request, self.template_name, providers)


class ProviderDetailView(TemplateView):
    template_name = 'detail.html'

    def dispatch(self, request, *args, **kwargs):
        return super(ProviderDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProviderDetailView, self).get_context_data(**kwargs)
        context['npi'] = kwargs['npi']
        # TODO: Pull other information from multiple APIs
        context.update(query_provider_detail(context['npi']))
        return context
