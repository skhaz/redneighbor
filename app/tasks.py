# -*- coding: utf-8 -*-
import logging
import os
import cloudstorage as gcs

from datetime import datetime
from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.ext import deferred

from jinja2 import Environment
from google.appengine.api import app_identity

from app.models import Nude


def build():
    # TODO enviar url_for, domain, etc.

    jinja_env = Environment()
    jinja_env.globals['domain'] = 'https://mandanudes.ae'
    sitemap_template = jinja_env.from_string(
        """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
          {% for result in results -%}
          <url>
            <loc>{{ domain }}/nude/{{ result.key.urlsafe() }}</loc>
            <lastmod>{{ date.strftime('%Y-%m-%d') }}</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.8</priority>
          </url>
          {% endfor %}
        </urlset>""")

    sitemaps = []
    bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())

    retry_params = gcs.RetryParams(backoff_factor=1.1)
    query = Nude.query(Nude.public == True)
    more = True
    cursor = None
    while more:
        results, cursor, more = query.fetch_page(1000, start_cursor=cursor)
        filename = 'sitemap_%02d.xml' % 1
        gcs_file = gcs.open(
            '/%s/static/%s' % (bucket_name, filename),
            'w',
            content_type='text/xml',
            retry_params=retry_params)
        content = sitemap_template.render(results=results, date=datetime.utcnow())
        gcs_file.write(content.encode('utf-8'))
        gcs_file.close()
        sitemaps.append(filename)

    robots_txt = jinja_env.from_string(
        """User-agent: *
        Allow: /
        {% for sitemap in sitemaps -%}
        Sitemap: {{ domain }}/{{ sitemap }}
        {% endfor %}""").render(sitemaps=sitemaps)

    gcs_file = gcs.open(
        '/%s/static/robots.txt' % bucket_name,
        'w',
        content_type='text/plain',
        retry_params=retry_params)
    gcs_file.write(robots_txt.encode('utf-8'))
    gcs_file.close()
