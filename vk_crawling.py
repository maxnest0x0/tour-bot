import requests
import re

user_token = '20de5dba20de5dba20de5dbae323c8c4ad220de20de5dba45a8831f4c6fd24ff12e10fb'
version = 5.199
domain = 'krugosvetka66'

for post_number in range(1, 501, 20):
    my_response = requests.get('https://api.vk.com/method/wall.get',
                               params={
                                   'access_token': user_token,
                                   'domain': domain,
                                   'v': version,
                                   'offset': post_number
                               })

    result = my_response.json()

    with open('data.txt', 'a') as f:
        for i in range(20):
            post = result['response']['items'][i]
            text = post['text'].replace('\n', '')
            if len(text) > 120:
                num_of_repeats = text.count('|')
                for i in range(num_of_repeats):
                    ind1 = text.index('[')
                    ind2 = text.index('|')
                    text = text[:ind1] + text[ind2+1:]
                emoji_links = re.compile("["
                                            u"\U0001F600-\U0001F64F"
                                            u"\U0001F300-\U0001F5FF"
                                            u"\U0001F680-\U0001F6FF"
                                            u"\U0001F1E0-\U0001F1FF"
                                            u"\U00002500-\U00002BEF"
                                            u"\U00002702-\U000027B0"
                                            u"\U000024C2-\U0001F251"
                                            u"\U0001f926-\U0001f937"
                                            u"\U00010000-\U0010ffff"
                                            u"\u2640-\u2642"
                                            u"\u2600-\u2B55"
                                            u"\u200d"
                                            u"\u23cf"
                                            u"\u23e9"
                                            u"\u231a"
                                            u"\ufe0f"
                                            u"\u3030""]+", re.UNICODE)
                almost_result = emoji_links.sub(r'', text)
                text_in_list = almost_result.split()
                for word in text_in_list:
                    if ('http' in word) or ('+7' in word):
                        text_in_list.remove(word)
                res = ' '.join(text_in_list)
                f.write(res)
                f.write('\n'*2)
