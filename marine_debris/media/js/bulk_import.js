var app = {
  resetForm: function ($form, options) {
  
  
    var update = function(lat, lon) {
    
      if (lat && lon) {
        $("#id_geometry").val("POINT(" + lon + " " + lat + ")");
        pointSelected(lat, lon);
        $form.find(".submit-site-btn").removeAttr('disabled');
      }
    };
  
    $form.find("#id_latitude").on('change', function () {
      update($form.find("#id_latitude").val(), $form.find("#id_longitude").val());
    });

    $form.find("#id_longitude").on('change', function () {
      update($form.find("#id_latitude").val(), $form.find("#id_longitude").val());
    });
    $form.find('.problem').on('click', function (e) {
      app.resetForm($form, options);
    });
    $form.find('.submit-site-btn').attr('disabled', true);
    $form.find('.form-buttons').show();
    $form.find('.alert').hide();
    $form.find('#id_sitename').val(options.sitename).closest('p').hide();
    $form.find('#id_county').val(options.county).closest('p').hide();
    $form.find("#id_state").closest('p').hide()
    $form.find("#id_state").val($form.find('option:contains("' + options.state + '")').attr('value'));
    $form.find("#id_transaction").closest('p').hide();
    $form.find("#id_latitude").removeAttr('disabled');
    $form.find("#id_longitude").removeAttr('disabled');
    $form.find("#id_latitude").val(null);
    $form.find("#id_longitude").val(null);
    $form.find("#id_geometry").val(null);
    pointLayer.removeAllFeatures()
  },
  submitSite: function (data, success, error) {
    $("#id_latitude").attr('disabled', true);
    $("#id_longitude").attr('disabled', true);
    $.ajax({
      url: '/site/create',
      data: data,
      type: "POST",
      success: success,
      error: error
    });
  }
}


$(function() {

      $('.errorlist').find(".create-site").removeAttr('disabled');

      $('.errorlist').scroll(function () {
        map.updateSize();
      });

      $( "#bulk_submit" ).click( function(e) {
          $(".wcga-database-right").html('<div class="alert alert-info">Loading...</div>');
      });
      $( "#download-csv-template" ).click( function(e) {
          e.preventDefault();
          selected = $("#id_datasheet_id").val();
          window.open("/datasheet/csv_header/" + selected);
      });
      $('.errorlist').on('click', '.cancel', function (e) {
        var $a = $(e.target).closest('.btn'), $container = $a.closest('li');
        $container.find('#site-form').remove();
        $container.find('.create-site').removeAttr('disabled');
      });
      $('.errorlist').on('click', '.submit-site-btn', function (e) {
        var data = {}, $form = $(e.target).closest('div');
        $form.find('input,select').each(function (i, field) {
          var $field = $(field), name = $field.attr('name');
          if (!$field.val()) {
            // hard code select last transaction
            $field.val($field.find("option:last-child").val());
          }
          data[name] = $field.val();
        });
        app.submitSite(data, 
          function (response) {
            $alert = $form.closest('li');
            if (/Success/.test(response)) {
              $alert.removeClass('alert-error').addClass('alert-success');
              $alert.text(data.sitename + ' successfully created.  Please resubmit data when all sites have been created.')

            } else {
              $form.find('.form-buttons').hide();
              $alert.find('.problem').show();  
            }
          },
          function (response, error) {
            $form.find('.form-buttons').hide();
            $form.closest('li').find('.problem').show();
          });
      });

      $('.errorlist').on('click','.create-site', function (e) {
        var $a = $(e.target).closest('.btn'), $container = $a.closest('li'),
            $form = $('#site-form').clone().wrap('form'),
            options = $.deparam($a.attr('href').split('?')[1]);
        
        e.preventDefault();
        $a.attr('disabled', true);
        app.resetForm($form, options);
        $container.append($form.show());
        map.render('bulk-site-map');
        map.zoomToExtent(map.restrictedExtent);
      });

    

});
  