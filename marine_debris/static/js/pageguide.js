app.pageguide = {};

/* THE DEFAULT PAGE GUIDE */

var defaultGuide = {
  id: 'jQuery.PageGuide',
  title: 'Data Page Guide',
  steps: [
    {
      target: '#left-content',
      content: 'The panel on the left side of the screen is where you will be able to filter, or \'query\' the full set of events collected in this database. There are thousands of cleanup events collected here, so this will make it easy for you to only view the events you want to see.',
      direction: 'right',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#right-content',
      content: 'The panel on the right side of the screen is where you will view the data for the events in your query. We will cover the different ways the data can be viewed in just a moment.',
      direction: 'left',
      arrow: {offsetX: 0, offsetY: 50}
    },{
      target: '#location-tab',
      content: 'This tab allows you to query the cleanup events by location, either by specifying the state or the county that they were conducted in. You can select multiple states or counties to include events for each in your query. For derelict gear removal, the county with coast closest in proximity to the event is used.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#event-type-tab',
      content: 'This tab allows you to select the type of debris cleanup event you\'re looking for. This will likely be either a \'Site Cleanup\' or a \'Derelict Gear Removal\'.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#project-organization-tab',
      content: 'This tab allows you to narrow your query down to specific organizations\' or projects\' events. Select as many organizations or projects as you\'re interested in and the rest will be left out of your query.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#date-tab',
      content: 'If you are only interested in events that fall within a range of dates, you may specify the starting date and ending date here. This is very useful if you only want to see 1 year\'s worth of data.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#events-table',
      content: 'Here is the list of events that match your query. If you haven\'t added any filters to your query, then this will display all of the events (by pages of 5 at a time).',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#events-table_paginate',
      content: 'Use these buttons to navigate the list of events.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#map-tab',
      content: 'Click this tab to display all of the queried events on the map. If you have not entered any query criteria, all events will show.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#details-tab',
      content: 'Click on this tab to display the details of a certain event. To select an event to get details about, either click on its point on the map, or on the event from the list in the left panel.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '#report-tab',
      content: 'Click on this tab to aggregate the values for fields across all of the events in your query. Warning: this may take some time to generate if you have a lot of events.',
      direction: 'top',
      arrow: {offsetX: 0, offsetY: 0}
    },{
      target: '.wcga-database-right .tab-content',
      content: 'This is the map where you can view the locations of the events in your query. You can move the map, as well as zoom in on it. You may also select an event on the map to show it in the left list, as well as pull up the details of event by clicking on the \'Event Details\' tab afterwards.',
      direction: 'left',
      arrow: {offsetX: 100, offsetY: 100},
      zIndex: 10000
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
        } else if ($(this).data('idx') === 11){
            $('#map-tab').tab('show');
        }
        
      }
    }
  }
}

$(function() {
  // Load the default guide!  
  $.pageguide(defaultGuide, defaultGuideOverrides);
  // $.pageguide(defaultGuide);
  
});