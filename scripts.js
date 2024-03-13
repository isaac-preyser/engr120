var weatherData = null; //global variable to store the weather data
var positionData = null; //global variable to store the position data
var publicToken = "pk.eyJ1IjoicHJleXNlciIsImEiOiJjbHRvenp2b3YwNTVqMmpwa3ZldmdzdzI5In0.xxdA2sVzYqcyU1kJPGek0Q" //for mapbox API

function getWeather(lat, long, callback) {
    var apiUrl = "https://api.pirateweather.net/forecast/8xb4Xw81stuOYY6R9OaUdLcwsbsRQzBa/"+lat+"%2C"+long+"?units=ca";
        fetch(apiUrl).then(response => {
            // weatherData = response.json();
            return response.json();
        }).then(data => {
            // Work with JSON data here
            weatherData = data; //store the data in the global variable
            document.getElementById("forecast").innerHTML = "It is currently "+ Math.round(weatherData.currently.temperature) + " degrees and " + weatherData.currently.summary +".";
            console.log(data);
            callback(); //call the callback function
        }).catch(err => {
            // Do something for an error here
            console.log("Error: " + err);
        });

    }

function init() {
    //get coordinates of user via geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var lat = position.coords.latitude;
            var long = position.coords.longitude;
            console.log(lat);
            console.log(long);
            //TODO call getWeather with lat and long as parameters
            getWeather(lat, long, function() {
                //update the location on the DOM
                console.log("Data has been loaded");
                updateLocationByCoordinates(lat, long);
            });
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

function getLocation(){
    //grab the user input from the text box with id locationInput
    var location = document.getElementById("locationInput").value;
    //format string for URL
    location = location.replace(" ", "%20");


    //use the input to build the URL for the API
    //using mapbox API to get the latitude and longitude of the location

    
    
    var url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + location + ".json?proximity=ip&access_token=" + publicToken;

    //fetch the data from the API and store long and lat into globals 
    fetch(url).then(response => {
        return response.json();
    }).then(data => {
        // Work with JSON data here
        console.log(data);
        var lat = data.features[0].center[1];
        var long = data.features[0].center[0];
        console.log(lat);
        console.log(long);
        //call the weather function with the lat and long as parameters
        getWeather(lat, long);
        //update the location on the DOM
        document.getElementById("location").innerHTML = data.features[0].place_name;
    }).catch(err => {
        // Do something for an error here
        console.log("Error: " + err);
    });


}

function updateLocationByCoordinates(lat, long){
    //search for the location using lat and long via reverse geocoding
    //use the input to build the URL for the API
    //using mapbox API to get the latitude and longitude of the location

    var url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + long + "," + lat + ".json?proximity=ip&access_token=" + publicToken;

    //fetch the data from the API and update the location ID on the DOM
    fetch(url).then(response => {
        return response.json();
    }).then(data => {
        // Work with JSON data here
        positionData = data; //store the data in the global variable
        console.log(data);
        var location = data.features[2].place_name;
        console.log(location);
        document.getElementById("location").innerHTML = location;
    }).catch(err => {
        // Do something for an error here
        console.log("Error: " + err);
    });
}


//these functions toggle physical devices on the pi (server)
//these functions will send a request to the server to toggle the device
//ideally these should send PUT requests to update the state of the device
//maybe a JSON object with the device name and state


function toggleShades() {
    //send request to the server to toggle the shades


}

function toggleHeating() {

}

function toggleCooling() {
    //send request to the server to toggle the cooling

} 

function setTemp(){
    //update the temperature set on the DOM
    var temp = document.getElementById("tempInput").value;
    document.getElementById("tempDisplay").innerHTML = temp;
}