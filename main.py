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
        photo_dict ={}
        params_dict = self.get_common_params()
        params_dict.update({'user_id': self.user_id, 'album_id': 'profile', 'extended': '1'})
        response1 = requests.get(f'{self.API_BASE_URL}/photos.get', params = params_dict)
        for item in response1.json()['response']['items']:
            likes = str(item.get('likes').get('count'))
            date = item.get('date')
            sizes = sorted(item.get('sizes'), key = lambda x: x['height']*x['width'])
            type = sizes[-1].get('type')
            url = sizes[-1].get('url')
            size = {'type': type, 'url': url}
            if likes in photo_dict:
                photo_dict[f'{likes}({date})'] = size
            else:
                photo_dict[likes] = size
        return photo_dict

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
        for item in self.get_photos().items():
            print(count, ':')
            if count != 0:
                params_dict = {
                    'path': f'{path}/{item[0]}',
                    'url': item[1].get('url')
                }
                count -= 1
                response1 = requests.post(url_upload_photos, params = params_dict, headers = headers)
                items.append({"file_name": f'{item[0]}.jpg',
                              "size": item[1].get('type')})
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
    print(vk_client.upload_photos())
