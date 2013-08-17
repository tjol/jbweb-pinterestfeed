Pinterest RSS Feeds
===================

This Django app produces RSS feeds for Pinterest users and pinboards
with full-sized images. The standard Pinterest RSS feeds only give you
tiny images, so this is meant to be an improvement.

Most of the work is moved to the background using *Celery*. Running your
Celery worker with *eventlet* concurrency enabled in recommended.

Copyright
---------

Copyright © 2013 Thomas Jollans

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

For details, see `COPYING`
