# EC

Indigo 7 plugin for Environment Canada weather data

![Environment Canada](http://www.public-domain-photos.com/free-cliparts-1/flags/america/national_flag_of_canada_.png)

[Indigo](https://www.indigodomo.com) is a home automation software controller for the Mac supporting multiple interface technologies.

This plugin allows you to create weather station "devices" that can provide data to Indigo. For example, you can create a weather station for the nearest Environment Canada site and use its data to feed rules in Indigo.

Creating a new weather device is the same as for any new plugin device in Indigo. After creating the device, you will be presented with a configuration dialog for the device:

![Weather device configuration](http://res.cloudinary.com/deleyamlh/image/upload/v1487671703/Screen_Shot_2017-02-21_at_05.06.28_jvyxpw.png)

By clicking the button you can find a [list of all of the available weather station](http://dd.weather.gc.ca/citypage_weather/docs/site_list_towns_en.csv) identifiers in Canada. If you would prefer to search by province, you can [search here](http://dd.weather.gc.ca/citypage_weather/xml/) too. Sorry, there's not a cleaner way to do this yet.

That's all there is to it.

## Custom server states exposed by the plugin

- `observationDate` - timestamp of the most recent observationDate
- `currentCondition` - description of the current conditions at the station
- `temperature` - current temperature at the station in °C
- `temperatureString` - human readable temperature as string with units
- `dewpoint` - current dewpoint at the station in °C
- `dewpointString` - human readable dewpoint as string with units
- `humidity` - relative humidity at the station.
- `pressure` - barometric pressure at the station in kPa
- `visibility` - current visibility at the station in km
- `windSpeed` - wind speed in km/h
- `windBearing` - wind bearing as string
- `windGust` - wind gust in km/h
- `yesterdayHighTemp` - yesterday's high temperature in °C
- `yesterdayLowTemp` - yesterday's low temperature in °C
- `yesterdayPrecipitation` - yesterday's precipitation in cm

To install the plugin, you'll need to [follow the instructions](http://wiki.indigodomo.com/doku.php?id=indigo_6_documentation:plugin_guide) with particular attention to naming the direction with the `.indigoPlugin` extension to create the required bundle. 
