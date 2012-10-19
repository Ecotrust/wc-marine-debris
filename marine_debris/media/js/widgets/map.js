var layerExtent = new OpenLayers.Bounds( -14050000, 3800000, -13000000 , 6280000);

var map = new OpenLayers.Map("map", {'restrictedExtent': layerExtent});

var map_extent = new OpenLayers.Bounds(-20037508, -20037508, 20037508, 20037508.34);	
    
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

esriOcean = new OpenLayers.Layer.XYZ("ESRI Ocean", "http://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/${z}/${y}/${x}", {
    sphericalMercator: true,
    projection: map_options.displayProjection,
    numZoomLevels: map_options.numZoomLevels,
    isBaseLayer: true,
    maxExtent: map_extent,
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
    point = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(lon, lat));
    point.geometry.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
    pointLayer.addFeatures(point);
    pointLayer.drawFeature(point);
    clearOldPoints(point);
    map.setCenter([pointLayer.features[0].geometry.x, pointLayer.features[0].geometry.y], 11, true);
    pointLayer.redraw()
}

map.addLayers([esriOcean, pointLayer]);
map.zoomToExtent(map.restrictedExtent);

map.addControl(point);
point.activate();