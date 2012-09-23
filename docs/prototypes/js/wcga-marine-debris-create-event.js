$(function() {  

	// prototype code for mimicing Balsamiq mockups create event interactions

	// create event
	$('.create-row-project, .create-row-date, .create-row-data-sheet, .create-row-state, .create-row-events-file').hide();

	$('.create-event-summary').hide();

	$('.created-event-map-location').hide();

	$('#create-event-summary').hide();

	$('#btn-select-event-location').hide();

	$('#btn-set-location').hide();

	$('#btn-create-event-disabled, #btn-create-event').hide();

	$('#create-event-select-location').hide();

	$('#create-event-location-selected').hide();

	$('#event-details').hide();

	$('.state-row, .latitude-row, .longitude-row').hide();

	$('select[name="create-select-organization"]').change(function() {
		if ($(this).find('#organization-save-our-shores').is(':selected')) {
			$('.create-row-project').show();
		}
	});

	$('select[name="create-select-project"]').change(function() {
		if ($(this).find('#project-derelict-gear').is(':selected')) {
			$('.create-row-date').show();
		}
	});

	// date filed icon triggering Bootstrap popover containing calendar
	$('#select-date').click(function() {
		$(this).popover({
			template: '<div id="popover-select-date" class="popover popover-select-date"><div class="popover-inner"><div class="popover-content"><div class="select-date-widget"></div></div></div></div>',
			placement: 'right'
		});
		// faking selected date as I couldn't get click events inside the popover to close it
		$('#input-selected-date').attr('value', '08/28/12');
		$(this).popover('hide');
		$('.create-row-data-sheet').show();
	});

	$('select[name="create-select-data-sheet"]').change(function() {
		if ($(this).find('#data-sheet-derelict-gear-data').is(':selected')) {
			$('#btn-select-event-location-disabled').hide();
			$('#btn-select-event-location').show();
		}
	});

	$('#btn-select-event-location').click(function () {
		$('.create-event-summary').show();
		$("#btn-select-event-location").hide();
		$("#btn-select-event-location-disabled").show();
		$('#create-event-select-location').show();
		$("#form-create-event-selection").hide();
		$("#create-event-summary").show();
		$("#create-event-location-setup").show();
		$('#btn-create-event-disabled').show();
		$('#btn-select-event-location-disabled').hide();
	});

	$('#input-location-longitude, #input-location-latitude').click(function () {
		$('#input-location-latitude').attr('value', '36.8374');
		$('#input-location-longitude').attr('value', '-121.9850');
		$('.created-event-map').hide();
		$('.created-event-map-location').show();
		$('#btn-set-location-disabled').hide();
		$('#btn-set-location').show();
	});

	$("#btn-cancel-set-location").click(function () {
		$('#create-event-select-location').hide();
		$('#create-event-summary').hide();
		$('#form-create-event-selection').show();
		$('#btn-select-event-location-disabled').hide();
		$('#btn-select-event-location').show();
		$('#input-location-latitude').attr('value', '');
		$('#input-location-longitude').attr('value', '');
		$('.created-event-map').show();
		$('.created-event-map-location').hide();
		$('#btn-set-location-disabled').show();
		$('#btn-set-location').hide();
		$('#btn-create-event-disabled').hide();
	});

	$('#btn-set-location').click(function () {
		$('#create-event-location-setup').hide();
		$('#create-event-location-selected').show();
		$('#btn-create-event-disabled').hide();
		$('#btn-create-event').show();
		$('.state-row, .latitude-row, .longitude-row').show();
	});

	$('#btn-edit-location').click(function () {
		$('#create-event-location-setup').show();
		$('#create-event-location-selected').hide();
		$('#btn-create-event-disabled').show();
		$('#btn-create-event').hide();
		$('.state-row, .latitude-row, .longitude-row').hide();
	});

	$('#btn-create-event').click(function () {
		$(this).hide();
		$('#create-event-location-selected').hide();
		$('#event-details').show();
		$('#btn-edit-event').show();
	});

	$('#btn-edit-event').click(function () {
		$(this).hide();
		$('#create-event-location-selected').show();
		$('#event-details').hide();
		$('#btn-create-event').show();
	});

});