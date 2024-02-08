from pprint import pprint
from urllib.parse import urlencode
import requests
import json


Token = ''
ya_token = ''
user_id = ''


def get_token_url():
    APP_ID = '51844282'
    OAUTH_BASE_URL = 'https://oauth.vk.com/authorize'
    redirect_uri = 'https://example.com/callback'
    params = {
        'client_id': APP_ID,
        'redirect_uri': redirect_uri,
        'display': 'page',
        'scope': 'friends,photos',
        'response_type': 'token'
    }
    return f'{OAUTH_BASE_URL}?{urlencode(params)}&v=5.131&state=123456'


class VK_api:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id1, ya_token1):
        self.token = token
        self.user_id = user_id1
        self.ya_token = ya_token1

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.199'
        }

    def get_photos(self):
        photo_album = []
        pic_likes = []
        type_album = []
        new_size = []
        new_types = []
        params_dict = self.get_common_params()
        params_dict.update({'user_id': self.user_id, 'album_id': 'profile', 'extended': '1'})
        response1 = requests.get(f'{self.API_BASE_URL}/photos.get', params = params_dict)
        self_response = response1.json()['response']['items']
        sort_by_date = sorted(self_response, key = lambda x: x['date'])
        sort_by_likes = sorted(sort_by_date, key = lambda x: x['likes']['count'], reverse = True)
        for answer in sort_by_likes:
            pic_likes.append(answer['likes']['count'])
            for size in answer.get('sizes'):
                one_pic_sizes = {size.get('url'): size.get('height')}
                size_types = {size.get('type'): size.get('height')}
                new_types = sorted(size_types, key = lambda d: d[-1])
                new_size = sorted(one_pic_sizes, key = lambda d: d[1])
            photo_album.append(new_size[-1])
            type_album.append(new_types[-1])
        updated_album = dict(zip(photo_album, zip(pic_likes, type_album)))
        return updated_album

    def upload_photos(self):
        path = 'VK_photo_copy'
        url_yandisk = 'https://cloud-api.yandex.net'
        url_create_folder = f'{url_yandisk}/v1/disk/resources'
        items = []
        params_dict = {
            'path': path
        }
        headers = {
            'Authorization': self.ya_token
        }
        requests.put(url_create_folder, params = params_dict, headers = headers)
        url_upload_photos = f'{url_yandisk}/v1/disk/resources/upload'
        count = 5
        likes = 10000000000000000000000000000000000000000000000000000000000000000000000
        for photo, likes_and_types in self.get_photos().items():
            print(count, ':')
            if likes_and_types[0] == likes:
                likes = f'{likes_and_types[0]}({count})'
            else:
                likes = likes_and_types[0]
            if count != 0:
                params_dict = {
                    'path': f'{path}/{likes}',
                    'url': photo
                }
                count -= 1
                response1 = requests.post(url_upload_photos, params = params_dict, headers = headers)
                items.append({"file_name": f'{likes}.jpg',
                              "size": likes_and_types[1]})
                likes = likes_and_types[0]
                print(response1)
            else:
                print('<All done!>')
        info_dict = {
            "channel": {
                "file_name": "amount of likes on a photo",
                "size": "name of the photo size",
                "items": [items]
            }
        }
        json_info = json.dumps(info_dict, indent = 4)
        with open('VK_photo_copy.json', 'w') as j:
            j.write(json_info)


if __name__ == '__main__':
    print(get_token_url())
    vk_client = VK_api(Token, user_id, ya_token)
    pprint(vk_client.upload_photos())
