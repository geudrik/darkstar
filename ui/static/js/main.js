function api_failure(xhr) {
    console.error(xhr.responseJSON.error_debug);
    toastr.error(xhr.responseJSON.error_msg)
}

$(document).ready(function() {

    // Enable tooltips
    $('body').tooltip({
        selector: '[data-toggle="tooltip"]'
    });

    $('table[name=tracked-domains]').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/api/resolutions",
            "dataSrc": "items",
            "data": function(d) {
                // Lets us add URL args
                d.enabled_opt = $('#tableOptsEnabledFilter').val()
            }
        },
        "columns": [
            {"title": "", "width": "80px", "data": null, "orderable": false, "render": renderToolsColumn},
            {"title": "Tag", "width": "100px", "data": "tag", "render": renderTagColumn},
            {"title": "Domain", "data": "domain"},
            {"title": "Added", "width": "200px", "data": "added", "render": renderTimestampColumn},
            {"title": "Latest Resolution", "width": "200px", "data": "last_resolved", "render": renderTimestampColumn},
            {"title": "TTR (mins)", "width": "100px", "data": "ttr"},
        ],
        //"createdRow": render_row,
        "order": [[0, 'desc']],
        "pageLength": 10,
        "stateSave": false,
        "dom":
            "<'row'<'col-sm-12'rt>>"+
            "<'row'<'col-sm-5'i><'col-sm-7'p>>",
        "buttons": []
    })
})