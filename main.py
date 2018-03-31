import json
import requests
import api_keys
import base64
import config
import time
import csv

def main():
	hot_count = 0
	earthquake_count = 0
	weather_ops = auth_weather_ops(api_keys.WEATHER_OPS_ID, api_keys.WEATHER_OPS_SECRET)

	relevant=[]
	with open('results', 'r') as f:
		next(f)
		reader = csv.reader(f, delimiter='\t')
		for item in reader:
			relevant.append({
							'year':item[2],
							'month':item[3],
							'day':item[4],
							'lat':item[20],
							'lng':item[21]
						})
		f.close()
	print('Waiting 9 seconds to comply with wunderground api...')
	for item in relevant:
		m=int(item['month'])
		d=int(item['day'])
		y=int(item['year'])
		lat=item['lat'].strip()
		lng=item['lng'].strip()
		#loop through earthquake files
		temp = get_temp(m,d,y,lat,lng)
		avg_temp = get_mean_temp(m,d,lat,lng,weather_ops)
		diff = 1
		try:
			diff = temp-avg_temp
			if diff>3:
				hot_count+=1
			earthquake_count+=1	
		except:
			diff = temp and avg_temp
	print('Out of '+str(earthquake_count)+' earthquake days, '+str(hot_count)+' were hotter than usual for that day.')
	
def get_temp(m,d,y,lat,lng): #returns temp for that day in fahrenheit
	time.sleep(9) #prevents reaching wunderground call limit
	m = '0'+str(m) if m<10 else str(m)
	d = '0'+str(d) if d<10 else str(d)
	y = str(y)
	r = requests.get('http://api.wunderground.com/api/63ef2a0a47a5d435/history_'+y+m+d+'/q/'+lat+','+lng+'.json')
	temp = json.loads(r.text)
	# print(temp)
	try:
		a = temp['history']['dailysummary'][0]['meantempi']
		if int(a)<1000000: #keeps from storing blank info
			print("The temperature at {}, {} on {}-{}-{} is {} degrees fahrenheit.".format(str(lat), str(lng), m, d, y, str(a)))
			return float(a)
		return False
	except:
		return False
	# return float(a)

def auth_awhere(): #TODO: keep track of api tokens, they expire after an hour
	auth = api_keys.AWHERE_KEY+':'+api_keys.AWHERE_SECRET
	b_auth = base64.b64encode(auth.encode()).decode()
	r = requests.post('https://api.awhere.com/oauth/token', 
		headers = {
			'Content-type':'application/x-www-form-urlencoded', 
			'Authorization':'Basic '+b_auth
		},
		data = {
			'grant_type':'client_credentials'
		})
	res = json.loads(r.text)
	print(res['access_token'])
	return res['access_token']

def auth_weather_ops(key,secret):
	auth = key+':'+secret
	b_auth = base64.b64encode(auth.encode()).decode()
	return 'Basic '+b_auth

def get_mean_temp(m,d,lat,lng,auth): #heh freedom units! so this function averages the highs and lows of that day
									 #who knew getting mean temp data would be so hard >>
	m = '0'+str(m) if m<10 else str(m)
	d = '0'+str(d) if d<10 else str(d)

	high_temp_req = requests.get("https://insight.api.wdtinc.com/climatology/daily-high-temperature/"+lat+'/'+lng+'?unit=fahrenheit', headers={
			'Authorization':auth
		}, data={
			'start':m+'-'+d,
			'end':m+'-'+d
		})
	high_temp = (json.loads(high_temp_req.text)) ["highTemperature"]
	low_temp_req = requests.get("https://insight.api.wdtinc.com/climatology/daily-low-temperature/"+lat+'/'+lng+'?unit=fahrenheit', headers={
			'Authorization':auth
		}, data={
			'start':m+'-'+d,
			'end':m+'-'+d
		})
	low_temp = (json.loads(low_temp_req.text))["lowTemperature"]
	avg_temp = round((low_temp+high_temp)*0.5,1)
	print("The average temperature for {}-{} at {}, {} is {} degrees fahrenheit.".format(m,d,str(lat),str(lng),str(avg_temp)))
	return avg_temp

if __name__ == '__main__':
	main()