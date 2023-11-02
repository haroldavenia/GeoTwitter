import json
from shapely import to_geojson, Point
from src.services.Locate import Locate


class TwitterExtractLocation(Exception):
    def __init__(self, message):
        super().__init__(message)


class ExtractLocation(object):
    def __init__(self, tweet, twitter_conn, log):
        self._tweet = tweet
        self._loc = Locate(log)
        self._coord = None
        self._accuracy = 0.0
        self.twitter_conn = twitter_conn
        self._log = log

    def extract(self):
        if not self._exec_func(self._exact_loc, 100.0):
            if not self._exec_func(self._geo_tagged, 70.0):
                if not self._exec_func(self._user_loc, 50.0):
                    if not self._exec_func(self._friends_loc, 40.0):
                        if not self._exec_func(self._text_loc, 30.0):
                            pass

    def _exec_func(self, func, acc):
        self._coord = func()
        if self._coord:
            self._accuracy = acc
            return True
        return False

    def _text_loc(self):
        location = None
        text = self._tweet.get('text', None)
        if text:
            location = self._loc.get_coord({'text_loc': text})
        return location

    def _exact_loc(self):
        location = None
        coord = self._tweet.get('coordinates', None)
        if coord:
            location = self._loc.get_coord({'coordinates': coord})
        else:
            coord = self._tweet.get('geo').get('coordinates', None) if self._tweet.get('geo', None) else None
            if coord:
                location = self._loc.get_coord({'coordinates': coord})
        return location

    def _geo_tagged(self):
        location = None
        if self._tweet.get('place', None):
            location = self._loc.get_coord({'place': self._tweet.get('place')})
        return location

    def _user_loc(self):
        location = None
        user_loc = self._tweet.get('user_loc', None)
        if user_loc:
            location = self._loc.get_coord({'user_loc': self._tweet.get('user_loc')})
            if not location:
                user_desc = self._tweet.get('user_desc', None)
                if user_desc:
                    location = self._loc.get_coord({'text_loc': user_desc})
        return location

    def _friends_loc(self):
        try:
            user_id = self._tweet.get('author_id')
            if user_id:
                friend_locations = self._get_friend_locations(user_id)
                location = self._calculate_location(friend_locations)
                return location
            return None
        except Exception as e:
            self._log.writeLogError(f"Error in _friends_loc: {str(e)}")
            return None

    def _get_friend_locations(self, user_id):
        friend_locations = []
        for friend in self.twitter_conn.get_friends(user_id):
            friend_loc = friend.get('location')
            if friend_loc:
                coord = self._loc.get_coord({'friend_loc': friend_loc})
                if coord:
                    friend_locations.append(coord)
        return friend_locations

    def _calculate_location(self, locations):
        if len(locations) == 1:
            return locations[0]
        elif len(locations) > 1:
            return self._loc.points_centroid(locations)
        return None

    def get_location(self):
        if self._coord:
            city, state, country = self._loc.get_city_country(self._coord.get('x'), self._coord.get('y'))
            x = self._coord.get('x')
            y = self._coord.get('y')
            lonlat = "%s, %s" % (x, y)
            latlon = "%s, %s" % (y, x)
            geojson_dict = json.loads(to_geojson(Point(x, y)))
            return {'x': x, 'y': y, 'lonlat': lonlat, 'latlon': latlon, "geometry": geojson_dict,
                    'city': city, 'state': state, 'country': country, 'accuracy': self._accuracy}
        else:
            return None
