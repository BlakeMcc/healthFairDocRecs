import json
import logging
from geopy.geocoders import Nominatim
import requests

from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.db.models import F
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


def zip_to_lat_lon(zip_code):
    geolocator = Nominatim()
    location = geolocator.geocode(zip_code)
    return '{},{},25'.format(location.latitude, location.longitude)


def get_docs(**kwargs):
    better_docs_params = {}

    for key, value in kwargs.items():
        better_docs_params[key] = value

    better_docs_params['user_key'] = settings.BETTER_DOCTOR_API_KEY
    better_docs_params['location'] = zip_to_lat_lon(better_docs_params['zip_code'])
    better_docs_params.pop('zip_code')

    r = requests.get(settings.BETTER_DOCTOR_URL, params=better_docs_params)
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
    params['skip']=skip
    json_data = get_docs(**params)
    doctor_dicts = []

    for doctor in json_data:
        practice_for_doc = get_best_practice(doctor['practices'])
        if len(practice_for_doc) > 0:
            practice_for_doc = practice_for_doc[0]
            d = {}
            d['full_name'] = doctor['profile']['first_name'] + ' ' + doctor['profile']['last_name']
            practice_location = practice_for_doc['visit_address']
            d['location'] = practice_location['street']+" "+practice_location['street2'] +'\n' +practice_location['city']+ ", "+practice_location['state'] + " " + practice_location['zip']
            d['phone'] = practice_for_doc['phones'][0]['number']
            d['npi'] = doctor['npi']
            doctor_dicts.append(d)

    return doctor_dicts

# TODO: Implement querying provider APIs for detail info, Vital Signs, etc.
def query_provider_detail(npi):
    params['skip']=skip
    json_data = get_docs(**params)
    doctor_dicts = []

    for doctor in json_data:
        practice_for_doc = get_best_practice(doctor['practices'])
        if len(practice_for_doc) > 0:
            practice_for_doc = practice_for_doc[0]
            d = {}
            d['full_name'] = doctor['profile']['first_name'] + ' ' + doctor['profile']['last_name']
            practice_location = practice_for_doc['visit_address']
            d['location'] = practice_location['street']+" "+practice_location['street2'] +'\n' +practice_location['city']+ ", "+practice_location['state'] + " " + practice_location['zip']
            d['phone'] = practice_for_doc['phones'][0]['number']
            d['npi'] = doctor['npi']
            d['education'] = doctor['education']
            d['specialties'] = doctor['specialties']
            d['hospital'] = doctor['hospital_affiliations']
            d['practice'] = practice_for_doc
            doctor_dicts.append(d)

    return doctor_dicts


# TODO: Pull insurance and specialty options
def get_api_options():
    return {
        'gender_options': [
            {'value': 'female', 'display': 'Female'},
            {'value': 'male', 'display': 'Male'},
            {'value': 'other', 'display': 'Other'}
        ],
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
        # Only update visits count if it's the first page
        if skip_val == 0:
            screen_obj.update(visits=F('visits')+1)

        provider_info = query_providers(
            screen_obj[0].params, skip=skip_val
        )
        response_dict = {'screen': screen_obj[0], 'providers': provider_info}
        if skip_val >= 10:
            response_dict['prev_skip'] = skip_val - 10
        response_dict['next_skip'] = skip_val + 10

        response_dict.update(get_api_options())
        return render(request, self.template_name, response_dict)

    def post(self, request, *args, **kwargs):
        post_args = request.POST.dict()
        params = parse_params(post_args)
        if len(params.keys()) == 0:
            return JsonResponse({'message': 'Must include search terms for providers'})
        screen_obj = Screen.objects.filter(slug=kwargs['slug'])
        if not len(screen_obj):
            return JsonResonse({'message': 'Not found'})

        screen_obj.update(
            params=params,
            phone=post_args.get('phone'),
            email=post_args.get('email')
        )
        provider_info = query_providers(params)
        response_dict = {'screen': screen_obj[0], 'providers': provider_info}
        response_dict['next_skip'] = 10

        response_dict.update(get_api_options())
        if request.GET.get('format') == 'json':
            return JsonResponse(providers)
        return render(request, self.template_name, response_dict)


class SendTextView(View):
    def dispatch(self, request, *args, **kwargs):
        return super(SendTextView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        screen_obj = Screen.objects.filter(slug=kwargs['slug'])
        if not len(screen_obj):
            return HttpResponseBadRequest()

        patient_number = screen_obj[0].phone
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        provider_info = query_providers(screen_obj[0].params)
        prettydoc = []
        for doc in provider_info:
            prettydoc.append('Name: ' + doc['full_name'] + '\n')
            prettydoc.append('Phone: ' + doc['phone'] + '\n')
            prettydoc.append('Office: ' + doc['location'] + '\n\n')

        textbody = ''.join(prettydoc)

        message = client.messages.create(
            to=patient_number,
            from_=settings.TWILIO_CALLER_ID,
            body= textbody + 'https://' + request.get_host() + reverse('screen', kwargs=kwargs)
        )
        return HttpResponseRedirect(reverse('screen', kwargs=kwargs))


class ProviderDetailView(TemplateView):
    template_name = 'detail.html'

    def dispatch(self, request, *args, **kwargs):
        return super(ProviderDetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        resp = requests.get(
            settings.VITAL_SIGNS_URL + kwargs['npi'],
            headers={'X-API-Key': settings.VITAL_SIGNS_API_KEY}
        )

        # return render(request, self.template_name, response.json())
        return JsonResponse(resp.json())


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        screens = Screen.objects.all().values()
        param_list = [
            dict(s['params'],
            **{'date': s['created_at'].strftime('%Y-%m-%d'),
            'visits': s['visits']}) for s in screens
        ]
        return render(request, self.template_name, {'param_list': param_list})
