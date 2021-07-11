from bs4 import BeautifulSoup
import re
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

class downloader:
    def __init__(self,mainlink,st,end):
        self.mainlink=mainlink
        self.st=st
        self.end=end
    
    
    ##
    def get_all_eps(self,mainlink):
        res=requests.get(mainlink,headers=headers)
        sp=BeautifulSoup(res.text,'html.parser')

        wdgts=sp.find_all('div',{'class':'Wdgt AABox'})
        eps=[]
        num=1
        for wdgt in wdgts:
            table=wdgt.find('table')
            trs=table.find_all('tr')
            for tr in trs:
                ep={}
                #num=tr.find('span',{"class":'Num'}).text
                ep['num']=num
                num+=1
                link=tr.find('td',{'class':'MvTbTtl'}).find('a').get('href')
                ep['link']=link
                name=tr.find('td',{'class':'MvTbTtl'}).find('a').text
                ep['name']=name
                eps.append(ep)
        self.eps=eps
        return eps
    ##
    def get_4shared_id(self,soup):
        ul=soup.find('ul',{'class':'TPlayerNv'})    # find list of servers available 
        FourShared_ids=[]
        for li in ul.find_all('li'):
            data={}
            if '4shared' in li.text:
                idd=li.get("data-tplayernv")
                data['name']=li.text
                data['id']=idd
                FourShared_ids.append(data)
        #[{'name': '4shared - 1080p', 'id': 'Opt4'},
        # {'name': '4shared - 720p', 'id': 'Opt7'},
        # {'name': '4shared - 360p', 'id': 'Opt10'}]
        self.FourShared_ids=FourShared_ids
        return FourShared_ids
    ##
    def find_iframe(self,Id,soup):
        div=soup.find('div',{'class':'TPlayerCn BgA'}).find('div',{'id':Id})
        iframesrc=BeautifulSoup(div.text,'html.parser').find('iframe').get('src')

        #'https://ww1.gateanime.com/?trembed=3&trid=10766&trtype=2'
        return iframesrc

    ##
    def get_download_link(self,iframe):
        r=requests.get(iframe,headers=headers)
        sp=BeautifulSoup(r.text,'html.parser')
        iframeSrc=sp.find('iframe').get('src')
        #https://www.4shared.com/web/embed/file/IYrq_GX5iq

        r1=requests.get(iframeSrc,headers=headers)
        sp1=BeautifulSoup(r1.text,'html.parser')
        link=sp1.find('video').find('source').get('src')
        #https://dc349.4shared.com/img/IYrq_GX5iq/y_26lgfp_3D66_26bip_3DNDEuMjUxLjEuMjUy_26bip_3DNDEuMjUxLjEuMjUy/preview.mp4
        return link
    ##
    def chose_best_quality(self,listt):
        #[{'name': '4shared - 1080p', 'id': 'Opt4'},
        # {'name': '4shared - 720p', 'id': 'Opt7'},
        # {'name': '4shared - 360p', 'id': 'Opt10'}]
        if len(listt) == 1:
            return listt[0]
        else:
            for q in listt:
                if '1080' in q['name']:
                    return q

                if '720' in q['name']:
                    return q

                if '360' in q['name']:
                    return q
        return None
    ##
    def test(self):
        print(self.FourShared_ids)
        
    def start(self):
        mainlink=self.mainlink
        print('getting eps //')
        eps=self.get_all_eps(mainlink)
        epsNeeded=eps[int(self.st)-1:int(self.end)]
        print('looping ..')
        for ep in epsNeeded:
            print('scraping ep : {}'.format(ep['name']))
            print(ep['link'])
            response = requests.get(ep['link'], headers=headers)
            soup=BeautifulSoup(response.text,'html.parser')
            
            FourShared_ids=self.get_4shared_id(soup)
            if len(FourShared_ids)==0:
                print('no 4shared server found !')
                print('check the ep link : \n')
            else:                
                print('chosing best quality ..')
                bestQ=self.chose_best_quality(FourShared_ids)
                if bestQ==None:
                    print('no best found !')
                    print('chose one : ')
                    for index, _ in enumerate(FourShared_ids) :
                        print(index,_['name'])
                    ind=int(input('-:'))
                    bestQ=FourShared_ids[ind]['id']
    
                bestId=bestQ['id']

                print('best is {}'.format(bestQ['name']))
                #
                iframe=self.find_iframe(bestId,soup)
                print('getting download link')
                download=self.get_download_link(iframe)
                print(download)
                print('\n')
                print('\n')
