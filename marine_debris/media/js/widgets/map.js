var layerExtent = new OpenLayers.Bounds( -14050000, 3800000, -13000000 , 6280000);

var map = new OpenLayers.Map("map", {'restrictedExtent': layerExtent});

OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
    defaultHandlerOptions: {
        'single': true,
        'double': false,
        'pixelTolerance': 0,
        'stopSingle': false,
        'stopDouble': false
    },
    initialize: function(options) {
        this.handlerOptions = OpenLayers.Util.extend(
            {}, this.defaultHandlerOptions
        );
        OpenLayers.Control.prototype.initialize.apply(
            this, arguments
        );
        this.handler = new OpenLayers.Handler.Click(
            this, {
                'click': this.trigger
            }, this.handlerOptions
        );
    },
    trigger: function(e) {
        var lonlat = map.getLonLatFromPixel(e.xy).transform(new OpenLayers.Projection("EPSG:900913"), new OpenLayers.Projection("EPSG:4326"));
        try{
            updateCoordVals(lonlat.lon, lonlat.lat);
        }
        catch(e){
            // function updateCoordVals(lon, lat) not available
        }
    }
}); 

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
    projection: map_options.displayProjection,
    isBaseLayer: true,
    // numZoomLevels: 13,
    maxExtent: map_extent,
});

map.addLayers([esriOcean]);
map.zoomToExtent(map.restrictedExtent);
var click = new OpenLayers.Control.Click();
map.addControl(click);
click.activate(); 