import os

from cmt.framework import set_services

path_to_services = os.path.join(os.path.dirname(__file__), '..', '..',
                                'testing')
set_services('services', path=[path_to_services, ])
