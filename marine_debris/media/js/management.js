
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
		"iDisplayLength": 8,
    	"sPaginationType": "full_numbers"
    };

	self.transactions = {
		new: [
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'new'
			},
			{
				username: "Goat Man",
				organization: "Save Our Shores",
				timestamp: "09/14/2007 10:05",
				status: 'new'
			},
			{
				username: "Data Wrangler",
				organization: "Georgia Straits",
				timestamp: "09/14/2007 10:05",
				status: 'new'
			},
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'new'
			}
		],
		accepted: [
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'accepted'
			},
			{
				username: "Goat Man",
				organization: "Save Our Shores",
				timestamp: "09/14/2007 10:05",
				status: 'accepted'
			},
			{
				username: "Data Wrangler",
				organization: "Georgia Straits",
				timestamp: "09/14/2007 10:05",
				status: 'accepted'
			},
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'accepted'
			}
		],
		rejected: [
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'rejected'
			},
			{
				username: "Goat Man",
				organization: "Save Our Shores",
				timestamp: "09/14/2007 10:05",
				status: 'rejected'
			},
			{
				username: "Data Wrangler",
				organization: "Georgia Straits",
				timestamp: "09/14/2007 10:05",
				status: 'rejected'
			},
			{
				username: "Data Wrangler",
				organization: "Surfrider",
				timestamp: "09/14/2007 10:05",
				status: 'rejected'
			}
		]
	};
};

ko.applyBindings(new viewModel());
