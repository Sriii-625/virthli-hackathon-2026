let latitude = 0;
let longitude = 0;
let coordinatesFetched = false; // 1. New state flag

const mapDisplay = document.getElementById("map");
const apiKeyInput = document.getElementById("API_KEY");
let API_KEY = ""; 

let map, aqLayer; 

function updateAPIKey() {
    // 3. Check if coordinates are fetched before proceeding
    if (!coordinatesFetched) {
        alert("Please click 'Get Coordinates' first to establish your location.");
        return; // Exits the function early
    }

    API_KEY = apiKeyInput.value; 
    apiKeyInput.value = ""; 
    generateHeatmap(); 
}

const geolocation = () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function showPosition(position) {
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
    coordinatesFetched = true; // 2. Update flag upon successful retrieval
    alert("Latitude: " + latitude + "\nLongitude: " + longitude);
}

function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        default:
            alert("An unknown error occurred.");
    }
}

function zoomToLocation() {
    // 3. Check if coordinates are fetched before proceeding
    if (!coordinatesFetched) {
        alert("Please click 'Get Coordinates' first to establish your location.");
        return; // Exits the function early
    }

    if (map) { 
        map.setCenter({ lat: latitude, lng: longitude });
        map.setZoom(15);
    } else {
        alert("Map is not initialized yet. Please update your API key.");
    }
}

function generateHeatmap() {
    const googleMapsScript = document.createElement('script');
    
    googleMapsScript.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&callback=initMap`;
    googleMapsScript.async = true;
    googleMapsScript.defer = true;
    document.head.appendChild(googleMapsScript);
}

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: { lat: latitude, lng: longitude },
        mapTypeId: "terrain",
        mapTypeControl: true,
        mapTypeControlOptions: {
            mapTypeIds: [
                google.maps.MapTypeId.ROADMAP,
                google.maps.MapTypeId.SATELLITE,
                google.maps.MapTypeId.HYBRID,
                google.maps.MapTypeId.TERRAIN
            ],
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_LEFT
        }
    });

    const mapType = "UAQI_RED_GREEN";

    aqLayer = new google.maps.ImageMapType({
        getTileUrl: function (coord, zoom) {
            return `https://airquality.googleapis.com/v1/mapTypes/${mapType}/heatmapTiles/${zoom}/${coord.x}/${coord.y}?key=${API_KEY}`;
        },
        tileSize: new google.maps.Size(256, 256),
        maxZoom: 16,
        opacity: 0.50,
        name: "Air Quality"
    });

    map.overlayMapTypes.insertAt(0, aqLayer);

    let mapHolder = document.getElementById("mapHolder");
    mapHolder.style.display = "none"; 
}