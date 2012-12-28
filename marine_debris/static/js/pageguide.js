app.pageguide = {};

/* THE DEFAULT PAGE GUIDE */

var defaultGuide = {
  id: 'jQuery.PageGuide',
  title: 'Data Page Guide',
  steps: [
    {
      target: '#left-content',      
      content: 'Use the panel on the left side of the screen to filter, or \'query\' the full set of events collected in this database. There are thousands of cleanup events collected here. This will make it easy for you to only view the events you want to see.',
      direction: 'right',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#right-content',
      content: 'Use the panel on the right side of the screen to view the data for the events in your query. This tour will cover the different ways the data can be viewed.',
      direction: 'left',
      arrow: {offsetX: 0, offsetY: 50}
    },{
      target: '#location-tab',      //mention "one or more filters"
      content: 'Use the Location tab to apply one or more location filters to query the cleanup events by location, either by specifying the state or the county that they were conducted in.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#event-type-tab',
      content: 'Use the Type of Debris tab to apply one or more filters to query the events by the type of debris cleanup event you\'re looking for. This will likely be either a \'Site Cleanup\' or a \'Derelict Gear Removal\'.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#project-organization-tab',
      content: 'Use the Organization/Project tab to apply filters to query the events by those belonging to one or more specific organizations or projects.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#date-tab',
      content: 'Use the Date tab to apply filters to query the events by those that fall within a range of dates, you may specify the starting date and ending date here. This is very useful if you only want to see 1 year\'s worth of data.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#events-table',      //mention selecting an event
      content: 'Use the Events Table to view the list of events in your query results. If you haven\'t added any filters to your query, then this will display all of the events by pages of 5 at a time. You can click on an event to highlight it on the map, and use the \'i\' button to see details about it.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#events-table_paginate',
      content: 'Use these buttons to navigate the list of events pages. Five events can be shown per page.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#map-tab',       //mention selecting an event    //use images for clusters
      content: 'Use the Map tab to view the location of each event in your query results. Select a cluster of events <img src="' + static_url + 'img/cluster.png" /> to zoom in on them. Select a single event <img src="' + static_url + 'img/event_point.png" /> to learn more about it. Different colors represent different event types: orange for site cleanups, gray for derelict gear removals. NOTE: IE8 and older will display clusters as larger circles with no numbers.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#details-tab',
      // content: 'Click on this tab to display the details of a certain event. To select an event to get details about, either click on its point on the map, or on the event from the list in the left panel.',
      content: 'Once you\'ve selected an event, you can view all available information for that event in the Event Details tab.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#report-tab',
      content: 'Click on this tab to aggregate the values for fields across all of the events in your query results. Be sure that you have selected the correct filters for this report to represent what you want.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#view-report-button',
      content: 'Click on this button to jump to the report tab described in the last step.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#download-data-button',
      content: 'Click on this button once you\'re happy with your query results and you want to download the data for your own use.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    }
  ]
}

var defaultGuideOverrides = {
  /*events: {
    open: function () {
    },
    close: function () {
    }
  },*/
  step: {
    events: {
      select: function() {
        if ($(this).data('idx') === 2) {
            $('#location-tab').tab('show');
        } else if ($(this).data('idx') === 3) {
            $('#event-type-tab').tab('show');
        } else if ($(this).data('idx') === 4) {
            $('#project-organization-tab').tab('show');
        } else if ($(this).data('idx') === 5){
            $('#date-tab').tab('show');
        } else if ($(this).data('idx') === 8){
            $('#map-tab').tab('show');
        } else if ($(this).data('idx') === 9){
            $('#details-tab').tab('show');
        } else if ($(this).data('idx') === 10){
            $('#report-tab').tab('show');
        }
        
      }
    }
  }
}


$(function() {
  // Load the default guide!  
  $.pageguide(defaultGuide, defaultGuideOverrides);

  setTimeout(function () {
    $('#help-tab').effect("pulsate", { times:3 }, 1000);  
  }, 2000);
  

  $('#help-tab').on('click', function() {
    if ( $.pageguide('isOpen') ) { // activated when 'tour' is clicked
        // close the pageguide
        $.pageguide('close');
        
    } else {
        //start the tour
        setTimeout( function() { $.pageguide('open'); }, 200 );      
    }
  });
  
  
});
