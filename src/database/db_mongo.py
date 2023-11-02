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
from dotenv import load_dotenv
from mongoengine import connect

load_dotenv('.env')


def init_mongo_bd():
    # Configuración de la base de datos MongoDB
    mongo_dbname = os.getenv('MONGO_DBNAME')
    mongo_uri = os.getenv('MONGO_URI')
    mongo_uri = f'mongodb://{mongo_uri}/{mongo_dbname}'

    # Configuración de la conexión a MongoDB
    connect(db=mongo_dbname, host=mongo_uri, alias=os.getenv('MONGO_ALIAS'))
