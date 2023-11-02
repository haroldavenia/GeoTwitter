import collections.abc
from shapely.geometry import box, MultiPoint, Point
from geopy.geocoders import Nominatim
import spacy
from src.services.ClusteringDBSCAN import ClusteringDBSCAN

ALLOW_PLACE_TYPE = ['poi', 'city', 'neighborhood', 'admin']
ALLOW_PLACE_CLASS = ['boundary', 'place']


class Locate:

    def __init__(self, log):
        self.sp = spacy.load("en_core_web_sm")
        self.GEOLOCATOR = Nominatim(user_agent="smy-application")
        self._log = log

    def get_city_country(self, long, lat):
        try:
            place = self.GEOLOCATOR.reverse((lat, long), exactly_one=True, language='en')
            city = place.raw['address'].get('city', '')
            state = place.raw['address'].get('state', '')
            country = place.raw['address'].get('country', '')
            return city, state, country
        except Exception as e:
            print(f"Error while retrieving city and country: {e}")
            return None, None

    # get coordinates
    def _extract_coord(self, geom):
        data = None
        try:
            if hasattr(geom, 'point'):
                geom = Point(geom.longitude, geom.latitude)
                data = {'x': geom.x, 'y': geom.y}
            elif hasattr(geom, 'geom_type') and geom.geom_type == "Point":
                data = {'x': geom.x, 'y': geom.y}
            elif isinstance(geom, collections.abc.Sequence) and len(geom) == 2:
                geom = Point(geom)
                data = {'x': geom.x, 'y': geom.y}
        except Exception as error:
            print(error)
            print("couldn't assign point")

        return data

    def points_centroid(self, points):
        location = None
        if len(points) > 1:
            locations = [(obj["x"], obj["y"]) for obj in points]
            points = MultiPoint(locations)
            location = {'x': points.representative_point().x, 'y': points.representative_point().y}
        elif len(points) == 1:
            location = points[0]
        return location

    def NER_locate(self, text):
        doc = self.sp(text)
        GPE = []
        LOC = []
        for entidad in doc.ents:
            if entidad.label_ == "LOC":
                LOC.append(entidad.text)
            elif entidad.label_ == "GPE":
                GPE.append(entidad.text)

        locations = [f'{loc}, {gpe}' for loc, gpe in zip(LOC, GPE)]
        locations = locations + GPE + LOC
        points = []
        for loc in locations:
            coord = self.get_coord({'user_loc': loc})
            points.append(coord) if coord else None

        if len(points) > 0:
            return self.cluster_dense_centroid(points)
        else:
            return None

    def _place_locate(self, place):
        xy = self.GEOLOCATOR.geocode(u'' + place, timeout=60)
        if xy and xy != "" and xy.raw.get('class') in ALLOW_PLACE_CLASS:
            return self._extract_coord(xy)
        else:
            return None

    def _poitn_array_locate(self, points):
        points = MultiPoint(points)
        return self._extract_coord(points.centroid)

    def _bbox_locate(self, bbox):
        geom = box(*bbox, ccw=True)
        return self._extract_coord(geom.centroid)

    def cluster_dense_centroid(self, points):
        location = None
        cluster_DBSACN = ClusteringDBSCAN()
        coords = cluster_DBSACN.centroid_most_dense(points)
        if coords:
            location = self.points_centroid(coords)
        return location

    def get_coord(self, data):
        data_loc = None
        if data.get('coordinates', None):
            xy = data.get('coordinates')
            data_loc = self._extract_coord(xy)
        elif data.get('place'):
            place = data.get('place')
            if place.get('geo', None) and place.get('geo').get('coordinates', None):
                xy = data.get('geo').get('coordinates')
                data_loc = self._extract_coord(xy)
            elif place.get('bounding_box', None) and place.get('place_type') in ALLOW_PLACE_TYPE:
                bbox = place.get('bounding_box').get("coordinates")
                data_loc = self._poitn_array_locate(bbox)
            elif place.get('geo', None) and place.get('geo').get('bbox', None) and place.get(
                    'place_type') in ALLOW_PLACE_TYPE:
                bbox = place.get('geo').get('bbox')
                data_loc = self._bbox_locate(bbox)
            elif place.get('place_type') in ALLOW_PLACE_TYPE:
                full_name, country = place
                data_loc = self._place_locate("%s, %s" % (full_name, country))
        elif data.get('user_loc', None) and data.get('user_loc'):
            data_loc = self._place_locate(data.get('user_loc'))
        elif data.get('friend_loc', None) and data.get('friend_loc'):
            data_loc = self._place_locate(data.get('friend_loc'))
        elif data.get('text_loc', None) and data.get('text_loc'):
            data_loc = self.NER_locate(data.get('text_loc'))

        return data_loc
