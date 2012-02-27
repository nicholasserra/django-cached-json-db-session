#Overview
__This session backend is experimental!__

A JSON encoded cached db session backend for Django. Uses compressed JSON instead of pickling, easier to access in Node, etc. Still falls back to DB on a miss, but the DB encode and decode is duck punched to also use JSON and zlib.

#Usage
In settings.py:

```python
SESSION_ENGINE = 'cached_json_db'
```