import requests
from bs4 import BeautifulSoup
import re
from requests import urllib3
import urllib
import threading
import pymysql
url='http://wh.meituan.com/meishi/{}/pn'
baseUrl='http://wh.meituan.com/meishi/'
baseUrlComment='http://www.meituan.com/meishi/api/poi/getMerchantComment?uuid=65094818ee37415e9b11.1521373123.1.0.0&platform=1&partner=126&originUrl=http%3A%2F%2Fwww.meituan.com%2Fmeishi%2F1032903%2F&riskLevel=1&optimusCode=1&id={}&userId=0&offset=0&pageSize=10&sortType=1'
hd={
'Accept':'application/json',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Connection':'keep-alive',
'Cookie':'_lxsdk_cuid=1622d02cdf40-0c3bbf7da3ce24-b353461-e1000-1622d02cdf5c8; ci=57; client-id=12a406e2-c766-4701-8867-807bdec4614f; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk=1622d04adcac1-04f811df5a42cb-b353461-e1000-1622d04adcbc8; rvct=57; _ga=GA1.2.1381669426.1521272956; _gid=GA1.2.1147856201.1521272956; uuid=65094818ee37415e9b11.1521373123.1.0.0; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; lat=30.505605; lng=114.402741; __mta=50238873.1521173581663.1521344355738.1521344363998.37; _lxsdk_s=16237302179-05-e45-306%7C%7C12',
'Host':'www.meituan.com',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
   }
conn=pymysql.connect(host='localhost',user='root',password='123456',db='mysql',charset='utf8')
cur=conn.cursor()
sql='''
        create table districtInfo(
        districtName varchar(25) not null,
        resName varchar(225) not null,
        avgScore float(16) not null,
        Address varchar(255) not null,
        Longitude float(16) not null,
        Latitude float(16) not null,
        avgPrice int(8) not null,
        totalComment int(16) not null)DEFAULT CHARSET=utf8;
        '''
sqla='''
        insert into districtInfo(districtName,resName,avgScore,Address,Longitude,Latitude,avgPrice,totalComment)
        values(%s,%s,%s,%s,%s,%s,%s,%s);
        '''
try:
    employee=cur.execute(sql)
    print('成功')
except:
    print('数据库创建失败')
class myThread(threading.Thread):
    def __init__(self,districtName,districtNumber,districtCount):
        threading.Thread.__init__(self)
        self.districtName=districtName
        self.districtNumber=districtNumber
        self.districtCount=districtCount
    def run(self):
        fileName='D:\\'+self.districtName+'.txt'
        fileStream=open(fileName,'w')
        ownUrl=url.format(self.districtNumber)
        for i in range(int(self.districtCount)):
            currentMainUrl=ownUrl+str(i+1)+'/'
            print("#",end='')
            html=requests.get(currentMainUrl)
            poiPattern=re.compile(r'"poiId":[0-9]{6,9}')
            poiMessage=poiPattern.findall(html.text)
            for item in poiMessage:
                currentUrl=baseUrl+item[8:]+'/'
                try:
                    currentHtml=requests.get(currentUrl,headers=hd)
                    targetIforPattern=re.compile(r'"poiId":.*?"brandId"')
                    targetIfor=targetIforPattern.findall(currentHtml.text)
                    name=re.findall(r'"name":.*?,',targetIfor[0])
                    for it in name:
                        name=it[8:-2]
                    avgScore=re.findall(r'"avgScore":.*?,',targetIfor[0])
                    avgScore=avgScore[0][11:-1]
                    #fileStream.write(name+'\n'+'Average Score:'+avgScore+'\n')
                    address=re.findall(r'"address":.*?,',targetIfor[0])
                    address=address[0][11:-2]
                    #fileStream.write("Address:"+address+'\n')
                    longitude=re.findall(r'"longitude".*?,',targetIfor[0])
                    longitude=longitude[0][12:-1]
                    latitude=re.findall(r'"latitude".*?,',targetIfor[0])
                    latitude=latitude[0][11:-1]
                    #fileStream.write("Longitude:"+longitude+'\n'+"Latitude:"+latitude+'\n')
                    avgPrice=re.findall(r'"avgPrice".*?,',targetIfor[0])
                    avgPrice=avgPrice[0][11:-1]
                    #fileStream.write("Average Price:"+avgPrice+'\n')
                    currentCommentUrl=baseUrlComment.format(item[8:])
                    currentCommenthtml=requests.get(currentCommentUrl,headers=hd)
                    tagInfo=re.findall(r'"count":.*?\}',currentCommenthtml.text)
                    for item in tagInfo:
                        fileStream.write(item+'\t')
                    total=re.findall(r'"total":.*?\}',currentCommenthtml.text)
                    #fileStream.write('\n'+"Total Comment"+total[0][7:-1]+'\n')
                    cur.execute(sqla,(self.districtName,name,avgScore,address,longitude,latitude,avgPrice,total[0][7:-1]))
                except:
                    print("error!")
                finally:
                    pass
        fileStream.close()
        conn.commit()
        cur.close()
        conn.close()
districtInfo={"hongshanqu":["b112","14"],
             "hanyangqu":["b110","14"],
             "jianghanqu":["b108","19"],
             "wuchangqu":["b107","19"],
             "qiaokouqu":["b109","11"],
             "qingshanqu":["b111","16"],
             "jianganqu":["b106","18"],
             "dongxihuqu":["b203","15"],
             "jiangxiaqu":["b3403","22"],
             "huangpiqu":["b3404","16"],
             "caidianqu":["b3402","12"],
             "hannanqu":["b3401","2"],
             "xinzhouqu":["b3405","4"]
             }
threads=[]
for key in districtInfo:
    thread=myThread(key,districtInfo[key][0],districtInfo[key][1])
    threads.append(thread)
for item in threads:
    item.start()
for item in threads:
    item.join()
