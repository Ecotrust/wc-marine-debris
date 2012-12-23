

var app = {}, map = new OpenLayers.Map('map', {
  //allOverlays: true,
  displayProjection: new OpenLayers.Projection("EPSG:4326"),
  projection: "EPSG:3857"
});

app.maxZoom = 12;

app.map = map;
app.rowIndex = {};
app.highlightedCluster = null;
app.highlightedEvent = null;
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
  self.states = options.filters.states;
  self.locations = options.filters.locations;
  self.fields = options.filters.fields;

  self.organizations = options.filters.organizations;
  self.projects = options.filters.projects;

  self.queryFilter = ko.observableArray();
  self.fromDate = ko.observable();
  self.toDate = ko.observable();
  
  self.fromDate.subscribe(function (date) {
    $( "#to" ).datepicker( "option", "minDate", date );
    self.queryFilter.remove(function (item) {
      return item.type === 'toDate';
    });
    if (date) {
      self.queryFilter.push({
        type: 'toDate',
        value: new Date(date).toString('yyyy-MM-dd')
      });
    }
    
  });

  self.toDate.subscribe(function (date) {
    $( "#from" ).datepicker( "option", "maxDate", date );
    self.queryFilter.remove(function (item) {
      return item.type === 'fromDate';
    });
    if (date) {
      self.queryFilter.push({
        type: 'fromDate',
        value: new Date(date).toString('yyyy-MM-dd')
      });  
    }
    
  });

  self.removeDate = function (self, event) {
    $(event.target).closest('.input-append')
      .find('input')
      .datepicker( "setDate", null )
      .trigger('change');
  };

  self.activeFilterTypes = ko.computed(function (type) {
    var filterSet={}, filterList=[];
    if (self.queryFilter().length) {
      $.each(self.queryFilter(), function (i, filter) { 
        if (filter.type !== 'point' && filter.type !== 'report') {
          filterSet[filter.type] = true;
        }
      });
      $.each(filterSet, function (key, x) {
        filterList.push(key);
      });  
    }
    
    return filterList;
  });

  // optikons for the right hand tables
  self.reportTableOptions = {
    'iDisplayLength': -1,
    "bSort": false,
     "sDom": '<"filter"f><"wrapper"lipt>'
  };
  
  self.categoryTableOptions = {
    'bFilter': false, 
    'iDisplayLength': -1,
    "bSort": false,
     "sDom": '<"filter"f><"wrapper"lipt>'
  };

  self.dataTablesOptions = {
    'bFilter': false, 
    "iDisplayLength": 5,
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
  
  self.downloadData = function () {
    var filters = self.queryFilter();
    var url = "/events/download.csv?pprint=True&filter=" + JSON.stringify(filters || []);
    $('iframe#download-frame').attr('src', url);
  };

  self.showReport = function () {
    $("#report-tab").tab('show');  
    //self.getReport(self.queryFilter());
  };

  self.showMap = function () {
    self.showDetailsSpinner(true);
    $("#map-tab").tab('show');  
  };

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
        report.event_values = $.map(report.fields, function(field) {
            if ($.inArray(field.name, [
                'Number_volunteers_beach',
                'Pounds_trash_beach',
                'Cleanup_distance_beach'
            ]) !== -1){
                field.display_name = mapping[field.name];
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

  self.url = ko.computed(function () {
    var filters = {}, filterList = [];
    $.each(self.queryFilter(), function (i, filter) {
      var value = filter.value;
      if (filter.type === 'county') {
        value = filter.state + ':' + value;
      }
      if (filters[filter.type]) {
        filters[filter.type] = filters[filter.type] + ',' + value; 
      } else {
        filters[filter.type] = value;
      }
    });
    $.each(filters, function (type, value) {
      filterList.push(type + '=' + value.replace(/ /g, '+'));
    });
    return filterList.join('&');
  });

  self.url.subscribe(function (url) {
    window.location.hash = url;
  });

  self.queryDisplay = ko.computed(function () {
    var display = {};
    $.each(self.queryFilter(), function (i, filter) {
      var text = filter.value;
      if (filter.state) {
        text = text + ", " + filter.state;
      }
      if (display[filter.type]) { 
        display[filter.type] = [display[filter.type], filter.value].join(", ");
      } else {
        display[filter.type] = text;
      }
    });
    return display;
  });


  self.queryFilter.subscribe(function (newFilter) {
    var getPoints = true;
    
    app.highlightedEvent = null;
    app.highlightedCluster = null;
    self.report(false);
    $('#events-table').dataTable().fnReloadAjax();
    
    // points not exist at first
    // $.each(newFilter, function (i, filter) {
    //   if (filter.type === 'point') {
    //     getPoints = false;
    //   }
    // });
    // if (newFilter.length === 0) {
    //   getPoints = false;
    // }

    if (app.points && getPoints) {
      self.mapIsLoading(true);
      app.points.refresh({ 
          params: {
              'filter': JSON.stringify(self.queryFilter())
          }
      });
      self.mapIsLoading(false);  
    } 

    
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

  self.report = ko.observable();

  self.clearFilters = function () {
    self.queryFilter.removeAll();
  };

  self.selectedClusterEvent.subscribe(function (event) {
    if (event) {
        self.showDetail(event, false);      
    } else {
      self.activeEvent(false);
    }
  });

  self.highlightCluster = function (event) {

    
    for (var i = 0; i < app.points.features.length; i++) {
      var cluster = app.points.features[i].cluster;
      for (var j=0; j < cluster.length; j++) {
        if (cluster[j].attributes.id === event.id) {
          var selectedCluster = app.points.features[i];
        }
      }
    }

    if (app.highlightedCluster !== selectedCluster) {
      console.log('highlighting');
      if (app.highlightedCluster) {
        app.selectControl.unhighlight(app.highlightedCluster);  
      }
      if (selectedCluster) {
        app.selectControl.highlight(selectedCluster);

        app.highlightedCluster = selectedCluster;
        app.highlightedEvent = event;  
      }  
    }  
  
  };

  self.handleTableClick = function (event, e) {
    
    var selectedCluster, $row = $(e.target).closest('tr'),
       pos = new OpenLayers.LonLat(event.site.lon, event.site.lat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
    $row.siblings().removeClass('active');
    $row.addClass('active');
    self.highlightCluster(event);
    
    self.showDetail(event, true);
    //app.map.setCenter(pos, app.map.getZoom() + 2);
  };

  self.zoomTo = function (event, e) {
    
    var zoomLevel = Math.max(12, app.map.getZoom()), $row = $(e.target).closest('tr');
    $row.siblings().removeClass('active');
    $row.addClass('active');
    app.highlightedEvent = event;
    //self.showDetail(event);
    //$('a[href=#map-content]').tab('show');
    if (typeof event.site !== 'undefined') {
      app.map.setCenter(new OpenLayers.LonLat(event.site.lon, event.site.lat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), zoomLevel);  
    } else {
      app.map.setCenter(event.geometry.x, event.geometry.y);
    }
    
    
  };

  self.showDetail = function(event, showDetail) {
    event.data = ko.observable(false);
    self.showDetailsSpinner(true);
    $.get('/event/view/' + event.id, function(data) {
      var event_details = data.details;
      event_details.data = data.fields;
      self.activeEvent(event_details);
      self.showDetailsSpinner(false);
      if (showDetail) {
        $('a[href=#event-details-content]').tab('show');    
      }
      
      
      
    });
      
  };

  

}



app.loadHash = function (hash) {
  var filters = {}, filterList = [];
  if (hash) {
    filterList = hash.split("&");
  }
  $.each(filterList, function (i, filter) {
    var parts = filter.split('='),
        type = parts[0],
        values = parts[1].replace(/\+/, ' ').split(','), firstFilter=true;
        
        // open the first tab
        if (firstFilter && type !== 'report' ) {
          $('.' + type).tab('show');
          firstFilter = false;
        }

        if (type === 'report') {
          $('#report-tab').tab('show');
        }

        // update the select fields
        $('select.' + type).val(values);

        // unpack the query filter
        $.each(values, function (i, value) {
          var valueParts = value.split(':')

          if (type === 'toDate' || type === 'fromDate') {
             $(document.getElementById(type)).datepicker( "setDate", value );
             app.viewModel.queryFilter.push({
               type: type,
               value: value
             });
          }
          // counties are a special case
          else if (type === 'county') {
            app.viewModel.queryFilter.push({
              type: type,
              value: valueParts[1],
              state: valueParts[0]
            });    
          } else {
            app.viewModel.queryFilter.push({
              type: type,
              value: value
            });    
          }
        });
  });
};

$.ajax({
    url: "/events/get_filters",
    type: 'GET',
    dataType: 'json'
  }).done(function (filters) {
    app.viewModel = new viewModel({
      filters: filters
    });
    // bind the viewmodel
    ko.applyBindings(app.viewModel);

    // load app state from url
    app.loadHash(window.location.hash.replace('#', ''));

  
    app.viewModel.mapExtent(map.getExtent());

    
    $(".filters").removeClass('hide');
    $(document).ready(function() {

      $('#map-tab').on('shown', function (e) {
        app.viewModel.showDetailsSpinner(false);
      })

      $("select.organization").chosen().change(function (event, option) {
        if (option.selected) {
          app.viewModel.queryFilter.push({
            type: "organization",
            value: option.selected
          });
        } else if (option.deselected) {
          app.viewModel.queryFilter.remove(function (filter) {
            return filter.type === 'organization' && filter.value === option.deselected;
          });
        }
      });

      $("select.field").chosen().change(function (event, option) {
        if (option.selected) {
          app.viewModel.queryFilter.push({
            type: "field",
            value: option.selected
          });
        } else if (option.deselected) {
          app.viewModel.queryFilter.remove(function (filter) {
            return filter.type === 'field' && filter.value === option.deselected;
          });
        }
      });

      $("select.project").chosen().change(function (event, option) {
        if (option.selected) {
          app.viewModel.queryFilter.push({
            type: "project",
            value: option.selected
          });
        } else if (option.deselected) {
          app.viewModel.queryFilter.remove(function (filter) {
            return filter.type === 'project' && filter.value === option.deselected;
          });
        }
      });
      

      $("select.event_type").chosen().change(function (event, option ) {
        if (option.selected) {
          app.viewModel.queryFilter.push({
            type: "event_type",
            value: option.selected
          });
        } else if (option.deselected) {
          app.viewModel.queryFilter.remove(function (filter) {
            return filter.type === 'event_type' && filter.value === option.deselected;
          });
        }
        
      });

      $("select.state").chosen().change(function (event, option ) {
        if (option.selected) {
          app.viewModel.queryFilter.push({
            type: "state",
            value: option.selected
          });
        } else if (option.deselected) {
          app.viewModel.queryFilter.remove(function (filter) {
            return filter.type === 'state' && filter.value === option.deselected;
          });
        }
        
      });
      $("select.county").chosen().change(function (event, option ) {
        var state, county;
        if (option.selected) {
          state = option.selected.split(':')[0];
          county = option.selected.split(':')[1];
          app.viewModel.queryFilter.push({
            type: "county",
            value: county,
            state: state
          });
        } else if (option.deselected) {
          state = option.deselected.split(':')[0];
          county = option.deselected.split(':')[1];
          app.viewModel.queryFilter.remove(function (filter) {
            return filter.type === 'county' && filter.value === county && filter.state === state  ;
          });
        }
      });
    });

  }).then(function () {
    //Do nothing for now
  app.initMap();
  app.map.addLayer(app.points);
  app.map.raiseLayer(app.points, 2);

  });



app.initMap = function () {
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
      format: new OpenLayers.Format.GeoJSON(),
      params: {
          'filter': JSON.stringify(app.viewModel.queryFilter())
        }
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

  var mProj = new OpenLayers.Projection("EPSG:4326"),
      gProj = new OpenLayers.Projection("EPSG:900913");

  map.addLayers([hybrid]);
  map.setCenter(new OpenLayers.LonLat(-122.5, 41).transform(mProj, gProj), 5);

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

  app.map.events.on({
    "moveend": function () {
    
      if (app.highlightedEvent) {
        app.viewModel.highlightCluster(app.highlightedEvent);
        //app.highlightedEvent = null;
      }
    
    }
  })

  app.points.events.on({
    "featuresadded": function () {
      app.viewModel.mapIsLoading(false);

    },
    "featuresremoved": function () {
      app.viewModel.mapIsLoading(false);
    },
    "refresh": function () {
      app.viewModel.mapIsLoading(false);
      app.viewModel.clusteredEvents(false);
    },
    "featureselected": function(e) {
      var centerLonLat = e.feature.geometry.bounds.centerLonLat,
          centroid = e.feature.geometry.transform(gProj, mProj).getCentroid();

      app.viewModel.queryFilter.remove(function (item) {
        return item.type === 'point';
      });
      
      app.viewModel.queryFilter.push({
        type: 'point',
        value: [centroid.x.toFixed(4), centroid.y.toFixed(4)].join(':')
      });
      if ( e.feature.attributes.count === 1){
        if (app.viewModel.clusteredEvents()) {
          app.viewModel.clusteredEvents.removeAll();
        }
         app.viewModel.showDetail(e.feature.cluster[0].attributes, false);
        setTimeout(function () {
          $("#events-table").find('tbody tr:first').addClass('active');
        }, 500);

      } else {
        
         app.viewModel.activeEvent(false);
         
         app.map.setCenter(centerLonLat, app.map.getZoom() + 2);
          
         if (e.feature.cluster.length < 100) {
          app.viewModel.clusteredEvents($.map(e.feature.cluster, function (f) {
            return f.attributes;
          })); 
         }
         
         
      }
      if (app.viewModel.highlightedCluster) {
        app.selectControl.unhighlight(app.viewModel.highlightedCluster);
      }
      


      
   },
   "featureunselected": function(e) {
     //showStatus("unselected feature " + e.feature.id + " on Vector Layer 1");
   }
   });  
}

$(document).resize(function () {
  var $table = $('#events-table');
  $table.css({ width: $(oTable).parent().width() });
  $table.dataType().fnAdjustColumnSizing();  
});
 
// map.events.register("moveend", map, function() {
  // app.viewModel.mapExtent(map.getExtent());
// });


