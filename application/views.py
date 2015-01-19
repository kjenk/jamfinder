from application import app
from flask.views import MethodView
from utils import (get_concert_songs,
                   get_zipcode_from_latlng,
                   get_zipcode_from_address)
from datetime import timedelta, date
import settings, random, os
from flask import (Blueprint, request, redirect,
                   render_template, url_for, make_response)
import json, re
from flask import Markup

@app.route('/')
@app.route('/index/')
def index():
    print "concerts"
    #concerts = get_concert_songs(settings.DEFAULT_ZIPCODE)
    #print len(concerts)
    return render_template('index.html', google_maps_api_key = settings.GOOGLE_MAPS_API_KEY)

class UpdateView(MethodView):
    current_zipcode = settings.DEFAULT_ZIPCODE

    def get(self):
        radius = int(request.args.get('radius', 50))
        date_option = int(request.args.get('date', 7))
        end_date = date.today() + timedelta(days=date_option)
        addr = request.args.get('address', None)
        lat = request.args.get('lat', None)
        lng = request.args.get('lng', None)
        if not addr and not lat and not lng:
            zipcode = current_zipcode
        if not addr or not re.match(r'\d{5}', addr):
            if lat and lng:
                zipcode = get_zipcode_from_latlng(float(lat), float(lng))
            else:
                zipcode = get_zipcode_from_address(addr)
        else:
            zipcode = int(addr)
        concerts = get_concert_songs(zipcode, radius = radius,
                                     end_date = end_date)
        current_zipcode = zipcode
        response= make_response(concerts)
        response.content_type = 'application/json'
        return response

app.add_url_rule('/update', view_func=UpdateView.as_view('update'))
