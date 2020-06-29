var domainsTable = null;

function api_failure(xhr) {
    console.error(xhr.responseJSON.error_debug);
    toastr.error(xhr.responseJSON.error_msg)
}

$(document).ready(function() {

    domainsTable = $('table[name=tracked-domains]').DataTable({
        "processing": true,
        "serverSide": false,
        "ajax": {
            "url": "/api/resolutions",
            "dataSrc": "items",
            "data": function(d) {
                // Lets us add URL args
                d.only_enabled = false  // TODO: Ensure this is bound to a toggle value, then just redraw table on toggle
            }
        },
        "columns": [
            {"title": "", "width": "100px", "data": null, "orderable": false, "render": renderToolsColumn},
            {"title": "Tag", "width": "100px", "data": "tag", "render": renderTagColumn},
            {"title": "Domain", "data": "domain"},
            {"title": "Added", "width": "200px", "data": "added", "render": renderTimestampColumn},
            {"title": "Latest Resolution", "width": "200px", "data": "last_resolved", "render": renderTimestampColumn},
            {"title": "TTR", "width": "100px", "data": "ttr", "render": (data) => {return `${data} Mins`}},
        ],
        //"createdRow": render_row,
        "order": [[0, 'desc']],
        "pageLength": 20,
        "stateSave": false,
        "dom":
            "<'row'<'col-sm-12'rt>>"+
            "<'row'<'col-sm-5'i><'col-sm-7'p>>",
        "buttons": []
    })
})