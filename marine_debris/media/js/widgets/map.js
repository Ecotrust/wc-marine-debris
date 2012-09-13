var layerExtent = new OpenLayers.Bounds( -14050000, 3800000, -13400000 , 6220000);
var map = new OpenLayers.Map("map", {'restrictedExtent': layerExtent});

var map_extent = new OpenLayers.Bounds(-20037508, -20037508, 20037508, 20037508.34);	
    
//Map base options
var map_options = {
    controls: [],
    projection: new OpenLayers.Projection("EPSG:900913"),
    displayProjection: new OpenLayers.Projection("EPSG:4326"),
    units: "m",
    numZoomLevels: 21,
    maxResolution: 156543.0339,
    eventListeners: {
        "zoomend": this.zoomHandler,
        scope: this
    }
};       

esriOcean = new OpenLayers.Layer.XYZ("ESRI Ocean", "http://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/${z}/${y}/${x}", {
    sphericalMercator: true,
    isBaseLayer: true,
    // numZoomLevels: 13,
    maxExtent: map_extent,
});

map.addLayers([esriOcean]);
map.zoomToExtent(map.restrictedExtent);