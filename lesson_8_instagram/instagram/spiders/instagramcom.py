# -*- coding: utf-8 -*-
import scrapy
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from instagram.items import InstagramItem

class InstagramcomSpider(scrapy.Spider):
    name = 'instagramcom'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    insta_login = 'rgeekmca'
    insta_pass = '#PWD_INSTAGRAM_BROWSER:10:1591357205:AeZQAABkUYvOAQ99OxiRScG5iZdt0z5KdNcvitL6qr79UOF1XnnXIYJMLuERGRxhKHmeUaJA7p9IRPklKGm6QL8quV6lVe+FX7vqGiNCegZ8wWDHpyWyCwNTm18sVPXCZYueRIbDZayMLqhg'
    parser_user = 'rkl.shows'
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    hash_followers = 'c76146de99bb02f6415203be841dd25a'
    graphql_link = 'https://www.instagram.com/graphql/query/?'

    def parse(self, response):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_login_link,
            method='POST',
            callback=self.parse_user,
            formdata={
                'username': self.insta_login,
                'enc_password': self.insta_pass
            },
            headers={'X-CSRFToken': csrf_token}
        )

        pass

    def parse_user(self, response):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            yield response.follow(
                f'/{self.parser_user}',
                callback=self.user_data_parse
            )

    def user_data_parse(self, response):
        user_id = self.fetch_user_id(response.text, self.parser_user)
        variables = {"id": user_id,
                     "first": 12
                     }
        url_followers = f'{self.graphql_link}query_hash={self.hash_followers}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.followers_parse,
            cb_kwargs={'user_id': user_id,
                       'variables': deepcopy(variables)
                       }
        )


    def followers_parse(self, response, user_id, variables):
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url_followers = f'{self.graphql_link}query_hash={self.hash_followers}&{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        followers = j_body.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers:
            item = InstagramItem(
                followers_of=user_id,
                id=follower['node']['id'],
                username=follower['node']['username'],
                fullname=follower['node']['full_name']
            )

            yield item


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')