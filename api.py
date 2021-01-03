import requests

# template = 'https://www.google.com/search?q={}+episodes'

# title = 'breaking bad'
# folder = 'season 1'

# print(template.format('+'.join(title.split(' ') + folder.split(' '))))

# url = template.format('+'.join(title.split(' ') + folder.split(' ')))
# page = requests.get(url)


# enough of the scraping, lets get it through API.

baseUrl = 'http://api.tvmaze.com/singlesearch/shows?q={}&embed=episodes'

def getDataFor(title):

    try:
        url = baseUrl.format('+'.join(title.split(' ')))
        response = requests.get(url)
        response.raise_for_status()
    
    except Exception as err:
        print(f'Other error occurred. {err}')
        return {'status': 0}
    
    else:
        data = response.json()
        # print(data)

        assert response.status_code == 200
        info = {}

        info['name'] = data['name']
        info['language'] = data['language']
        info['genres'] = data['genres']
        info['premiered'] = data['premiered']

        seasonInfo = {}
        seasonNumber = 1
        episodeList = []

        for episode in data['_embedded']['episodes']:
            # print(f"Season {episode['season']} Episode {episode['number']} {episode['name']}")

            if int(episode['season']) != seasonNumber:
                seasonInfo[f'Season {seasonNumber}'] = {number: name for number, name in episodeList}
                seasonNumber = seasonNumber + 1
                episodeList.clear()
            
            episodeList.append((episode['number'], episode['name']))

        seasonInfo[f'Season {seasonNumber}'] = {number: name for number, name in episodeList}    
        
        info['episodes'] = seasonInfo
        info['status'] = 1
        
        # print(info)
        return info


if __name__ == '__main__':

    getDataFor('a simple murder')
    # getDataFor('attack on titan')
    # getDataFor('friends')
    # getDataFor('fleabag')