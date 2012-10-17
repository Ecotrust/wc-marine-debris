

var app = {}, map = new OpenLayers.Map('map', {
  //allOverlays: true,
  displayProjection: new OpenLayers.Projection("EPSG:4326"),
  projection: "EPSG:3857"
});

app.map = map;
app.rowIndex = {};
app.points = new OpenLayers.Layer.Vector("Events", {
  renderers: OpenLayers.Layer.Vector.prototype.renderers,
  projection: "EPSG:4326",
  //strategies:[new OpenLayers.Strategy.Cluster({distance: 5})],
  styleMap: new OpenLayers.StyleMap({
    "default": new OpenLayers.Style({
      pointRadius: "${radius}",
      fillColor: "#ffcc66",
      fillOpacity: 0.8,
      strokeColor: "#cc6633",
      strokeWidth: 2,
      strokeOpacity: 0.8
    }, {
      context: {
        radius: function(feature) {
          return 5//Math.min(feature.attributes.count, 7) + 3;
        }
      }
    }),
    "select": {
      fillColor: "#8aeeef",
      strokeColor: "#32a8a9"
    }
  })
});




function viewModel(options) {
  var self = this;

  self.events = ko.observableArray();
  self.states = options.locations.states;
  self.locations = options.locations.locations;

  self.locationFilter = ko.observableArray();

  self.dataTablesOptions = {
    'bFilter': false, 
    "iDisplayLength": 5,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": "/events/get",
    "iDisplayStart": 0,
    "fnServerParams": function ( aoData ) {
      var filters = self.locationFilter();
      if (self.filterByExtent()) {
        filters.push({"type": "bbox", "bbox": self.mapExtent().transform(new OpenLayers.Projection("EPSG:900913"), new OpenLayers.Projection("EPSG:4326")).toBBOX() });
      };
      aoData.push( { "name": "filter", "value": JSON.stringify(filters) });
    }
  };

  // populate points
  self.addEvents = function (events) {
    $.each(events, function(i, event) {
      var state = event.site.state,
        pos = new OpenLayers.LonLat(event.site.lon, event.site.lat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")),
        point = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(event.site.lon, event.site.lat));

      event.pos = pos;
      event.feature = point;
      point.event = event;
      point.geometry.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
      self.events().push(event);
    });
  }

  // store mapextent here
  self.mapExtent = ko.observable();
  self.filterByExtent = ko.observable(false);

  self.showSpinner = ko.observable(false);

  self.filteredEvents = ko.computed(function() {
    var filteredEvents = [];
    self.showSpinner(true);
    if(self.locationFilter() && self.locationFilter().length !== 0) {
      $.each(self.events(), function(i, event) {
        $.each(self.locationFilter(), function(i, filter) {
          if((filter.type === 'state' && filter.name === event.site.state) || (filter.type === 'county' && filter.name === event.site.county.replace(" County", "") && filter.state === event.site.state)) {
            if(self.filterByExtent()) {
              if(self.mapExtent().containsLonLat(event.pos)) {
                filteredEvents.push(event);
              }
            } else {
              filteredEvents.push(event);
            }
          }
        });
      });
        
    } else if (self.filterByExtent()) {
      $.each(self.events(), function(i, event) {
          if(self.mapExtent().containsLonLat(event.pos)) {
            filteredEvents.push(event);
          }
        });
    } else {
      filteredEvents = self.events();
    }
    self.showSpinner(false);
    return filteredEvents;
  });
  
  self.getReport = function (filters) {
    self.showSpinner(true);
    $.ajax({
        url: "/events/get_values",
        type: 'GET',
        data: {
            "filters" : JSON.stringify(filters)
        },
        dataType: 'json'
    }).done(function(report) { 
        self.report(report);
        self.showSpinner(false);
    });
  };

  self.locationFilter.subscribe(function () {
    $('#events-table').dataTable().fnReloadAjax();
    self.getReport(self.locationFilter());
  });

  self.filteredEvents.subscribe(function() {
    app.addPoints(self.filteredEvents());
  });

  self.activeEvent = ko.observable();
  self.zoomTo = function(event, e) {

    var $table = $('#events-table').dataTable(), row,
      pos = new OpenLayers.LonLat(event.site.lon, event.site.lat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));

 
    if ($.inArray(event.feature, app.points.selectedFeatures) === -1) {
      app.selectControl.unselectAll();
      app.selectControl.select(event.feature);
    } 
    if(!event.data) {
      event.data = ko.observable(false);
      $.get('/event/view/' + event.id, function(data) {
        self.activeEvent(event);
        self.activeEvent().data(data);
      });
    } else {
      self.activeEvent(event);
    }


    if(!self.filterByExtent() && ! self.mapExtent().containsLonLat(pos)) {
      app.map.setCenter(pos);
    }

    // display the row in datatables
    row = $table.fnFindCellRowNodes(event.id, 'id')[0];
    $table.fnDisplayRow(row);
    $(row).addClass('active');
    $(row).siblings().removeClass('active');
  };

  self.report = ko.observable(init_report);
  
};

app.get_events = function () {
  $.ajax({
        url: "/events/get",
        type: 'GET',
        dataType: 'json'
  }).done(function(res) { 
    app.viewModel.addEvents(res.aaData);
    app.addPoints(app.viewModel.events());
  });
};

$.ajax({
    url: "/events/get_locations",
    type: 'GET',
    dataType: 'json'
  }).done(function (locations) {
    app.viewModel = new viewModel({
      locations: locations
    });
    // bind the viewmodel
    ko.applyBindings(app.viewModel);  
    app.viewModel.mapExtent(map.getExtent());

    $(".location").chosen();


    $(document).ready(function() {
      $(".location").chosen().change(function(event, option) {
        var $select = $(event.target),
          state,
          name;
        if(option){
          if (option.deselected) {
            state = option.deselected.split(':')[0];
            name = option.deselected.split(':')[1];
            $select.find('[value="' + name + '"]').attr('disabled', 'disabled');
              
            app.viewModel.locationFilter.remove(function(filter) {
              if (filter.type === 'county') {
                return (filter.name === name && filter.state === state);
              } else {
                return (filter.name === name);
              }
            });
              
            $select.trigger("liszt:updated");

          } else {
            app.viewModel.locationFilter.push({
              name: option.selected.split(':')[1],
              type: 'county',
              state: option.selected.split(':')[0]
            });
          }
        }
      });

      //When a state name is selected from filter box
      $('.chzn-results').on('click', '.group-result', function(event) {
        var $optgroup = $(event.target),
          name = $optgroup.text(),
          $select = $('.location'),
          $option = $select.find('[value="' + 'state:'+name + '"]'),
          index = -1,
          selected = $select.val() || [];

        $.each(app.viewModel.locationFilter(), function(i, filter) {
          if(filter.name === name) {
            index = i;
          }
        });
        if(index === -1) {
          $option.removeAttr('disabled');
          selected.push('state:'+name);
          app.viewModel.locationFilter.push({
            name: name,
            type: 'state'
          });
        } else {
          $option.attr('disabled', true);
          selected.splice($.inArray('state:'+name, selected), 1);
          app.viewModel.locationFilter.splice(index, 1);

        }
        $select.val(selected);
        $select.trigger('change');
        $select.trigger("liszt:updated");
      });
      
    });
  }).then(function () {
    app.get_events();

  });

app.addPoints = function(events) {
  app.points.removeAllFeatures();
  app.points.addFeatures($.map(events, function (event) { return event.feature; }))
};

esriOcean = new OpenLayers.Layer.XYZ("ESRI Ocean", "http://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/${z}/${y}/${x}", {
  sphericalMercator: true,
  isBaseLayer: true,
  numZoomLevels: 13,
  attribution: "Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri"
});
map.addLayers([esriOcean, app.points]);
map.setCenter(new OpenLayers.LonLat(-122.5, 41).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), 5);

app.selectControl = new OpenLayers.Control.SelectFeature(
            [app.points],
    {
        clickout: true, toggle: false,
        multiple: false, hover: false,
        toggleKey: "ctrlKey", // ctrl key removes from selection
        multipleKey: "shiftKey" // shift key adds to selection
    }
);

app.map.addControl(app.selectControl);
app.selectControl.activate();

app.points.events.on({
  "featureselected": function(e) {
    app.viewModel.zoomTo(e.feature.event);      
 },
 "featureunselected": function(e) {
   //showStatus("unselected feature " + e.feature.id + " on Vector Layer 1");
 }
 });



map.events.register("moveend", map, function() {
  app.viewModel.mapExtent(map.getExtent());
});


