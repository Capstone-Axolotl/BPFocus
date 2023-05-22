from time import strftime

df=(12, 13, 14)
health_time=strftime('%Y-%m-%d %H:%M:%S')
print(health_time)

for i in df:
    print(("update health_check set off_time='{}' where id='{}'").format(health_time, i))
