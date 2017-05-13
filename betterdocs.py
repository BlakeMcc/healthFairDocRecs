#query betterdocs
import requests



def getDocs(**kwargs):
    params = {}
    for key, value in kwargs.items():
        params[key] = value

    apikey = '9d97e00ba65c3569f4510e5f607eea14'

    url = 'https://api.betterdoctor.com/2016-03-01/doctor'

    r = requests.get(url, params=params)

    return r.content



$.get(resource_url, function (data) {
    // data: { meta: {<metadata>}, data: {<array[Practice]>} }
    var template = Handlebars.compile(document.getElementById('docs-template').innerHTML);
    document.getElementById('content-placeholder').innerHTML = template(data);
});