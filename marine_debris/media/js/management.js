
function viewModel () {
	var self = this;

	self.selectTransaction = function (transaction, event) {
		$(event.target).closest('tr').addClass('active');
		self.selectedTransaction(transaction);
	};

	self.selectedTransaction =  ko.observable(false);

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

	self.transactions = {
		new: [
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'new',
				events: [{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8860},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.7153, 48.458517","lon":-122.7153,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.458517},"project":{"name":"Derelict Gear"},"date":"07/03/2010","organization":{"name":"Northwest Straits"},"id":2820},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.50355, 48.731983","lon":-122.50355,"county":"Whatcom","state":"Washington","st_initials":"WA","lat":48.731983},"project":{"name":"Derelict Gear"},"date":"05/04/2010","organization":{"name":"Northwest Straits"},"id":2817},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8858},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":2818},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.712583, 48.463183","lon":-122.712583,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.463183},"project":{"name":"Derelict Gear"},"date":"09/06/2010","organization":{"name":"Northwest Straits"},"id":2819},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4226, 47.673833","lon":-122.4226,"county":"King","state":"Washington","st_initials":"WA","lat":47.673833},"project":{"name":"Derelict Gear"},"date":"05/28/2010","organization":{"name":"Northwest Straits"},"id":2822},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4487, 48.107667","lon":-122.4487,"county":"Island","state":"Washington","st_initials":"WA","lat":48.107667},"project":{"name":"Derelict Gear"},"date":"05/13/2012","organization":{"name":"Northwest Straits"},"id":2821}]
			},
			{
				username: "Goat Man",
				organization: "Save Our Shores",
				timestamp: "09/14/2007 10:05",
				status: 'new',
				events: [{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8860},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.7153, 48.458517","lon":-122.7153,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.458517},"project":{"name":"Derelict Gear"},"date":"07/03/2010","organization":{"name":"Northwest Straits"},"id":2820},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.50355, 48.731983","lon":-122.50355,"county":"Whatcom","state":"Washington","st_initials":"WA","lat":48.731983},"project":{"name":"Derelict Gear"},"date":"05/04/2010","organization":{"name":"Northwest Straits"},"id":2817},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8858},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":2818},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.712583, 48.463183","lon":-122.712583,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.463183},"project":{"name":"Derelict Gear"},"date":"09/06/2010","organization":{"name":"Northwest Straits"},"id":2819},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4226, 47.673833","lon":-122.4226,"county":"King","state":"Washington","st_initials":"WA","lat":47.673833},"project":{"name":"Derelict Gear"},"date":"05/28/2010","organization":{"name":"Northwest Straits"},"id":2822},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4487, 48.107667","lon":-122.4487,"county":"Island","state":"Washington","st_initials":"WA","lat":48.107667},"project":{"name":"Derelict Gear"},"date":"05/13/2012","organization":{"name":"Northwest Straits"},"id":2821}]

			},
			{
				username: "Data Wrangler",
				organization: "Georgia Straits",
				timestamp: "09/14/2007 10:05",
				status: 'new',
				events: [{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8860},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.7153, 48.458517","lon":-122.7153,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.458517},"project":{"name":"Derelict Gear"},"date":"07/03/2010","organization":{"name":"Northwest Straits"},"id":2820},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.50355, 48.731983","lon":-122.50355,"county":"Whatcom","state":"Washington","st_initials":"WA","lat":48.731983},"project":{"name":"Derelict Gear"},"date":"05/04/2010","organization":{"name":"Northwest Straits"},"id":2817},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8858},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":2818},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.712583, 48.463183","lon":-122.712583,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.463183},"project":{"name":"Derelict Gear"},"date":"09/06/2010","organization":{"name":"Northwest Straits"},"id":2819},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4226, 47.673833","lon":-122.4226,"county":"King","state":"Washington","st_initials":"WA","lat":47.673833},"project":{"name":"Derelict Gear"},"date":"05/28/2010","organization":{"name":"Northwest Straits"},"id":2822},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4487, 48.107667","lon":-122.4487,"county":"Island","state":"Washington","st_initials":"WA","lat":48.107667},"project":{"name":"Derelict Gear"},"date":"05/13/2012","organization":{"name":"Northwest Straits"},"id":2821}]

			},
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'new',
				events: [{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8860},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.7153, 48.458517","lon":-122.7153,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.458517},"project":{"name":"Derelict Gear"},"date":"07/03/2010","organization":{"name":"Northwest Straits"},"id":2820},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.50355, 48.731983","lon":-122.50355,"county":"Whatcom","state":"Washington","st_initials":"WA","lat":48.731983},"project":{"name":"Derelict Gear"},"date":"05/04/2010","organization":{"name":"Northwest Straits"},"id":2817},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":8858},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.582183, 47.573483","lon":-122.582183,"county":"Kitsap","state":"Washington","st_initials":"WA","lat":47.573483},"project":{"name":"Derelict Gear"},"date":"11/16/2010","organization":{"name":"Northwest Straits"},"id":2818},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.712583, 48.463183","lon":-122.712583,"county":"Skagit","state":"Washington","st_initials":"WA","lat":48.463183},"project":{"name":"Derelict Gear"},"date":"09/06/2010","organization":{"name":"Northwest Straits"},"id":2819},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4226, 47.673833","lon":-122.4226,"county":"King","state":"Washington","st_initials":"WA","lat":47.673833},"project":{"name":"Derelict Gear"},"date":"05/28/2010","organization":{"name":"Northwest Straits"},"id":2822},{"datasheet":{"id":19,"name":"Northwest Straits Derelict Gear Data","event_type":"Derelict Gear Report","start_date":2002},"site":{"name":"-122.4487, 48.107667","lon":-122.4487,"county":"Island","state":"Washington","st_initials":"WA","lat":48.107667},"project":{"name":"Derelict Gear"},"date":"05/13/2012","organization":{"name":"Northwest Straits"},"id":2821}]

			}
		],
		accepted: [
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'accepted',
				events: []
			},
			{
				username: "Goat Man",
				organization: "Save Our Shores",
				timestamp: "09/14/2007 10:05",
				status: 'accepted',
				events: []
			},
			{
				username: "Data Wrangler",
				organization: "Georgia Straits",
				timestamp: "09/14/2007 10:05",
				status: 'accepted',
				events: []
			},
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'accepted',
				events: []
			}
		],
		rejected: [
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'rejected',
				events: []
			},
			{
				username: "Goat Man",
				organization: "Save Our Shores",
				timestamp: "09/14/2007 10:05",
				status: 'rejected',
				events: []
			},
			{
				username: "Data Wrangler",
				organization: "Georgia Straits",
				timestamp: "09/14/2007 10:05",
				status: 'rejected',
				events: []
			},
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'rejected',
				events: []
			}
		]
	};
};

ko.applyBindings(new viewModel());
