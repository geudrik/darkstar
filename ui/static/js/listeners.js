// Listen for clicks of the "Edit" tools menu option
$(document).on('click', '#rowClickEditDomain', function(e) {
    let tr = $(this).closest('tr');
    let d = $('table[name=tracked-domains]').DataTable().row(tr).data();
    modalEditDomain(d);
})

// Listen for clicks of the "Delete" tools menu option
$(document).on('click', '#rowClickDeleteDomain', function(e) {
    let tr = $(this).closest('tr');
    let dt = $('table[name=tracked-domains]').DataTable();
    let d = dt.row(tr).data();
    $.ajax({
        method: 'DELETE',
        url: `/api/domain/${d.domain}`,
        success: function() {
            toastr.success(`Successfully deleted ${d.domain} from tracking`);
            dt.ajax.reload().draw();
        },
        error: function(xhr) {
            api_failure(xhr);
        }
    })
})

// Set the enabled/disable filter
// Since its value is applied in the DT init, all we have to do is redraw to have its new value
//  picked up.
$(document).on('change', '#tableOptsEnabledFilter', function(event, ui) {
    $('table[name=tracked-domains]').DataTable().draw();
});

// Set our page length and redraw
$(document).on('change', '#tableOptsPageLength', function(event, ui) {
    let dt = $('table[name=tracked-domains]').DataTable();
    dt.page.len($(this).val()).draw();
});

// Searching (ftilering) in the domains table
$(document).on('keyup', '#domainsTableFilterSearchInput', function(event, ui) {
    if(event.keyCode == 13)
    {
        let search_query = $(this).val();

        // Add a trailing asterisk to the query if it doesn't end with one already. This is ES..
        if ( ! search_query.endsWith("*") ) {
            search_query = `${search_query}*`;
        }

        // Do the search and redraw the table
        let dt = $('table[name=tracked-domains]').DataTable();
        dt.search(search_query).draw();
    }
});

// Listen for a click of the actual search button, right next to the search box
$(document).on('click', '#domainsTableFilterSearchButton', function(e) {
    let search_query = $('#domainsTableFilterSearchInput').val();

    // Add a trailing asterisk to the query if it doesn't end with one already. This is ES..
    if ( ! search_query.endsWith("*") ) {
        search_query = `${search_query}*`;
    }

    // Do the search and redraw the table
    let dt = $('table[name=tracked-domains]').DataTable();
    dt.search(search_query).draw();
})


