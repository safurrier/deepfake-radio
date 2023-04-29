# %%
# [markdown] ##
from dotenv import load_dotenv
import requests
# Load the .env file
load_dotenv()


import os

print(os.environ.get('BOT_TOKEN'))
print(os.environ.get('ELEVEN_API_KEY'))

# %%
# [markdown] ##
site = "https://api.elevenlabs.io/v1/voices"
headers = {
        'accept': 'application/json',
        'xi-api-key': os.environ.get('ELEVEN_API_KEY')
    }
r = requests.get(site, headers=headers)
r_json = r.json()

# %%
# [markdown] ##
r_json.keys()
# %%
r_json['voices'][18]
# %%
# for v in r_json['voices']:
#     if v['category'] == 'cloned':
#         print(v['name'])
#         print(v['voice_id'])

VOICES = {
   v['name']:v['voice_id'] for v in r_json['voices'] if v['category'] == 'cloned'
}
VOICES


# %%
