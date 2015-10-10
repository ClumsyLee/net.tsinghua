from bs4 import BeautifulSoup as bs
from urllib import request, parse
from http import cookiejar

class SimuBrowser:
    def __init__(self, usr, pwd):
        self.username = usr
        self.password = pwd
        self.index_page = 'http://info.tsinghua.edu.cn/'
        self.info = {}
        self.scores = [0, 0]
        self.gpa = [0, 0]

    def get_form(self, idxpage=None):
        if not idxpage:
            page = bs(request.urlopen(self.index_page))
        else:
            page = bs(request.urlopen(idxpage))
        inputs = [i for i in page.form.find_all('input') if i['type'] not in ['hidden','image']]
        info = {'dst':page.form['action']}
        for ipt in inputs:
            if 'value' in ipt:
                info[ipt['name']] = ipt['value']
            else:
                info[ipt['name']] = 0
        for tag in info:
            if 'u' in tag and not info[tag]:
                info[tag] = self.username
            elif 'p' in tag and not info[tag]:
                info[tag] = self.password
        if not idxpage:
            self.info = info
        return info

    def get_gpa(self, display=False):
        self.get_form()
        cj = cookiejar.CookieJar()
        browser = request.build_opener(request.HTTPCookieProcessor(cj))
        browser.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
        dst = self.info.pop('dst')
        data = parse.urlencode(self.info).encode()
        resp = bs(browser.open(dst, data))
        if resp.find(text='进入门户'):
            info_url = self.index_page[:-1] + resp.find(text='进入门户').parent.parent['href']
            resp = bs(browser.open(info_url))
        logs = [i.text for i in resp.find(class_="log").find_all('span')]
        if display:
            for log in logs:
                print(log)
        iframes = resp.find_all('iframe')
        for ifr in iframes:
            src = ifr['src']
            if src.startswith('http'):
                browser.open(src)
            else:
                browser.open(self.index_page[:-1]+src)
        score_url = resp.find(text='全部成绩').parent['href']
        score_page = bs(browser.open(score_url))
        lines = score_page.find_all('tr')
        multi = [0, 0]
        for line in lines:
            cols = line.find_all('td')
            try:
                s = cols[5].text.strip()
                if s in ['通过', '优秀']:
                    pass
                s = int(s)
                w = int(cols[3].text.strip())
                if '任选' in cols[7].text:
                    multi[1] += s * w
                    self.scores[1] += w
                else:
                    multi[0] += s * w
                    self.scores[0] += w
                    multi[1] += s * w
                    self.scores[1] += w
            except:
                pass
        self.gpa[0] = multi[0] / self.scores[0]
        self.gpa[1] = multi[1] / self.scores[1]
        if display:
            print(self.scores)
            print(self.gpa[0])
            print(self.gpa[1])


# simu = SimuBrowser(username, password)
# simu.get_gpa(False)
# simu.gpa[0] for required subjects GPA
# simu.gpa[1] for all courses GPA
