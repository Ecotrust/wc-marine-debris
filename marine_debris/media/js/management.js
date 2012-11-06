var app = {};

app.map = new OpenLayers.Map({
	//allOverlays: true,
		displayProjection: new OpenLayers.Projection("EPSG:4326"),
		projection: "EPSG:3857"
});

app.markers = new OpenLayers.Layer.Markers( "Markers" );
app.map.addLayer(app.markers);

var hybrid = new OpenLayers.Layer.Bing({
              name: "Hybrid",
              key: 'AiEF9gzhYiOfxnplJmKcY768T9GhG071ww0DizfaPFi7AnAKpBAJQ_UrHadSgDX4',
              type: "AerialWithLabels"
          });


app.map.addLayers([hybrid]);



var transactionsFixture = {
	new: [
		{
			username: "Data Wrangler",
			organization: "Surfrider",
			timestamp: "09/14/2007 10:05",
			status: 'new',
			id: 1,
			events: [{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8860},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.7153, 48.458517","lon":-122.7153,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.458517},"project":{"name":"Derelict Gear"},"date":"07/03/2010","organization":{"name":"Northwest Straits"},"id":2820},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.50355, 48.731983","lon":-122.50355,"county":"Whatcom","state":"Washington","st_initials":"WA","lat":48.731983},"project":{"name":"Derelict Gear"},"date":"05/04/2010","organization":{"name":"Northwest Straits"},"id":2817},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8858},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":2818},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.712583, 48.463183","lon":-122.712583,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.463183},"project":{"name":"Derelict Gear"},"date":"09/06/2010","organization":{"name":"Northwest Straits"},"id":2819},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4226, 47.673833","lon":-122.4226,"county":"King","state":"Washington","st_initials":"WA","lat":47.673833},"project":{"name":"Derelict Gear"},"date":"05/28/2010","organization":{"name":"Northwest Straits"},"id":2822},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4487, 48.107667","lon":-122.4487,"county":"Island","state":"Washington","st_initials":"WA","lat":48.107667},"project":{"name":"Derelict Gear"},"date":"05/13/2012","organization":{"name":"Northwest Straits"},"id":2821}]
		},
		{
			username: "Goat Man",
			organization: "Save Our Shores",
			timestamp: "09/14/2007 10:05",
			status: 'new',
			id: 2,
			events: [{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8860},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.7153, 48.458517","lon":-122.7153,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.458517},"project":{"name":"Derelict Gear"},"date":"07/03/2010","organization":{"name":"Northwest Straits"},"id":2820},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.50355, 48.731983","lon":-122.50355,"county":"Whatcom","state":"Washington","st_initials":"WA","lat":48.731983},"project":{"name":"Derelict Gear"},"date":"05/04/2010","organization":{"name":"Northwest Straits"},"id":2817},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8858},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":2818},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.712583, 48.463183","lon":-122.712583,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.463183},"project":{"name":"Derelict Gear"},"date":"09/06/2010","organization":{"name":"Northwest Straits"},"id":2819},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4226, 47.673833","lon":-122.4226,"county":"King","state":"Washington","st_initials":"WA","lat":47.673833},"project":{"name":"Derelict Gear"},"date":"05/28/2010","organization":{"name":"Northwest Straits"},"id":2822},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4487, 48.107667","lon":-122.4487,"county":"Island","state":"Washington","st_initials":"WA","lat":48.107667},"project":{"name":"Derelict Gear"},"date":"05/13/2012","organization":{"name":"Northwest Straits"},"id":2821}]

		},
		{
			username: "Data Wrangler",
			organization: "Georgia Straits",
			timestamp: "09/14/2007 10:05",
			status: 'new',
			id: 3,
			events: [{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8860},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.7153, 48.458517","lon":-122.7153,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.458517},"project":{"name":"Derelict Gear"},"date":"07/03/2010","organization":{"name":"Northwest Straits"},"id":2820},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.50355, 48.731983","lon":-122.50355,"county":"Whatcom","state":"Washington","st_initials":"WA","lat":48.731983},"project":{"name":"Derelict Gear"},"date":"05/04/2010","organization":{"name":"Northwest Straits"},"id":2817},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8858},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":2818},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.712583, 48.463183","lon":-122.712583,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.463183},"project":{"name":"Derelict Gear"},"date":"09/06/2010","organization":{"name":"Northwest Straits"},"id":2819},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4226, 47.673833","lon":-122.4226,"county":"King","state":"Washington","st_initials":"WA","lat":47.673833},"project":{"name":"Derelict Gear"},"date":"05/28/2010","organization":{"name":"Northwest Straits"},"id":2822},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4487, 48.107667","lon":-122.4487,"county":"Island","state":"Washington","st_initials":"WA","lat":48.107667},"project":{"name":"Derelict Gear"},"date":"05/13/2012","organization":{"name":"Northwest Straits"},"id":2821}]

		},
		{
			username: "Data Wrangler",
			organization: "Surfrider",
			timestamp: "09/14/2007 10:05",
			status: 'new',
			id: 4,
			events: [{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8860},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.7153, 48.458517","lon":-122.7153,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.458517},"project":{"name":"Derelict Gear"},"date":"07/03/2010","organization":{"name":"Northwest Straits"},"id":2820},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.50355, 48.731983","lon":-122.50355,"county":"Whatcom","state":"Washington","st_initials":"WA","lat":48.731983},"project":{"name":"Derelict Gear"},"date":"05/04/2010","organization":{"name":"Northwest Straits"},"id":2817},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8858},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":2818},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.712583, 48.463183","lon":-122.712583,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.463183},"project":{"name":"Derelict Gear"},"date":"09/06/2010","organization":{"name":"Northwest Straits"},"id":2819},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4226, 47.673833","lon":-122.4226,"county":"King","state":"Washington","st_initials":"WA","lat":47.673833},"project":{"name":"Derelict Gear"},"date":"05/28/2010","organization":{"name":"Northwest Straits"},"id":2822},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4487, 48.107667","lon":-122.4487,"county":"Island","state":"Washington","st_initials":"WA","lat":48.107667},"project":{"name":"Derelict Gear"},"date":"05/13/2012","organization":{"name":"Northwest Straits"},"id":2821}]

		}
	],
	accepted: [
		{
			username: "Data Wrangler",
			organization: "Surfrider",
			timestamp: "09/14/2007 10:05",
			status: 'accepted',
			id: 5,
			events: []
		},
		{
			username: "Goat Man",
			organization: "Save Our Shores",
			timestamp: "09/14/2007 10:05",
			status: 'accepted',
			id: 6,
			events: []
		},
		{
			username: "Data Wrangler",
			organization: "Georgia Straits",
			timestamp: "09/14/2007 10:05",
			status: 'accepted',
			id: 7,
			events: []
		},
		{
			username: "Data Wrangler",
			organization: "Surfrider",
			timestamp: "09/14/2007 10:05",
			status: 'accepted',
			id: 8,
			events: []
		}
	],
	rejected: [
		{
			username: "Data Wrangler",
			organization: "Surfrider",
			timestamp: "09/14/2007 10:05",
			status: 'rejected',
			id: 9,
			events: []
		},
		{
			username: "Goat Man",
			organization: "Save Our Shores",
			timestamp: "09/14/2007 10:05",
			status: 'rejected',
			id: 10,
			events: []
		},
		{
			username: "Data Wrangler",
			organization: "Georgia Straits",
			timestamp: "09/14/2007 10:05",
			status: 'rejected',
			id: 11,
			events: []
		},
		{
			username: "Data Wrangler",
			organization: "Surfrider",
			timestamp: "09/14/2007 10:05",
			status: 'rejected',
			id: 12,
			events: []
		}
	]
};
function viewModel (fixture) {
	var self = this;

	self.transactions = ko.mapping.fromJS(fixture);

	self.showError = ko.observable(false);

	self.selectEvent = function (event, e) {
		var $row = $(e.target).closest('tr');
		$row.addClass('active');
		$row.siblings().removeClass('active');
		self.showDetailsSpinner(true);

		if (event.data) {
			self.selectedEvent(event);
			self.showDetailsSpinner(false);
		} else {
			$.get('/event/view/' + event.id(), function(data) {
			  	event.data = data.fields;
			  	self.selectedEvent(event);
			  	self.showDetailsSpinner(false);
			});

		}
		  
	};


	self.updateTransaction = function (transaction, status, reason) {
		self.showTransactionSpinner(true);
		$.ajax({
			url: '/transaction/update',
			method: 'POST',
			data: {
				transaction_id: transaction.id(),
				status: status,
				reason: reason
			},
			success: function (res) {
				self.showError(res.error);
			},
			error: function (res) {
				self.transactions[transaction.status()].remove(function (item) {
					console.log(item.id() === transaction.id());
					return item.id() === transaction.id();
				});
				transaction.status(status);
				self.transactions[status].unshift(transaction);
				self.showTransactionSpinner(false);
				self.selectedTransaction(false);
			}
		});
	}

	self.rejectTransaction = function () {
		self.updateTransaction(self.selectedTransaction(), 'rejected', self.reason);
	};

	self.acceptTransaction = function () {
		self.updateTransaction(self.selectedTransaction(), 'accepted');

	};

	self.selectTransaction = function (transaction, e) {
		var $row = $(e.target).closest('tr');
		$row.addClass('active');
		$row.siblings().removeClass('active');
		self.selectedTransaction(transaction);
	};

	self.returnToTransaction = function () {
		self.selectedEvent(false);
		self.selectedTransaction(false);
		$('tr.active').removeClass('active');
	};

	self.selectedEvent = ko.observable(false);
	self.selectedTransaction =  ko.observable(false);
	self.showDetailsSpinner = ko.observable(false);
	self.showTransactionSpinner = ko.observable(false);

	self.selectedEvent.subscribe(function (event) {
		var pos = new OpenLayers.LonLat(event.site.lon(), event.site.lat()).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
		setTimeout(function () {
			app.map.render('map');			
			app.mapIsRendered = true;	
			app.map.setCenter(pos, 9);
			app.markers.clearMarkers();
			app.markers.addMarker(new OpenLayers.Marker(pos, new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png')));
		}, 0);
	});

	self.reportTableOptions = {
	  'iDisplayLength': -1,
	  'bFilter': false,
	   "sDom": '<"filter"f><"wrapper"lipt>'
	};
	self.dataTableColumns = [
		{mDataProp: 'username', sTitle: 'Username'},
		{mDataProp: 'organization', sTitle: 'Organization'},

		{mDataProp:'timestamp', sTitle: 'Timestamp'},
		{mDataProp:'status', sTitle: 'Status', bSortable: false}
	];

	self.dataTableOptions = {
		"iDisplayLength": 8
    	//"sPaginationType": "full_numbers"
    };

	
};

ko.applyBindings(new viewModel(transactionsFixture));
