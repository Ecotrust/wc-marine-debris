

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




function viewModel() {
  var self = this;

  self.events = event_json;

  self.locationFilter = ko.observableArray();

  self.locations = {};

  // populate location list for filtering
  $.each(self.events, function(i, event) {
    var state = event.site.state,
      county = event.site.county,
      counties,
      pos = new OpenLayers.LonLat(event.site.lon, event.site.lat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")),
      point = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(event.site.lon, event.site.lat));

    event.pos = pos;
    event.feature = point;
    point.event = event;
    //app.points.addFeatures(pos);
    point.geometry.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
    app.points.addFeatures(point);
    app.points.drawFeature(point);
    if(self.locations[state]) {
      counties = $.map(self.locations[state].counties, function(county) {
        return county.name;
      });
      if($.inArray(county, counties) === -1) {
        self.locations[state].counties.push({
          name: county,
          type: 'county',
          state: state
        });
      }
    } else {
      self.locations[state] = {
        counties: [{
          name: event.site.county,
          type: 'county'
        }],
        state: event.site.state
      }
    }
  });

  // store mapextent here
  self.mapExtent = ko.observable();
  self.filterByExtent = ko.observable(false);

  self.states = $.map(self.locations, function(location) {
    return {
      name: location.state,
      type: 'state'
    }
  }).sort(function(a, b) {
    {
      return a.name.localeCompare(b.name);
    }
  });


  self.showSpinner = ko.observable(false);

  self.filteredEvents = ko.computed(function() {
    var filteredEvents = [];
    self.showSpinner(true);
    $.each(self.events, function(i, event) {
      if(self.locationFilter() && self.locationFilter().length !== 0) {
        $.each(self.locationFilter(), function(i, filter) {
          if((filter.type === 'state' && filter.name === event.site.state) || (filter.type === 'county' && filter.name === event.site.county)) {
            if(self.filterByExtent()) {
              if(self.mapExtent().containsLonLat(event.pos)) {
                filteredEvents.push(event);
              }
            } else {
              filteredEvents.push(event);
            }
          }
        });
      } else {
        // no filtering
        if(self.filterByExtent()) {
          if(self.mapExtent().containsLonLat(event.pos)) {
            filteredEvents.push(event);
          }
        } else {
          filteredEvents.push(event);
        }
      }
    });
    self.showSpinner(false);
    return filteredEvents;
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


};
app.viewModel = new viewModel()

app.addPoints = function(events) {
  app.points.removeAllFeatures();
  app.points.addFeatures($.map(events, function (event) { return event.feature; }))
};

// bind the viewmodel
ko.applyBindings(app.viewModel);

// initialize the select widget
$(".location").chosen();

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

app.viewModel.mapExtent(map.getExtent());

map.events.register("moveend", map, function() {
  app.viewModel.mapExtent(map.getExtent());
});



$(document).ready(function() {
  $(".location").chosen().change(function(event, option) {
    var $select = $(event.target);
    if(option.deselected) {
      $select.find('[value="' + option.deselected + '"]').attr('disabled', 'disabled');
      app.viewModel.locationFilter.remove(function(filter) {
        return filter.name === option.deselected;
      })
      $select.trigger("liszt:updated");

    }
  });

  $('.chzn-results').on('click', '.group-result', function(event) {
    var $optgroup = $(event.target),
      name = $optgroup.text(),
      $select = $('.location'),
      $option = $select.find('[value="' + name + '"]'),
      index = -1,
      selected = $select.val() || [];

    $.each(app.viewModel.locationFilter(), function(i, filter) {
      if(filter.name === name) {
        index = i;
      }
    });
    if(index === -1) {
      $option.removeAttr('disabled');
      selected.push(name)
      app.viewModel.locationFilter.push({
        name: name,
        type: 'state'
      });
    } else {
      $option.attr('disabled', true);
      selected.splice($.inArray(name, selected), 1);
      app.viewModel.locationFilter.splice(index, 1);

    }
    $select.val(selected);
    $select.trigger("liszt:updated");

  });
  app.addPoints(app.viewModel.filteredEvents());
});