#!/usr/bin/env python3
# encoding: utf-8
''' placeholder docstring

'''
from cortexutils.responder import Responder
import requests
import re
import json


class CreateCase(Responder):
    ''' placeholder docstring

    '''
    def __init__(self):
        Responder.__init__(self)
        self.url = self.get_param('config.url', None, 'SN url is missing')
        self.user = self.get_param('config.user', None, 'SN user is missing')
        self.pwd = self.get_param('config.password', None,
                                  'SN password missing')

    def operations(self, raw):
        return [
            (self.build_operation('AddTagToCase',
                                  tag='Responder:ServiceNow Case Created')),
            (self.build_operation(
                'AddTagToCase',
                tag=str(self.response.json()['result']['number']))),
        ]

    def run(self):
        Responder.run(self)
        tags = self.get_param('data.tags', None)
        for tag in tags:
            check_for_SN = re.match(r'^[\w]{9}:[\w]{10}\W[\w]{4}\W[\w]{7}',
                                    tag)
            if not check_for_SN:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                payload = {
                    "assignment_group": "<Your Assignment Group", #unique number tied to ServiceNow group to assign ticket to
                    "short_description": self.get_param('data.title', None),
                    "impact": "2",
                    "description": "Autocreated by The Hive SIRP\n\n",
                    "comments": 'https://<Your Hive Server>/index.html#!/case/' + #Adds comments to the ticket to help identify the api
                                self.get_param('data._routing') +
                                '/details',
                    "company": "<Your Company>", #Fill your company
                    "state": "6",
                    "u_corp_or_product": "1",
                    "u_category_corp_it": "<Your top category>", #category if applicable
                    "u_subcategory_corp_it": "<Your subcategory>", #subcategory if applicable
                    "assigned_to": self.get_param('data.owner') + #Assign to a user@yourcompany
                                '@<Your Company>.com',
		    "u_origin_point": "<Descriptor API>"
                }
                self.response = requests.post(
                    (self.url + '/api/now/table/incident'),
                    auth=(self.user, self.pwd),
                    headers=headers,
                    data=json.dumps(payload))
                if self.response.status_code == 200 or \
                        self.response.status_code == 201:
                    self.report({'message': json.loads(self.response.text)})
                else:
                    self.error(self.response.status_code)
            else:
                self.error('Case already exists')


if __name__ == '__main__':
    CreateCase().run()
