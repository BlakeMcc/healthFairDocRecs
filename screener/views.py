import json
import logging
import requests

from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import View, TemplateView

from twilio.rest import Client

from screener.models import *

logger = logging.getLogger('screener')

FORM_PARAMS = ['zip_code', 'insurance', 'specialty', 'gender']

def parse_params(param_dict):
    params = {}
    for p in FORM_PARAMS:
        if param_dict.get(p):
            params[p] = param_dict.get(p)
    return params


def zip_to_lat_lon(zip):
    return '41.883969,-87.6284144,100'


def get_docs(**kwargs):
    better_docs_params = {}

    for key, value in kwargs.items():
        better_docs_params[key] = value

    better_docs_params['user_key'] = settings.BETTER_DOCTOR_API_KEY
    better_docs_params['location'] = zip_to_lat_lon(better_docs_params['zip_code'])
    better_docs_params.pop('zip_code')

    url = 'https://api.betterdoctor.com/2016-03-01/doctors'
    r = requests.get(url, params=better_docs_params)
    return r.json()['data']


def get_best_practice(practices):
    bestpractice = []
    for practice in practices:
        if practice['within_search_area'] == False:
            continue
        if 'phones' in practice:
            if len(practice['phones']) == 0:
                continue
        if practice['accepts_new_patients'] == False:
            continue
        if len(bestpractice) == 0:
            bestpractice.append(practice)
            continue
        if practice['distance'] < bestpractice[0]['distance']:
            bestpractice[0] = practice
            continue
    return bestpractice


# params is a dict of the parameters to pass the API
# should return a list of providers for rendering as JSON or context dict in template
def query_providers(params, skip=0):
    json_data = get_docs(**params)
    doctor_dicts = []

    for doctor in json_data:
        practice_for_doc = get_best_practice(doctor['practices'])
        if len(practice_for_doc) > 0:
            practice_for_doc = practice_for_doc[0]
            d = {}
            d['full_name'] = doctor['profile']['first_name'] + ' ' + doctor['profile']['last_name']
            d['location'] = practice_for_doc['location_slug']
            d['phone'] = practice_for_doc['phones'][0]['number']
            doctor_dicts.append(d)

    return doctor_dicts

# TODO: Implement querying provider APIs for detail info, Vital Signs, etc.
def query_provider_detail(npi):
    return None

# TODO: Pull insurance and specialty options
def get_api_options():
    return {
        'specialty_options': [
            {'value': 'pcp', 'display': 'Primary Care Provider'},
            {'value': 'end', 'display': 'Endocrinologist'}
        ],
        'insurance_options': [
            {'value': 'medicaid', 'display': 'Medicaid'},
            {'value': 'aetna', 'display': 'Aetna'}
        ]
    }


class HomeView(TemplateView):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, get_api_options())

    # Submits params to APIs, creates Screen objects with those params, redirects
    def post(self, request, *args, **kwargs):
        post_args = request.POST.dict()
        params = parse_params(post_args)
        if len(params.keys()) == 0:
            return render(
                request,
                self.template_name,
                {'message': 'Must include search terms for providers'}
            )
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
        if not len(screen_obj):
            return HttpResponseBadRequest()

        skip_val = int(request.GET.get('skip', 0))
        provider_info = query_providers(
            screen_obj[0].params, skip=skip_val
        )
        response_dict = {'screen': screen_obj[0], 'providers': provider_info}
        if skip_val >= 10:
            response_dict['prev_skip'] = skip_val - 10
        response_dict['next_skip'] = skip_val + 10

        response_dict.update(get_api_options())
        return render(request, self.template_name, response_dict)

    # Updates the Screen object with new saved params
    def put(self, request, *args, **kwargs):
        put_args = request.POST.dict()
        params = parse_params(put_args)
        if len(params.keys()) == 0:
            return JsonResponse({'message': 'Must include search terms for providers'})

        screen_obj = Screen.objects.filter(slug=kwargs['slug'])
        if not len(screen_obj):
            return JsonResponse({'message': 'Not found'})

        screen_obj.update(
            params=params,
            phone=put_args.get('phone'),
            email=put_args.get('email')
        )
        return JsonResponse({
            'id': screen_obj.id,
            'slug': screen_obj.slug,
            'params': screen_obj.params
        })

    # Submits params to APIs, returns results
    def post(self, request, *args, **kwargs):
        post_args = request.POST.dict()
        params = parse_params(post_args)
        if len(params.keys()) == 0:
            return JsonResponse({'message': 'Must include search terms for providers'})

        providers = query_providers(params)
        if request.GET.get('format') == 'json':
            return JsonResponse(providers)
        return render(request, self.template_name, providers)


class SendTextView(View):
    def dispatch(self, request, *args, **kwargs):
        return super(SendTextView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # TODO: Implement sending text to email with URL, first results?
        screen_obj = Screen.objects.filter(slug=kwargs['slug'])
        if not len(screen_obj):
            return HttpResponseBadRequest()

        patient_number = screen_obj[0].phone
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            to=patient_number,
            from_=settings.TWILIO_CALLER_ID,
            body=reverse('screen', kwargs=kwargs)
        )

        return HttpResponseRedirect(reverse('screen', kwargs=kwargs))


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
