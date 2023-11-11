# - * - coding: UTF - 8 -*-
# -------------------------------------------------------------------------------
# Name:        	Gazetter V3.0
# Purpose:		Aproximador de sitios de interes Colombia
#
# Author:      	Harold Avenia - Esri Colombia.
#
# Created:     	14/06/2017
# Last Edition: 13/10/2017
# Copyright:   	(c) Esri Colombia 2017
# Licence:    	Arcpy
# -------------------------------------------------------------------------------
"""---------------------------Import Libraries --------------------------------"""
from flask_restx import Resource, fields
# local modules
from src.services.ExtractLocation import ExtractLocation
from src.utils.Log import Log
from src.services.TwitterConnection import TwitterConnection
from src.services.SentAnalysis import SentAnalysis
from src.database.Repository import Repository
from src.config import AppConfig

log = Log()
# Get the application instance
appConfig = AppConfig()
api = appConfig.get_api()

twitter_conn = TwitterConnection()

# Define un modelo para el objeto JSON 'bbox-filter'
bbox_filter_model = api.model('BoundingBoxFilter', {
    'min_lat': fields.Float(required=True, description='Minimum Latitude'),
    'max_lat': fields.Float(required=True, description='Maximum Latitude'),
    'min_lon': fields.Float(required=True, description='Minimum Longitude'),
    'max_lon': fields.Float(required=True, description='Maximum Longitude')
})

# Define el modelo para los parámetros de la solicitud GET
search_post_req = api.model('twitter', {
    'client_id': fields.String(required=True, description='Tenant ID'),
    'tag_filter': fields.String(required=True, description='Tag filter'),
    'filter_comm-cmd': fields.String(required=True, description='Command filter'),
    'bbox-filter': fields.Nested(bbox_filter_model, required=False, description='Bounding Box')
})


@api.route('/health', methods=['GET'])
@api.response(404, 'Search not found.')
class HealthCheck(Resource):
    def get(self):
        return {"status": "OK"}


#  Create a RESTful resource
@api.route('/search', methods=['POST'])
@api.response(404, 'Search not found.')
class InputSearch(Resource):

    @api.expect(search_post_req)
    @api.response(201, 'Geo_twitter search successfully completed.')
    def post(self):
        """
        This function creates a new person in the people structure
        based on the passed in person data

        :param search_post_req:  person to create in people structure
        :return:        201 on success, 406 on person exists
        """
        try:
            options = {
                'client_id': api.payload['client_id'],
                'bbox_filter': api.payload.get('bbox-filter', None),
                'tag_filter': api.payload['tag_filter'],
            }
            # observer = TwitterObserver()
            # twitter_conn.add_observer(observer)
            # self._twitter_conn.listener(api.payload['filter_comm-cmd'], options)
            df_tweets = twitter_conn.search_recent(api.payload['filter_comm-cmd'])
            sentiment = SentAnalysis()
            db_repo = Repository()
            twitters = []
            tweets = df_tweets.to_dict(orient='records')
            for tweet in tweets:
                extract_loc = ExtractLocation(tweet, twitter_conn, log)
                extract_loc.extract()
                data_loc = extract_loc.get_location()
                if data_loc:
                    data = sentiment.sentiment_fit({**tweet, **data_loc}, "text")
                    twitters.append(data)
            if twitters:
                response_data = db_repo.save_db(twitters, options)
                return response_data, 201
            else:
                return {"message": "No data found."}, 204
        except Exception as ex:
            return str(ex), 500
