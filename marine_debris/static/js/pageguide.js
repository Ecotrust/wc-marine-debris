app.pageguide = {};

/* THE DEFAULT PAGE GUIDE */

var defaultGuide = {
  id: 'jQuery.PageGuide',
  title: 'Data Page Guide',
  steps: [
    {
      target: '#left-content',      
      content: 'Initially, all marine debris events from the database will be shown in the event list.  You can narrow down this list with a combination of one or more filters.  Only the events that match <i>all</i> of your filters will be shown.',
      direction: 'right',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#location-tab',
      content: 'The <i>Location</i> tab lets you filter events by State or County by typing them in or selecting them from the drop-down list. <i>Note</i>, you can add more than one state or county.',
      direction: 'left',
      arrow: {offsetX: 0, offsetY: 50}
    },{
      target: '#event-type-tab',
      content: 'The <i>Type Of debris</i> tab lets you filter by event type (e.g. Site Cleanup, Derelict Gear Removal) or Debris Type (e.g. plastic bags, ammunition, debris description).',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#project-organization-tab',
      content: 'The <i>Organization/Project</i> tab lets you find events associated with a specific debris cleanup organization or project',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#date-tab',
      content: 'The <i>Date</i> tab lets you find events after a given start date and/or before a given end date.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#events-table',
      content: 'Marine debris events are listed 5 at a time.  As you apply or remove filters this list will be updated.  Click one of the events to highlight it on the map.  Click any of the column headers to sort by that column ascending or descending.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#events-table_paginate',
      content: 'The <i>Navigation</i> bar lets you scroll through the list of events.  The <i>First</i> and <i>Last</i> button lets you quickly jump to the beginning or end of the list',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#right-content',
      content: 'You can get more information about individual events in your list, or your list as a whole using the Map, Event Details, and Report tabs.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#map-tab',
      content: 'The <i>Map</i> tab shows you geographically where each of the events in your list occurred.  Orange colored circles are site cleanups and grey colored circles are derelict gear removals.  Events that are close together are clustered <image>.  Click on a cluster to zoom in on individual events.  Individual events that took place at the exact same location will always show as clustered, no matter how far you zoom in.  Clicking a cluster or an event on the map will also  reorder the event list so that the event(s) you selected will show first in the list.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#details-tab',    
      content: 'Once you\'ve selected an event, either on the map or in the event list, the <i>Event Details</i> tab provides you with all of the information collected for that event.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#report-tab',
      content: 'The <i>Report<i> tab provides you with a cumulative summary of all events in your event list (e.g. total pounds of trash collected, total number of volunteers, etc).  Note, filtering your events to either Site Cleanups or Derelict Gear Removal will provide you with the most meaningful report.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#view-report-button',
      content: 'The <i>View Report</i> button below the event list will take you straight to the <i>Report</i> tab',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#download-data-button',
      content: 'The <i>Download Data</i> button allows you to download all of the event data for all of the events in your list as a CSV spreadsheet.  By removing all filters you can effectively download the entire database.',
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
