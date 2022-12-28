import requests
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess

def jalali_to_gregorian(jy, jm, jd):
 jy += 1595
 days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
 if (jm < 7):
  days += (jm - 1) * 31
 else:
  days += ((jm - 7) * 30) + 186
 gy = 400 * (days // 146097)
 days %= 146097
 if (days > 36524):
  days -= 1
  gy += 100 * (days // 36524)
  days %= 36524
  if (days >= 365):
   days += 1
 gy += 4 * (days // 1461)
 days %= 1461
 if (days > 365):
  gy += ((days - 1) // 365)
  days = (days - 1) % 365
 gd = days + 1
 if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
  kab = 29
 else:
  kab = 28
 sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
 gm = 0
 while (gm < 13 and gd > sal_a[gm]):
  gd -= sal_a[gm]
  gm += 1
 return [gy, gm, gd]

def convert(year , month):
    year= str(year)
    month = str(month)

    api_url_curl = f"""
    curl --location --request POST 'https://www.time.ir/' \
    --form 'Year={year}' \
    --form 'Month={month}' \
    --form 'Base1="0"' \
    --form 'Base2="1"' \
    --form 'Base3="2"' \
    --form 'Responsive="true"'
    """

    status, output = subprocess.getstatusoutput(api_url_curl)

    soup = BeautifulSoup(output, 'html.parser')

    objs = soup.findAll('ul', {'class': 'list-unstyled'})[0].findAll('li')

    result = []
    for obj in objs:
        j = 0
        is_holiday = False
        if obj.attrs['class'] == ['eventHoliday']:
            is_holiday = True
        span = obj.find('span')
        geo_date = jalali_to_gregorian(int(year), int(month), int(span.text.split()[0]))
        value = {
            "day": span.text.strip(),
            "date": geo_date,
            "event": obj.text.replace(span.text, '').replace('\n', '').strip().replace('                             ',
                                                                                       ' '),
            "date_time" : datetime(int(geo_date[0]), int(geo_date[1]), int(geo_date[2])),
            "is_holiday": is_holiday
        }
        result.append(value)

    return result
