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
			type: 'POST',
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