

var app = {}, map = new OpenLayers.Map('map', {
  //allOverlays: true,
  displayProjection: new OpenLayers.Projection("EPSG:4326"),
  projection: "EPSG:3857"
});

app.maxZoom = 12;

app.map = map;
app.rowIndex = {};

OpenLayers.Strategy.AttributeCluster = OpenLayers.Class(OpenLayers.Strategy.Cluster, {
    /**
     * the attribute to use for comparison
     */
    attribute: null,
    /**
     * Method: shouldCluster
     * Determine whether to include a feature in a given cluster.
     *
     * Parameters:
     * cluster - {<OpenLayers.Feature.Vector>} A cluster.
     * feature - {<OpenLayers.Feature.Vector>} A feature.
     *
     * Returns:
     * {Boolean} The feature should be included in the cluster.
     */
    shouldCluster: function(cluster, feature) {
        var cc_attrval = cluster.cluster[0].attributes[this.attribute];
        var fc_attrval = feature.attributes[this.attribute];
        var superProto = OpenLayers.Strategy.Cluster.prototype;
        return cc_attrval === fc_attrval && 
               superProto.shouldCluster.apply(this, arguments);
    },
    CLASS_NAME: "OpenLayers.Strategy.AttributeCluster"
});

function viewModel(options) {
  var self = this;

  self.events = ko.observableArray();
  self.states = options.locations.states;
  self.locations = options.locations.locations;

  self.queryFilter = ko.observableArray();
  self.fromDate = ko.observable();
  self.toDate = ko.observable();
  
  self.fromDate.subscribe(function (date) {
    $( "#to" ).datepicker( "option", "minDate", date );
    self.queryFilter.remove(function (item) {
      return item.name === 'toDate';
    });
    self.queryFilter.push({
      type: 'date',
      name: 'toDate',
      value: new Date(date).toString('yyyy-MM-dd')
    });
  });

  self.toDate.subscribe(function (date) {
    $( "#from" ).datepicker( "option", "maxDate", date );
    self.queryFilter.remove(function (item) {
      return item.name === 'fromDate';
    });
    self.queryFilter.push({
      type: 'date',
      name: 'fromDate',
      value: new Date(date).toString('yyyy-MM-dd')
    });
  });

  self.removeDate = function (self, event) {
  $(event.target).closest('.input-append').find('input').datepicker( "setDate", null ).trigger('change');

  };

  self.activeFilterTypes = ko.computed(function (type) {
    return $.map(self.queryFilter(), function (filter) { return filter.type });
  });

  // optikons for the right hand tables
  self.reportTableOptions = {
    'iDisplayLength': -1,
     "sDom": '<"filter"f><"wrapper"lipt>'
  };

  self.dataTablesOptions = {
    'bFilter': false, 
    "iDisplayLength": 8,
    "bProcessing": true,
    "bServerSide": true,
    "sPaginationType": "full_numbers",
    "sAjaxSource": "/events/get",
    "iDisplayStart": 0,
    "fnServerParams": function ( aoData ) {
      var filters = self.queryFilter();
      if (self.startID) {
        console.log(self.startID);
        aoData.push({ "name": "startID", "value": self.startID });
        self.startID = null;
      }
      // if (self.mapExtent()) {
        // filters.push({"type": "bbox", "bbox": self.mapExtent().transform(new OpenLayers.Projection("EPSG:900913"), new OpenLayers.Projection("EPSG:4326")).toBBOX() });
      // }
      aoData.push( { "name": "filter", "value": JSON.stringify(filters) });
    }
  };

  // populate points
  self.addEvents = function (events) {
    self.events([]);
    $.each(events, function(i, event) {
      var state = event.site.state,
        pos = new OpenLayers.LonLat(event.site.lon, event.site.lat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")),
        point = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(event.site.lon, event.site.lat));
      event.feature = point;
      point.event = event;
      point.attributes = event;
      point.attributes.event_type = event.datasheet.event_type;
      point.geometry.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
      self.events().push(event);
    });
  };

  // store mapextent here
  self.mapExtent = ko.observable();
  self.filterByExtent = ko.observable(false);

  self.showSpinner = ko.observable(false);
  self.showReportSpinner = ko.observable(false);
  self.mapIsLoading = ko.observable(true);
  self.showDetailsSpinner = ko.observable(false);
  self.filteredEvents = ko.computed(function() {
    self.showSpinner(false);
    return self.events();
  });
  
  self.getReport = function (filters) {
    self.showReportSpinner(true);
    $('#report').hide();
    $.ajax({
        url: "/events/get_values",
        type: 'GET',
        data: {
            "filters" : JSON.stringify(filters || [])
        },
        dataType: 'json'
    }).done(function(report) { 
        var mapping = {
            'Number_volunteers_beach': 'Volunteers',
            'Pounds_trash_beach': 'Lbs of trash',
            'Cleanup_distance_beach': 'Miles cleaned'
        };
        report.event_values = $.map(report, function(field) {
            if ($.inArray(field.field.name, [
                'Number_volunteers_beach',
                'Pounds_trash_beach',
                'Cleanup_distance_beach'
            ]) !== -1){
                field.field.display_name = mapping[field.field.name];
                return field;
            }
        });
        self.report(report);
        self.showReportSpinner(false);
        $("#report").show();
    });
  };
  $("#report-tab").on('shown', function(event) {
    self.getReport(self.queryFilter());
  });

  self.queryFilter.subscribe(function () {
    self.mapIsLoading(true);
    $('#events-table').dataTable().fnReloadAjax();
    app.points.refresh({ 
        params: {
            'filter': JSON.stringify(self.queryFilter())
        }
    });
    
    if ($("#report").is(":visible")){
        self.getReport(self.queryFilter());
    }
  });

  self.filteredEvents.subscribe(function() {
    app.addPoints(self.filteredEvents());
  });

  self.activeEvent = ko.observable();

  self.startID = null;

  // if you click on a cluster with multiple events
  self.clusteredEvents = ko.observableArray();
  self.selectedClusterEvent = ko.observable();

  self.selectedClusterEvent.subscribe(function (event) {
    if (event) {
        self.zoomTo(null, event);      
    } else {
      self.activeEvent(false);
    }
  });

  self.handleTableClick = function (event, e) {
    var $row = $(e.target).closest('tr'),
       pos = new OpenLayers.LonLat(event.site.lon, event.site.lat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
    $row.siblings().removeClass('active');
    $row.addClass('active');
    self.zoomTo(null, event);
    app.map.setCenter(pos, app.map.getZoom() + 2);
  };

  self.zoomTo = function(feature, event) {
    var $table = $('#events-table').dataTable(), row;

    if (! event) {
      event = {
        id: feature.cluster[0].attributes.id,
        data: false
      };
    }
    
      // feature = app.points.getFeaturesByAttribute('id', event.id)[0],
      // pos = new OpenLayers.LonLat(event.site.lon, event.site.lat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
    // if (! self.mapIsLoading() && $.inArray(feature, app.points.selectedFeatures) === -1 &&  ( $.browser.msie === undefined || $.browser.version >= 9)) {
      // app.selectControl.unselectAll();
      // app.selectControl.select(feature);
    // } 
    event.data = ko.observable(false);
    self.showDetailsSpinner(true);
    $.get('/event/view/' + event.id, function(data) {
      var event_details = data.details;
      event_details.data = data.fields;
      self.activeEvent(event_details);
      self.showDetailsSpinner(false);
    });
      
    $(row).addClass('active');
    $(row).siblings().removeClass('active');
  };

  self.report = ko.observable();

}


app.get_event_points = function(filters) {
  if ( $.browser.msie === undefined || $.browser.version >= 9) {
    $('#map').addClass('fade');
    app.viewModel.mapIsLoading(true);
    $.ajax({
          url: "/events/get",
          type: 'GET',
          data: {
              "filter" : JSON.stringify(filters)
          },
          dataType: 'json'
    }).done(function(res) { 
      app.viewModel.addEvents(res.aaData);
      app.addPoints(app.viewModel.events());
      $('#map').removeClass('fade');
      app.viewModel.mapIsLoading(false);

    });  
  }
};

app.get_events = function () {
  if ( $.browser.msie === undefined || $.browser.version >= 9) {
    $('#map').addClass('fade');
    app.viewModel.mapIsLoading(true);
    $.ajax({
          url: "/events/get",
          type: 'GET',
          dataType: 'json'
    }).done(function(res) { 
      app.viewModel.addEvents(res.aaData);
      app.addPoints(app.viewModel.events());
      $('#map').removeClass('fade');
      app.viewModel.mapIsLoading(false);

    });    
  }

};
// var onResize = function () {
//   $(".wcga-database").height(Math.max($(".wcga-database-left").height(), $(".wcga-database-right").height()));

// };
// onResize();
// $(document).on('resize', onResize);

$.ajax({
    url: "/events/get_filters",
    type: 'GET',
    dataType: 'json'
  }).done(function (locations) {
    app.viewModel = new viewModel({
      locations: locations
    });
    // bind the viewmodel
    ko.applyBindings(app.viewModel);

    app.viewModel.mapExtent(map.getExtent());

    $("select.location").chosen();
    $("select.type").val([]);
    $("select.type").chosen();
    $(".filters").removeClass('hide');
    $(document).ready(function() {
      $("select.type").val([]);


      $("select.type").chosen().change(function (event, option ) {
        if (option.selected) {
          app.viewModel.queryFilter.push({
            type: "event_type",
            name: option.selected
          });
        } else if (option.deselected) {
          app.viewModel.queryFilter.remove(function (filter) {
            return filter.type === 'event_type' && filter.name === option.deselected;
          });
        }
        
      });
      $(".location").chosen().change(function(event, option) {
        var $select = $(event.target),
          state,
          name;
        if(option){
          if (option.deselected) {
            state = option.deselected.split(':')[0];
            name = option.deselected.split(':')[1];
            $select.find('[value="' + name + '"]').attr('disabled', 'disabled');
              
            app.viewModel.queryFilter.remove(function(filter) {
              if (filter.type === 'county') {
                return (filter.name === name && filter.state === state);
              } else {
                return (filter.name === name);
              }
            });
              
            $select.trigger("liszt:updated");
          } else {
            app.viewModel.queryFilter.push({
              name: option.selected.split(':')[1],
              type: 'county',
              state: option.selected.split(':')[0]
            });
          }
        }
      });

      $(".location").find("optgroup").each(function () {
        var $optgroup = $(this), name = $optgroup.attr('label');
        $option = $("<option>", { "value": "state:" + name, "text": name, "class": "dummy-state" });
        $optgroup.append($option.hide());
      });
      $(".location").trigger("liszt:updated");
      //When a state name is selected from filter box
      $('.chzn-results').on('click', '.group-result', function(event) {
        var $optgroup = $(event.target),
          name = $optgroup.text(),
          $select = $('.location'),
          $option = $select.find('[value="' + 'state:'+name + '"]'),
          index = -1,
          selected = $select.val() || [];

        $.each(app.viewModel.queryFilter(), function(i, filter) {
          if(filter.name === name) {
            index = i;
          }
        });
        if(index === -1) {
          // $optgroup.append($option);
          $select.trigger("liszt:updated");
          selected.push('state:'+name);
          app.viewModel.queryFilter.push({
            name: name,
            type: 'state'
          });
        } else {
          // $optgroup.remove($option);
          selected.splice($.inArray('state:'+name, selected), 1);
          app.viewModel.queryFilter.splice(index, 1);

        }
        $select.val(selected);
        $select.trigger('change');
        $select.trigger("liszt:updated");
      });
      
    });
  }).then(function () {
    //Do nothing for now
  app.map.addLayer(app.points);
  app.map.raiseLayer(app.points, 2);

  });

app.addPoints = function(events) {
  app.points.removeAllFeatures();
  app.points.addFeatures($.map(events, function (event) { return event.feature; }))  ;
};

// esriOcean = new OpenLayers.Layer.XYZ("ESRI Ocean", "http://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/${z}/${y}/${x}", {
//   sphericalMercator: true,
//   isBaseLayer: true,
//   numZoomLevels: app.maxZoom+1,
//   attribution: "Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri"
// });
app.points = new OpenLayers.Layer.Vector("Events", {
  renderers: OpenLayers.Layer.Vector.prototype.renderers,
  projection: "EPSG:4326",
  strategies:[
    new OpenLayers.Strategy.Fixed(),
    new OpenLayers.Strategy.AttributeCluster({
      attribute:'event_type'
    })
  ],
  protocol: new OpenLayers.Protocol.HTTP({
    url: "/events/get_geojson",
    format: new OpenLayers.Format.GeoJSON()

  }),
  styleMap: new OpenLayers.StyleMap({
    "default": new OpenLayers.Style({
      pointRadius: "${radius}",
      fillColor: "${getColor}",
      fillOpacity: 0.8,
      strokeColor: "${getStrokeColor}",
      strokeWidth: 2,
      strokeOpacity: 0.8,
      label: "${clusterCount}",
      fontColor: "#333"
    },{ 
      // Rules go here.
      context: {
        radius: function(feature) {
          return Math.min(feature.attributes.count, 7) + 5;
        },
        clusterCount: function (feature) {
          return feature.attributes.count > 1 ? feature.attributes.count: "";
        },
        getColor: function(feature) {
          var type = feature.cluster[0].attributes.event_type;
          return type === "Site Cleanup" ? "#ffcc66" : "#ccc";
        },
        getStrokeColor: function(feature) {
            var type = feature.cluster[0].attributes.event_type;
            return type === "Site Cleanup" ? "#cc6633" : "#333";

         }
      }
    }),
    "select": {
      fillColor: "#8aeeef",
      strokeColor: "#32a8a9"
    }
  })
});

var hybrid = new OpenLayers.Layer.Bing({
              name: "Hybrid",
              key: 'AiEF9gzhYiOfxnplJmKcY768T9GhG071ww0DizfaPFi7AnAKpBAJQ_UrHadSgDX4',
              type: "AerialWithLabels"
          });


map.addLayers([hybrid]);
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
  "featuresadded": function () {
    app.viewModel.mapIsLoading(false);
  },
  "featuresremoved": function () {
    app.viewModel.mapIsLoading(false);
  },
  "refresh": function () {
    app.viewModel.mapIsLoading(false);
  },

  "featureselected": function(e) {
    var bounds;

    $("#events-table").find('tr.active').removeClass('active');

    if ( e.feature.attributes.count === 1){
        app.viewModel.clusteredEvents.removeAll();
        app.viewModel.zoomTo(e.feature);
    } else {
        app.viewModel.activeEvent(false);
        app.viewModel.clusteredEvents($.map(e.feature.cluster, function (f) {
          return f.attributes;
        }));
        
        app.map.setCenter(e.feature.geometry.bounds.centerLonLat, app.map.getZoom() + 2);
        
        
    }
 },
 "featureunselected": function(e) {
   //showStatus("unselected feature " + e.feature.id + " on Vector Layer 1");
 }
 });
$(document).resize(function () {
  var $table = $('#events-table');
  $table.css({ width: $(oTable).parent().width() });
  $table.dataType().fnAdjustColumnSizing();  
});
 
// map.events.register("moveend", map, function() {
  // app.viewModel.mapExtent(map.getExtent());
// });


