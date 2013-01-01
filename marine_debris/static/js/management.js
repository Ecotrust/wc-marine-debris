var app = {};

app.map = new OpenLayers.Map({
	//allOverlays: true,
		displayProjection: new OpenLayers.Projection("EPSG:4326"),
		projection: "EPSG:3857"
});
app.map.updateSize = $.noop;
app.markers = new OpenLayers.Layer.Markers( "Markers" );
app.map.addLayer(app.markers);

var hybrid = new OpenLayers.Layer.Bing({
              name: "Hybrid",
              key: 'AiEF9gzhYiOfxnplJmKcY768T9GhG071ww0DizfaPFi7AnAKpBAJQ_UrHadSgDX4',
              type: "AerialWithLabels"
          });


app.map.addLayers([hybrid]);

function viewModel (fixture) {
	var self = this;
	
	self.transactions = ko.mapping.fromJS(fixture);
	
	self.showError = ko.observable(false);

	self.selectEvent = function (event, e) {
		var $row = $(e.target).closest('tr');
		$('tr.active').removeClass('active');
		$row.addClass('active');
		
		self.showDetailsSpinner(true);
		self.selectedSite(false);
		if (event.data) {
			self.selectedEvent(event);
			self.showDetailsSpinner(false);
		} else {
			$.get('/event/view/' + event.id, function(data) {
			  	event.data = data.fields;
			  	self.selectedEvent(event);
			  	self.showDetailsSpinner(false);
			});
		}
		  
	};
    
    self.selectSite = function (site, e) {
		var $row = $(e.target).closest('tr');
		$('tr.active').removeClass('active');
		$row.addClass('active');
		
		self.showDetailsSpinner(true);
		self.selectedEvent(false);
		if (!site.data) {
            site.data = {
                "details": {
                    "sitename": site.name,
                    "state": site.state,
                    "county": site.county
                }
            }
		}
        self.selectedSite(site);
        self.showDetailsSpinner(false);
	};

	self.updateTransaction = function (transaction, status, reason) {
		self.showTransactionSpinner(true);
		$.ajax({
			url: '/transaction/update',
			type: 'POST',
			data: {
				transaction_id: transaction.id(),
				status: status,
				reason: reason,
				csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
			},
			success: function (res) {
				self.transactions[transaction.status()].remove(function (item) {
					return item.id() === transaction.id();
				});
				transaction.status(status);
				if (reason) {
					transaction.reason(reason);
				}
				self.transactions[status].unshift(transaction);
				self.showTransactionSpinner(false);
				self.selectedTransaction(false);

			},
			error: function (res) {
				self.showError(res.error);
			}
		});
	}

	self.rejectTransactionModal = function () {
		self.reason(null);
		$('#reason-modal').modal('show');
		
	};
	self.rejectTransaction = function () {
		self.updateTransaction(self.selectedTransaction(), 'rejected', self.reason());
		$('#reason-modal').modal('hide');
	};

	self.acceptTransaction = function () {
        var dependencies_met = true;
        if (self.selectedTransaction().site_dependencies().length > 0){
            for (i = 0; i < self.selectedTransaction().site_dependencies().length; i++){
                if ($.inArray(self.selectedTransaction().site_dependencies()[i], self.accepted_transactions()) < 0) {
                    dependencies_met = false;
                }
            }
        }
        if (self.selectedTransaction().site_dependencies().length === 0 || dependencies_met) {
            self.accepted_transactions().push(self.selectedTransaction().id()) 
            self.updateTransaction(self.selectedTransaction(), 'accepted');
        } else {
            self.dependency_text(self.selectedTransaction().site_dependencies().toString())
            $('#dependence-modal').modal('show');
        }
	};

	self.selectTransaction = function (transaction, e) {
		var $row = $(e.target).closest('tr');
		$row.addClass('active');
		$row.siblings().removeClass('active');
        self.showEvents(transaction.events_count())
        self.showSites(transaction.sites_count())
		self.selectedTransaction(transaction);
	};

	self.returnToTransaction = function () {
		self.selectedEvent(false);
		self.selectedSite(false);
		self.selectedTransaction(false);
		$('tr.active').removeClass('active');
	};

	self.selectedEvent = ko.observable(false);
	self.selectedSite = ko.observable(false);
	self.selectedTransaction =  ko.observable(false);
	self.showDetailsSpinner = ko.observable(false);
	self.showTransactionSpinner = ko.observable(false);

	// observable to hold reason for rejecting
	self.reason = ko.observable();
    
    self.dependency_text = ko.observable();
    self.accepted_transactions = ko.observableArray([]);
    self.showSites = ko.observable(null);
    self.showEvents = ko.observable(null);

	self.selectedEvent.subscribe(function (event) {
		if (event) {
			var pos = new OpenLayers.LonLat(
				event.site.lon, 
				event.site.lat).transform(
					new OpenLayers.Projection("EPSG:4326"),
					new OpenLayers.Projection("EPSG:900913"));

			setTimeout(function () {
				app.map.render('map');			
				app.mapIsRendered = true;	
				app.map.setCenter(pos, 9);
				app.markers.clearMarkers();
				app.markers.addMarker(new OpenLayers.Marker(pos, new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png')));
			}, 0);	
		}
	});
    
    self.selectedSite.subscribe(function (site) {
		if (site) {
			var pos = new OpenLayers.LonLat(
				site.lon, 
				site.lat).transform(
					new OpenLayers.Projection("EPSG:4326"),
					new OpenLayers.Projection("EPSG:900913"));

			setTimeout(function () {
				app.map.render('map');			
				app.mapIsRendered = true;	
				app.map.setCenter(pos, 9);
				app.markers.clearMarkers();
				app.markers.addMarker(new OpenLayers.Marker(pos, new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png')));
			}, 0);	
		}
	});

	self.reportTableOptions = {
	  'iDisplayLength': -1,
	  'bFilter': false,
	   "sDom": '<"filter"f><"wrapper"lipt>'
	};
    
    self.categoryTableOptions = {
      'bFilter': false, 
      'iDisplayLength': -1,
      "bSort": false,
       "sDom": '<"filter"f><"wrapper"lipt>'
    };
    
	self.dataTableColumns = [
		{mDataProp: 'id', sTitle: 'Id'},
		{mDataProp: 'username', sTitle: 'User'},
		{mDataProp:'timestamp', sTitle: 'Time'},
        {mDataProp:'sites_count', sTitle: 'Sites Count'},
		{mDataProp:'events_count', sTitle: 'Events Count'},
		{mDataProp:'status', sTitle: 'Status', bSortable: false}
	];

	self.eventTableOptions = {
		"iDisplayLength": 5,
		"bProcessing": true,
		"bServerSide": true,
		"sPaginationType": "full_numbers",
		"sAjaxSource": "/events/get",
		"iDisplayStart": 0,
		"fnServerParams": function ( aoData ) {
			aoData.push({
				name: "filter",
				value: JSON.stringify([{
					type: "transaction", 
					value: self.selectedTransaction().id()
				}])
			});
		}
	};
    
    self.siteTableOptions = {
		"iDisplayLength": 5,
		"bProcessing": true,
		"bServerSide": true,
		"sPaginationType": "full_numbers",
		"sAjaxSource": "/sites/get",
		"iDisplayStart": 0,
		"fnServerParams": function ( aoData ) {
			aoData.push({
				name: "transaction",
				value: self.selectedTransaction().id()
			});
		}
	};

	self.dataTableOptions = {
    	"sPaginationType": "full_numbers"
    };

	
};

$('#reason-modal').on('shown', function () {
  $(this).find('textarea').focus();
});

$.ajax({
	url: '/get_transactions',
	dataType: 'json',
	success: function (transactions) {
		ko.applyBindings(new viewModel(transactions));		
	}
})


