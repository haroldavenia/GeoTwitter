# -*- coding: UTF-8 -*-
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
import os
import connexion
from dotenv import load_dotenv
from flask_restx import Api
from flask_marshmallow import Marshmallow


class AppConfig:
    _instance = None
    _api = None
    _ma = None
    _app = None
    _connex_app = None

    def __new__(cls, env=None):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance.init_config(env)
        return cls._instance

    def init_config(self, env):
        # Configurar la aplicación Connexion
        basedir = os.path.abspath(os.path.dirname(__file__))
        baseDirParent = os.path.abspath(os.path.join(basedir, os.pardir))
        load_dotenv(os.path.join(baseDirParent, env)) if env else load_dotenv()
        self._connex_app = connexion.App(__name__, specification_dir=basedir)

        # Configurar la aplicación Flask
        self._app = self._connex_app.app
        self._app.config['JSON_AS_ASCII'] = os.getenv('JSON_AS_ASCII')

        # Inicializar Marshmallow
        self._ma = Marshmallow(self._app)
        self._api = Api(self._app)
        pass

    def get_app(self):
        return self._app

    def get_connex_app(self):
        return self._connex_app

    def get_marshmallow(self):
        return self._ma

    def get_api(self):
        return self._api
