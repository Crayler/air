import csv
import time
import requests
from bs4 import BeautifulSoup


class AqiSpider:
    def __init__(self,cityname,realname):
        self.cityname = cityname
        self.realname = realname
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
        }
        self.f = open(f'data.csv','a',encoding='utf-8-sig',newline='')
        self.write = csv.DictWriter(self.f,fieldnames=[
            'city',
            'date',
            'AQI',
            'airQuality',
            'rank',
            'PM2.5',
            'PM10',
            'So2',
            'No2',
            'Co',
            'O3',
        ])
        self.write.writeheader()
        

    def send_requests(self,year,month):
        url = f"https://www.tianqihoubao.com/aqi/{self.cityname}-"+str(year)+str("%02d"%month)+".html"
     
        response = requests.get(url,headers=self.headers,timeout=60)
        time.sleep(2)

        #print(response.text)
        #响应码200为成功
        print(f"响应状态码：{response.status_code}")
        self.parse_response(response.text)
       

    def parse_response(self,response):
        soup = BeautifulSoup(response,"html.parser")
        tr = soup.find_all('tr')

        for j in tr[1:]:
            td = j.find_all('td')
            Date = td[0].get_text().strip()#日期
            Quality_leval = td [1].get_text().strip()#空气质量等级
            AQI = td [2].get_text().strip()
            AQI_rank = td [3].get_text().strip()
            PM25 = td [4].get_text().strip()
            PM10 = td [5].get_text().strip()
            SO2 = td [6].get_text().strip()
            NO2 = td [7].get_text().strip()
            CO = td [8].get_text().strip()
            O3 = td [9].get_text().strip()
            data_dict = {
                'city':self.realname,
                'date':Date,
                'airQuality':Quality_leval,
                'AQI':AQI,
                'rank':AQI_rank,
                'PM2.5':PM25,
                'PM10':PM10,
                'So2':SO2,
                'No2':NO2,
                'Co':CO,
                'O3':O3,
            }

            # print(data_dict)
            self.save_data(data_dict)
            #break

    def save_data(self,data_dict):
        #存储
        # print('存入')
        self.write.writerow(data_dict)




    def run(self):
        for month in range(1,13):
            print(f"正在爬取{2025}年{month}月的数据")
            self.send_requests(2025,month)

if __name__ == '__main__':
    cityList = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'chengdu', 'wuhan', 'hangzhou', 'chongqing', 'suzhou']
    nameList = ['北京', '上海', '广州', '深圳', '成都', '武汉', '杭州', '重庆', '苏州']
    city_dict = dict(zip(cityList,nameList))
    #print(city_dict)
    for k,v in city_dict.items():

        AS = AqiSpider(k,v)
        AS.run()
       # break
        
       