$(function() {  
	
	// prototype code for mimicing Balsamiq mockups import events interactions

	// import events
	$('.import-row-project, .import-row-date, .import-row-data-sheet, .import-row-state, .import-row-events-file').hide();

	$('#imported-events-summary').hide();

	$('#btn-import-events').hide();

	$('#btn-edit-events').hide();

	$('#imported-events-map-data-reports').hide();

	$('select[name="import-select-organization"]').change(function() {
		if ($(this).find('#organization-save-our-shores').is(':selected')) {
			$('.import-row-project').show();
		}
	});

	$('select[name="import-select-project"]').change(function() {
		if ($(this).find('#project-derelict-gear').is(':selected')) {
			$('.import-row-data-sheet').show();
		}
	});

	$('select[name="import-select-data-sheet"]').change(function() {
		if ($(this).find('#data-sheet-derelict-gear-data').is(':selected')) {
			$('.import-row-state').show();
		}
	});

	$('select[name="import-select-state"]').change(function() {
		if ($(this).find('#state-california').is(':selected')) {
			$('.import-row-events-file').show();
			$('#btn-file-upload-open').hide();
		}
	});

	$('.import-data-file').click(function() {
		$('#import-file-upload').attr('value','Derelict_Gear_Data_Table');
		// had trouble with .on so i'm using two buttons instead
		$('#btn-file-upload-open-disabled').hide();
		$('#btn-file-upload-open').show();
	});

	$('#btn-file-upload-open').click(function() {
  		$('#modal-file-upload').modal('hide');
  		$('#input-events-file').attr('value','Derelict_Gear_Data_Table');
  		// had trouble with .on so i'm using two buttons instead
  		$('#btn-import-events-disabled').hide();
  		$('#btn-import-events').show();
	});

	$('#btn-import-events').click(function() {
		$('#form-import-events-selection').hide();
		$('#imported-events-summary').show();
		$('#btn-import-events').hide();
		$('#btn-edit-events').show();
		$('#imported-events-map-data-reports').show();
	});

	$('#btn-edit-events').click(function() {
		$(this).hide();
		$('#imported-events-summary').hide();
		$('#imported-events-map-data-reports').hide();
		$('#form-import-events-selection').show();
		$('#btn-import-events').show();
	});

	$('#btn-cancel-edit').click(function() {
		$('#btn-edit-events').hide();
		$('#imported-events-summary').hide();
		$('#imported-events-map-data-reports').hide();
		$('#form-import-events-selection').show();
		$('#btn-import-events').show();
	});

});