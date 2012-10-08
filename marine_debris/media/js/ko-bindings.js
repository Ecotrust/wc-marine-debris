ko.bindingHandlers.datepicker = {
    init: function(element, valueAccessor, allBindingsAccessor) {
        //initialize datepicker with some optional options
        var options = allBindingsAccessor().datepickerOptions || {};
        $(element).datepicker(options);

        //handle the field changing
        ko.utils.registerEventHandler(element, "change", function () {
            var observable = valueAccessor();
            observable($(element).datepicker("getDate"));
        });

        //handle disposal (if KO removes by the template binding)
        ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            $(element).datepicker("destroy");
        });

    },
    update: function(element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor());

        //handle date data coming via json from Microsoft
        if (String(value).indexOf('/Date(') == 0) {
            value = new Date(parseInt(value.replace(/\/Date\((.*?)\)\//gi, "$1")));
        }

        current = $(element).datepicker("getDate");

        if (value - current !== 0) {
            $(element).datepicker("setDate", value);
        }
    }
};


/// <reference path="_references.js" />
/**
* Contains a number of useful utiity methods for javascript.
*
* File:         cog.utils.js
* Version:      0.1
* Author:       Lucas Martin
* License:      Creative Commons Attribution 3.0 Unported License. http://creativecommons.org/licenses/by/3.0/ 
* 
* Copyright 2011, All Rights Reserved, Cognitive Shift http://www.cogshift.com  
*/

// ** Global Utilities **
var cog = {};
cog.utils = {};

cog.utils.intercept = function (fnToIntercept, fnToExecute) {
    /// <summary>
    /// Intercepts a function with another function.  The original function is passed to the new function
    /// as the last argument of it's parameter list, and must be executed within the new function for the interception
    /// to be complete.
    /// </summary>
    /// <param name="fnToIntercept" type="Function">
    ///     The old function to intercept.
    /// </param>
    /// <param name="fnToExecute" type="Function">
    ///     The new function to be executed.
    /// </param>
    /// <returns>
    ///     A proxy function that performs the interception.  Execute this function like you would execute the fnToExecute function.
    /// </returns>
    fnToIntercept = fnToIntercept || function () { }
    return function () {
        var newArguments = []
        $.each(arguments, function (i, item) { newArguments.push(item); });
        newArguments.push(fnToIntercept);
        return fnToExecute.apply(this, newArguments);
    }
}

// ** String Utilities **
cog.utils.string = {}
cog.utils.string.format = function () {
    /// <summary>
    /// Replaces tokens in a string with the supplied parameters.
    /// </summary>
    /// <param name="string" type="String">
    ///     The string to search for the tokens.
    /// </param>
    /// <param name="params" type="Arguments">
    ///     A parameter list of tokens to replace.
    /// </param>
    /// <returns>
    ///     The string with the tokens replaced.
    /// </returns>
    var s = arguments[0];
    for (var i = 0; i < arguments.length - 1; i++) {
        var reg = new RegExp("\\{" + i + "\\}", "gm");
        s = s.replace(reg, cog.utils.convert.toString(arguments[i + 1]));
    }

    return s;
};

cog.utils.string.endsWith = function (string, suffix) {
    /// <summary>
    /// Searches the end of a string for another string.
    /// </summary>
    /// <param name="string" type="String">
    ///     The string to check.
    /// </param>
    /// <param name="suffix" type="String">
    ///     The suffix to look for.
    /// </param>
    /// <returns>
    ///     Returns true if the string ends with the supplied suffix.
    /// </returns>
    return (string.substr(string.length - suffix.length) === suffix);
};

cog.utils.string.startsWith = function (string, prefix) {
    /// <summary>
    /// Searches the start of a string for another string.
    /// </summary>
    /// <param name="string" type="String">
    ///     The string to check.
    /// </param>
    /// <param name="prefix" type="String">
    ///     The prefix to look for.
    /// </param>
    /// <returns>
    ///     Returns true if the string ends with the supplied prefix.
    /// </returns>
    return (string.substr(0, prefix.length) === prefix);
};

cog.utils.string.trimEnd = function (string, chars) {
    /// <summary>
    /// Trims a list of characters from the end of a string.
    /// </summary>
    /// <param name="string" type="String">
    ///     The string to trim.
    /// </param>
    /// <param name="chars" type="String">
    ///     The characters to trim off the end of the string.
    /// </param>
    /// <returns>
    ///     The string with the characters trimmed off the end.
    /// </returns>
    if (cog.utils.string.endsWith(string, chars)) {
        return string.substring(0, string.length - chars.length);
    }

    return string;
};

cog.utils.string.trimStart = function (string, chars) {
    /// <summary>
    /// Trims a list of characters from the start of a string.
    /// </summary>
    /// <param name="string" type="String">
    ///     The string to trim.
    /// </param>
    /// <param name="chars" type="String">
    ///     The characters to trim off the start of the string.
    /// </param>
    /// <returns>
    ///     The string with the characters trimmed off the start.
    /// </returns>
    if (cog.utils.string.startsWith(string, chars)) {
        return string.substring(chars.length, string.length);
    }

    return string;
};

// cog.utils.string.repeat = function (string, count) {
//     /// <summary>
//     /// Repeats a string the specified amount of times.
//     /// </summary>
//     /// <param name="string" type="String">
//     ///     The string to repeat.
//     /// </param>
//     /// <param name="chars" type="String">
//     ///     The number of times to repeat the string.
//     /// </param>
//     /// <returns>
//     ///     The repeated string sequence.
//     /// </returns>
//     return new Array(count + 1).join(string);
// }


/**
* A KnockoutJs binding handler for the html tables javascript library DataTables.
*
* File:         knockout.bindings.dataTables.js
* Author:       Lucas Martin
* License:      Creative Commons Attribution 3.0 Unported License. http://creativecommons.org/licenses/by/3.0/ 
* 
* Copyright 2011, All Rights Reserved, Cognitive Shift http://www.cogshift.com  
*
* For more information about KnockoutJs or DataTables, see http://www.knockoutjs.com and http://www.datatables.com for details.                    
*/

(function () {
    var _onInitialisingEventName = "ko_bindingHandlers_dataTable_onInitialising",
        _dataTablesInstanceDataKey = "ko_bindingHandlers_dataTable_Instance";

    ko.bindingHandlers['dataTable'] = {
        options: {},
        addOnInitListener: function (handler) {
            /// <Summary>
            /// Registers a event handler that fires when the Data Table is being initialised.
            /// </Summary>
            $(document).bind(_onInitialisingEventName, handler);
        },
        removeOnInitListener: function (handler) {
            /// <Summary>
            /// Unregisters an event handler to the onInitialising event.
            /// </Summary>
            $(document).unbind(_onInitialisingEventName, handler);
        },
        init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var binding = ko.utils.unwrapObservable(valueAccessor());
            var options = $.extend(true, {}, ko.bindingHandlers['dataTable'].options);

            // If the table has already been initialised, exit now.  Sometimes knockout.js invokes the init function of a binding handler in particular
            // situations twice for a given element.
            if (getDataTableInstance(element))
                return;

            // ** Initialise the DataTables options object with the data-bind settings **

            // Clone the options object found in the data bindings.  This object will form the base for the DataTable initialisation object.
            if (binding.options)
                options = $.extend(options, binding.options);

            // Define the tables columns.
            if (binding.columns && binding.columns.length) {
                options.aoColumns = [];
                ko.utils.arrayForEach(binding.columns, function (col) {

                    if (typeof col == "string") {
                        col = { mDataProp: col }
                    }

                    options.aoColumns.push(col);
                })
            }

            // Support for computed template name and templates that change
            var rowTemplate = ko.utils.unwrapObservable(binding.rowTemplate);
            if (ko.isObservable(binding.rowTemplate)) {
                binding.rowTemplate.subscribe(function (value) {
                    rowTemplate = value;
                    getDataTableInstance(element).fnDraw();
                });
            }

            // Register the row template to be used with the DataTable.
            if (binding.rowTemplate && binding.rowTemplate != '') {
                // Intercept the fnRowCallback function.
                options.fnRowCallback = cog.utils.intercept(options.fnRowCallback || function (row) { return row; }, function (row, data, displayIndex, displayIndexFull, next) {
                    // Render the row template for this row.
                    ko.renderTemplate(rowTemplate, bindingContext.createChildContext(data), null, row, "replaceChildren");
                    return next(row, data, displayIndex, displayIndexFull);
                });
            }

            // Set the data source of the DataTable.
            if (binding.dataSource) {
                var dataSource = ko.utils.unwrapObservable(binding.dataSource);

                // If the data source is a function that gets the data for us...
                if (typeof dataSource == 'function' && dataSource.length == 2) {
                    // Register a fnServerData callback which calls the data source function when the DataTable requires data.
                    options.fnServerData = function (source, criteria, callback) {
                    dataSource.call(viewModel, convertDataCriteria(criteria), function (result) {
                            callback({
                                aaData: ko.utils.unwrapObservable(result.Data),
                                iTotalRecords: ko.utils.unwrapObservable(result.TotalRecords),
                                iTotalDisplayRecords: ko.utils.unwrapObservable(result.DisplayedRecords)
                            });
                        });
                    }

                    // In this data source scenario, we are relying on the server processing.
                    options.bProcessing = true;
                    options.bServerSide = true;
                }
                // If the data source is a javascript array...
                else if (dataSource instanceof Array) {
                    // Set the initial datasource of the table.
                    options.aaData = ko.utils.unwrapObservable(binding.dataSource);

                    // If the data source is a knockout observable array...
                    if (ko.isObservable(binding.dataSource)) {
                        // Subscribe to the dataSource observable.  This callback will fire whenever items are added to 
                        // and removed from the data source.
                        binding.dataSource.subscribe(function (newItems) {
                            // ** Redraw table **
                            var dataTable = $(element).dataTable();
                            setDataTableInstanceOnBinding(dataTable, binding.table);
                                                                                    
                            // Get a list of rows in the DataTable.
                            var tableRows = dataTable.fnGetNodes();

                            // If the table contains rows...
                            if (tableRows.length) {
                                // Clear the datatable of rows, and if there are no items to display
                                // in newItems, force the fnClearTables call to rerender the table (because
                                // the call to fnAddData with a newItems.length == 0 wont rerender the table).
                                dataTable.fnClearTable(newItems.length == 0);
                            }

                            // Unwrap the items in the data source if required.
                            var unwrappedItems = [];
                            ko.utils.arrayForEach(newItems, function (item) {
                                unwrappedItems.push(ko.utils.unwrapObservable(item));
                            });

                            // Add the new data back into the data table.
                            dataTable.fnAddData(unwrappedItems);

                            // Unregister each of the table rows from knockout.
                            // NB: This must be called after fnAddData and fnClearTable are called because we want to allow
                            // DataTables to fire it's draw callbacks with the table's rows in their original state.  Calling
                            // this any earlier will modify the tables rows, which may cause issues with third party plugins that 
                            // use the data table.
                            ko.utils.arrayForEach(tableRows, function (tableRow) { ko.cleanNode(tableRow); });
                        });
                    }
                }
                // If the dataSource was not a function that retrieves data, or a javascript object array containing data.
                else {
                    throw 'The dataSource defined must either be a javascript object array, or a function that takes special parameters.';
                }
            }

            // If no fnRowCallback has been registered in the DataTable's options, then register the default fnRowCallback.
            // This default fnRowCallback function is called for every row in the data source.  The intention of this callback
            // is to build a table row that is bound it's associated record in the data source via knockout js.
            if (!binding.rowTemplate || binding.rowTemplate == '') {
                options.fnRowCallback = cog.utils.intercept(options.fnRowCallback || function (row) { return row; }, function (row, srcData, displayIndex, displayIndexFull, next) {
                        var columns = this.fnSettings().aoColumns

                        // Empty the row that has been build by the DataTable of any child elements.
                        var destRow = $(row);
                        destRow.empty();

                        // For each column in the data table...
                        ko.utils.arrayForEach(columns, function (column) {
                            var columnName = column.mDataProp;
                            // Create a new cell.
                            var newCell = $("<td></td>");
                            // Insert the cell in the current row.
                            destRow.append(newCell);
                            // bind the cell to the observable in the current data row.
                        var accesor = eval("srcData['" + columnName.replace(".", "']['") + "']");
                        ko.applyBindingsToNode(newCell[0], { text: accesor }, bindingContext.createChildContext(srcData));
                        });

                    return next(destRow[0], srcData, displayIndex, displayIndexFull);
                });
            }

            // Before the table has it's rows rendered, we want to scan the table for elements with knockout bindings
            // and bind them to the current binding context.  This is so you can bind elements like the header row of the
            // table to observables your view model.  Ideally, it would be great to call ko.applyBindingsToNode here,
            // but when we initialise the table with dataTables, it seems dataTables recreates the elements in the table
            // during it's initialisation proccess, killing any knockout bindings you apply before initialisation.  Instead,
            // we mark the elements to bind here with the ko-bind class so we can recognise the elements after the table has been initialised,
            // for binding.
            $(element).find("[data-bind]").each(function (i, childElement) {
                $(childElement).addClass("ko-bind");
            });

            // Fire the onInitialising event to allow the options object to be globally edited before the dataTables table is initialised.  This
            // gives third party javascript the ability to apply any additional settings to the dataTable before load.
            $(document).trigger(_onInitialisingEventName, { options: options });

            var dataTable = $(element).dataTable(options);
            setDataTableInstanceOnBinding(dataTable, binding.table);
            setDataTableInstance(element, dataTable);            

            // Apply bindings to those elements that were marked for binding.  See comments above.
        $(element).find(".ko-bind").each(function (e, childElement) {
            ko.applyBindingsToNode(childElement, null, bindingContext);
            $(childElement).removeClass("ko-bind");
        });

            
            // Tell knockout that the control rendered by this binding is capable of managing the binding of it's descendent elements.
            // This is crucial, otherwise knockout will attempt to rebind elements that have been printed by the row template.
            return { controlsDescendantBindings: true };
        },

        getDataTableInstance: function (element) {
            return getDataTableInstance(element);
        }
    };

    //// This function transforms the data format that DataTables uses to transfer paging and sorting information to the server
    //// to something that is a little easier to work with on the server side.  The resulting object should look something like 
    //// this in C#
    //public class DataGridCriteria
    //{
    //    public int RecordsToTake { get; set; }
    //    public int RecordsToSkip { get; set; }
    //    public string GlobalSearchText { get; set; }

    //    public ICollection<DataGridColumnCriteria> Columns { get; set; }
    //}

    //public class DataGridColumnCriteria
    //{
    //    public string ColumnName { get; set; }
    //    public bool IsSorted { get; set; }
    //    public int SortOrder { get; set; }
    //    public string SearchText { get; set; }
    //    public bool IsSearchable { get; set; }
    //    public SortDirection SortDirection { get; set; }
    //}

    //public enum SortDirection
    //{
    //    Ascending,
    //    Descending
    //}

    function convertDataCriteria (srcOptions) {
        var getColIndex = function (name) {
            var matches = name.match("\\d+");

            if (matches && matches.length)
                return matches[0];

            return null;
        }

        var destOptions = { Columns: [] };

        // Figure out how many columns in in the data table.
        for (var i = 0; i < srcOptions.length; i++) {
            if (srcOptions[i].name == "iColumns") {
                for (var j = 0; j < srcOptions[i].value; j++)
                    destOptions.Columns.push(new Object());
                break;
            }
        }

        ko.utils.arrayForEach(srcOptions, function (item) {
            var colIndex = getColIndex(item.name);

            if (item.name == "iDisplayStart")
                destOptions.RecordsToSkip = item.value;
            else if (item.name == "iDisplayLength")
                destOptions.RecordsToTake = item.value;
            else if (item.name == "sSearch")
                destOptions.GlobalSearchText = item.value;
            else if (cog.utils.string.startsWith(item.name, "bSearchable_"))
                destOptions.Columns[colIndex].IsSearchable = item.value;
            else if (cog.utils.string.startsWith(item.name, "sSearch_"))
                destOptions.Columns[colIndex].SearchText = item.value;
            else if (cog.utils.string.startsWith(item.name, "mDataProp_"))
                destOptions.Columns[colIndex].ColumnName = item.value;
            else if (cog.utils.string.startsWith(item.name, "iSortCol_")) {
                destOptions.Columns[item.value].IsSorted = true;
                destOptions.Columns[item.value].SortOrder = colIndex;

                var sortOrder = ko.utils.arrayFilter(srcOptions, function (item) {
                    return item.name == "sSortDir_" + colIndex;
                });

                if (sortOrder.length && sortOrder[0].value == "desc")
                    destOptions.Columns[item.value].SortDirection = "Descending";
                else
                    destOptions.Columns[item.value].SortDirection = "Ascending";
            }
        });

        return destOptions;
    }

    function getDataTableInstance(element) {
        return $(element).data(_dataTablesInstanceDataKey);
    }

    function setDataTableInstance(element, dataTable) {
        $(element).data(_dataTablesInstanceDataKey, dataTable);
    }

    function setDataTableInstanceOnBinding(dataTable, binding) {
        if(binding && ko.isObservable(binding)) {
            binding(dataTable);
        }
    }
})();