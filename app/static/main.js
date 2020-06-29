var domainsTable = null;

function addDomain() {
    bootbox.dialog({
        title: 'Add a domain to track',
        message: `
        <form>
            <div class="form-row">
                <div class="col-sm-6">
                    <label>Domain</label>
                    <input type="email" class="form-control" id="newInputDomain" placeholder="Domain to monitor">
                    <small class="form-text text-muted">The domain to be perpetually resolved. Must be unique in system</small>
                </div>
                <div class="col-sm-3">
                    <label>Tag</label>
                    <div class="input-group">
                        <div class="input-group-prepend">
                            <div class="input-group-text"><i class="fa fa-tag"></i></div>
                        </div>
                        <input type="text" class="form-control" id="newInputDomainTag" placeholder="Tag">
                    </div>
                    <small class="form-text text-muted">Apply a logical grouping</small>
                </div>
                <div class="col-sm-3">
                    <label>TTR</label>
                    <select class="custom-select mr-sm-2" id="newInputDomainTTR">
                        <option selected value="5">5 Min</option>
                        <option value="10">10 Min</option>
                        <option value="30">30 Min</option>
                        <option value="60">60 Min</option>
                    </select>
                    <small class="form-text text-muted">Resolve frequency</small>
                </div>
            </div>
            <div class="form-row">
                <div class="col-sm-12 form-group">
                    <label>Notes</label>
                    <textarea class="form-control" id="newInputDomainNotes" rows="4"></textarea>
                    <small class="form-text text-muted">Any additional information you'd like to track. Markdown is supported.</small>
                </div>
                <div class="col-sm-3 my-1">
                
              </div>
            </div>
        </form>
      `,
        size: 'large',
        buttons: {
            cancel: {
                label: "Cancel",
                className: 'btn-default',
            },
            ok: {
                label: "Add Domain(s)",
                className: 'btn-success',
                callback: function() {

                    let domainRef = $("#newInputDomain");
                    let tag = $('#newInputDomainTag').val();
                    let ttr = $('#newInputDomainTTR').val();
                    let notes = $('#newInputDomainNotes').val();

                    if(!domainRef.val()) {
                        domainRef.addClass('is-invalid');
                        toastr.error("You must supply a domain to track.");
                        return false;
                    }

                    $.ajax({
                        method: "POST",
                        url: `/api/domain/${domainRef.val()}`,
                        dataType: 'json',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            tag: tag, 
                            ttr: ttr, 
                            notes: notes
                        }),
                        success: function(data) {
                            toastr.success(`Successfully added ${data['domain']} to Darkstar`);
                            $('table[name=tracked-domains]').DataTable().ajax.reload().draw();
                            bootbox.hideAll();
                        },
                        error: function(xhr) {
                            api_failure(xhr);
                        }
                    })

                    // Ensure the modal doesn't close - we gotta' close it from the ajax success
                    return false;
                }
            }
        }
    })
}

function api_failure(xhr) {
    console.error(xhr.responseJSON.error_debug);
    toastr.error(xhr.responseJSON.error_msg)
}

function renderDetailsColumn() {

}

$(document).ready(function() {

    function renderDetailsExpanderColumn(data, type, row, meta) {

    }

    function renderToolsColumn(data, type, row, meta) {
        return `
        <div class="btn-group" role="group">
            <button type="button" class="btn btn-secondary dropdown-toggle btn-sm" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Actions
            </button>
            <div class="dropdown-menu">
                <a class="dropdown-item" href="#">
                    Edit Details
                </a>
                <a class="dropdown-item" href="#">
                    ${row.enabled ? 'Disable' : 'Enable'} Resolving
                </a>
                <a class="dropdown-item" href="#">
                    Remove
                </a>
            </div>
        </div>
        `;
    }

    function renderTimestampColumn(data, type, row, meta) {
        let d = new Date(data);
        let minutes = (d.getMinutes() < 10 ? '0' : '') + d.getMinutes();
        let hours = (d.getHours() < 10 ? '0' : '') + d.getHours();
        let seconds = (d.getSeconds() < 10 ? '0' : '') + d.getSeconds();
        return `<span class='break-word monospace'>${d.toDateString()}&nbsp;${hours}:${minutes}:${seconds}</span>`
    }

    function renderTagColumn(data) {
        if(data) {
            let tag = data.replace(/(^\w{1})|(\s{1}\w{1})/g, match => match.toUpperCase());
            return `<i class="fa fa-tag"></i>&nbsp;&nbsp;${tag}`;
        }
        return '';
    }

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