# coding: utf-8
import urllib2


url = 'http://s.weibo.com/ajax/pincode/pin?type=sass&ts=1501817480'

headers = {
    'Cookie': 'SINAGLOBAL=9403398050209.357.1501147614085; UOR=news.ifeng.com,widget.weibo.com,hs.blizzard.cn; _s_tentry=-; Apache=8380369896293.758.1501578696781; ULV=1501578696812:2:1:1:8380369896293.758.1501578696781:1501147614103; SWB=usrmdinst_23; SCF=An2ESVdRdUj_zMz-QF-ChKmo_wfCsPpRhR8BkYrlHPES6WNPsAmvcYGTWdG8QL2_2bzEZL1huQM5Moh2pKCHYNo.; SUHB=0V51buwx3MDxSR; ULOGIN_IMG=1501819154602',
    'Host': 'w.weibo.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
}

if __name__ == '__main__':
    req = urllib2.Request(url)
    for name, value in headers.items():
        req.add_header(name, value)
    res = urllib2.urlopen(req)
    f = open('test.jpg', 'w')
    f.write(res)
