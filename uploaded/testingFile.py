from datetime import date
import datetime
import pytz


tz = pytz.timezone('Africa/Johannesburg')

today = date.today()
time = datetime.datetime.now(tz)

print(time)
# print(str(time.hour)+":"+str(time.minute))
# time_h = str(time.hour)+":"+str(time.minute)
# date_d = str(today.day)+"/"+str(today.month)+"/"
# d2 = str(date_d+time_h)

# print("Today's date:", d2)
# datetime_str = '13/11/12:7'
# datetime_object = datetime.datetime.strptime(datetime_str, '%d/%m/%H:%M')
# print(datetime_object)
# print(datetime_object.hour == time.hour)