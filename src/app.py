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
from src.routes.SearchTwitter import *
from src.database.db_mongo import init_mongo_bd
from src.config import AppConfig

init_mongo_bd()
appConfig = AppConfig()
app = appConfig.get_app()

# If we're running in stand-alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
