var layerExtent = new OpenLayers.Bounds( -14050000, 3800000, -13000000 , 6300000);

var map = new OpenLayers.Map('map', {
  restrictedExtent: layerExtent,
  displayProjection: new OpenLayers.Projection("EPSG:4326"),
  projection: "EPSG:3857"
});

var map_extent = new OpenLayers.Bounds(-20037508, -20037508, 20037508, 20037508.34);	
    
function updateCoordVals(lon, lat) {
    $( "#id_latitude" ).val(lat.toFixed(6)).change();
    $( "#id_longitude" ).val(lon.toFixed(6)).change();
    $("#id_geometry").val("POINT(" + lon + " " + lat + ")");
    pointSelected(lat, lon);
}

//Map base options
var map_options = {
    controls: [],
    projection: new OpenLayers.Projection("EPSG:900913"),
    displayProjection: new OpenLayers.Projection("EPSG:4326"),
    units: "m",
    numZoomLevels: 13,
    maxResolution: 156543.0339,
    eventListeners: {
        "zoomend": this.zoomHandler,
        scope: this
    }
};       

var hybrid = new OpenLayers.Layer.Bing({
  name: "Hybrid",
  key: 'AvD-cuulbvBqwFDQGNB1gCXDEH4S6sEkS7Yw9r79gOyCvd2hBvQYPaRBem8cpkjv',
  type: "AerialWithLabels"
});


var pointLayer = new OpenLayers.Layer.Vector("Point Layer");

var point = new OpenLayers.Control.DrawFeature(
    pointLayer,
    OpenLayers.Handler.Point,
    {
        "featureAdded": pointDrawn
    }
);

function pointDrawn(point) {
    var lonlat = point.geometry.transform(new OpenLayers.Projection("EPSG:900913"), new OpenLayers.Projection("EPSG:4326"));
    clearOldPoints(point);
    updateCoordVals(lonlat.x, lonlat.y);
    // re-project point to 900913
    point.geometry.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
}

// Only display the newest selected point
function clearOldPoints(point){
    for (var i = 0; i <= pointLayer.features.length; i++){
        if (pointLayer.features[i] != point){
            pointLayer.removeFeatures(pointLayer.features[i]);
        }
    }
}

function pointSelected(lat, lon){
    var zoom = map.zoom < 12 ? map.zoom + 2: 12;
    point = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(parseFloat(lon), parseFloat(lat)));
    point.geometry.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
    pointLayer.addFeatures(point);
    pointLayer.drawFeature(point);
    clearOldPoints(point);
    map.setCenter([pointLayer.features[0].geometry.x, pointLayer.features[0].geometry.y], zoom);
    pointLayer.redraw()
}

map.addLayers([hybrid, pointLayer]);

map.addControl(point);
point.activate();
map.zoomTo(4);