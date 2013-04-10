#!/usr/bin/env python
import os
import sys
# import my_cron

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssg_site.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

# def fetch_rss():
#     return my_cron.fetch_rss_feeds()