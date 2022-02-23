# Change id for location
# Toronto : 6167865
# Tokyo : 1850147
# Osaka : 1853909
# Gdansk : 3099434
# Olsztynek : 763165
# appid from https://openweathermap.org 
#
API_KEY="69112e20210bc2c957e8bb5f3cb85ac4"
WEATHER_ID=3099434


SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
wget -O ${SCRIPTPATH}/current-data.json "http://api.openweathermap.org/data/2.5/weather?id=$WEATHER_ID&&units=metric&appid=$API_KEY"
wget -O ${SCRIPTPATH}/forecast-data.json "http://api.openweathermap.org/data/2.5/forecast?id=$WEATHER_ID&units=metric&appid=$API_KEY"
