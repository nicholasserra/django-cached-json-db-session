"""
Cached json and base64 encoded database-backed sessions.
"""
import base64

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.backends.base import SessionBase
from django.core.exceptions import SuspiciousOperation
from django.core.cache import cache
from django.utils.simplejson import simplejson as json
from django.utils.crypto import constant_time_compare

KEY_PREFIX = "django.contrib.sessions.cached_json_db"

class SessionStore(DBStore):
    """
    Implements json encoded cached database backed sessions.
    """

    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)

    def load(self):
        data = cache.get(KEY_PREFIX + self.session_key, None)
        if data is None:
            data = super(SessionStore, self).load()
            cache.set(KEY_PREFIX + self.session_key, self.encode_cache(data), 
                      settings.SESSION_COOKIE_AGE)
        else:
            data = self.decode_cache(data)
        return data

    def exists(self, session_key):
        return super(SessionStore, self).exists(session_key)

    def save(self, must_create=False):
        super(SessionStore, self).save(must_create)
        cache.set(KEY_PREFIX + self.session_key, self.encode_cache(self._session), 
                  settings.SESSION_COOKIE_AGE)

    def delete(self, session_key=None):
        super(SessionStore, self).delete(session_key)
        cache.delete(KEY_PREFIX + (session_key or self.session_key))

    def flush(self):
        """
        Removes the current session data from the database and regenerates the
        key.
        """
        self.clear()
        self.delete(self.session_key)
        self.create()

    def encode_cache(self, session_dict):
        try:
             return json.dumps(session_dict).encode('zlib')
        except TypeError: 
            raise

    def decode_cache(self, session_data):
        try:
            return json.loads(session_data.decode('zlib'))
        except json.decoder.JSONDecodeError:
            raise ValueError

def encode(self, session_dict):
    try:
        encoded = json.dumps(session_dict).encode('zlib')
    except TypeError: 
        raise
    hash = self._hash(encoded)
    return base64.encodestring(hash + ":" + encoded)

def decode(self, session_data):
    encoded_data = base64.decodestring(session_data)
    try:
        # could produce ValueError if there is no ':'
        hash, jsond = encoded_data.split(':', 1)
        expected_hash = self._hash(jsond)
        if not constant_time_compare(hash, expected_hash):
            raise SuspiciousOperation("Session data corrupted")
        else:
            try:
                return json.loads(jsond.decode('zlib'))
            except json.decoder.JSONDecodeError:
                raise ValueError
    except Exception:
        return {}

SessionBase.encode = encode
SessionBase.decode = decode
