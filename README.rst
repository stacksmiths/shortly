shortly
=======

FastAPI-powered URL shortener for quick, reliable links.

---

Features
--------

- **URL Shortening**: Generate short, reliable links for any URL.
- **Redirection**: Retrieve the original URL from the short ID.
- **Analytics**: Track the number of clicks for each short URL.
- **Health Checks**: Simplified and detailed health endpoints for monitoring.
- **QR Code Generation**: Create QR codes for shortened URLs.

---

Installation
------------

Install the package from PyPI:

.. code-block:: bash

   pip install shortly

---

Usage
-----

Import and Use in Your Application:

.. code-block:: python

   from shortly import shorten_url, get_original_url, get_click_count

# Shorten a URL

   short_id = shorten_url("<https://example.com>")
   print(f"Shortened URL ID: {short_id}")

# Retrieve the original URL

   original_url = get_original_url(short_id)
   print(f"Original URL: {original_url}")

# Get click count for a short URL

   click_count = get_click_count(short_id)
   print(f"Click count: {click_count}")

---

API Endpoints
-------------

**Health Check**

- **Simplified Health**: ``GET /health``
  - Returns the overall status: ``{"status": "healthy"}`` or ``{"status": "unhealthy"}``.

- **Detailed Health**: ``GET /health/status``
  - Returns uptime and component statuses:

    .. code-block:: json

       {
         "status": "healthy",
         "uptime": "0:15:22.345678",
         "components": {
           "routes": "up"
         }
       }

**URL Shortening**

- **Shorten URL**: ``POST /shorten``
  - Request:

    .. code-block:: json

       {
         "url": "<https://example.com>"
       }

  - Response:

    .. code-block:: json

       {
         "short_url": "/a1b2c3"
       }

- **Redirect to Original URL**: ``GET /{short_id}``
  - Redirects to the original URL or returns ``404``.

**Analytics**

- **Click Analytics**: ``GET /{short_id}/analytics``
  - Response:

    .. code-block:: json

       {
         "short_id": "a1b2c3",
         "click_count": 42
       }

**QR Code Generation**

- **Generate QR Code**: ``GET /{short_id}/qr``
  - Returns a PNG QR code for the short URL.

---

License
-------

This project is licensed under the MIT License.
