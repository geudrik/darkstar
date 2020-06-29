function modalAddEditDomainRender(domain=false, tag=false, ttr=false, notes=false) {
    let d = domain ? `value="${domain}"` : '';
    let t = tag ? `value="${tag}"` : '';
    let n = notes ? `value="${notes}"` : '';
    return `
        <form>
            <div class="form-row">
                <div class="col-sm-6">
                    <label>Domain</label>
                    <input type="email" class="form-control" id="newInputDomain" placeholder="Domain to monitor" ${d}>
                    <small class="form-text text-muted">The domain to be perpetually resolved. Must be unique in system</small>
                </div>
                <div class="col-sm-3">
                    <label>Tag</label>
                    <div class="input-group">
                        <div class="input-group-prepend">
                            <div class="input-group-text"><i class="fa fa-tag"></i></div>
                        </div>
                        <input type="text" class="form-control" id="newInputDomainTag" placeholder="Tag" ${t}>
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
                    <textarea class="form-control" id="newInputDomainNotes" rows="4" ${n}></textarea>
                    <small class="form-text text-muted">Any additional information you'd like to track. Markdown is supported.</small>
                </div>
                <div class="col-sm-3 my-1">
                
              </div>
            </div>
        </form>
    `
}

function modalAddEditSubmitCallback() {
    
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

function modalAddDomain() {
    bootbox.dialog({
        title: 'Add a domain to track',
        message: modalAddEditDomainRender(),
        size: 'large',
        buttons: {
            cancel: {
                label: "Cancel",
                className: 'btn-default',
            },
            ok: {
                label: "Add Domain(s)",
                className: 'btn-success',
                callback: modalAddEditSubmitCallback
            }
        }
    })
}

function modalEditDomain(row_data) {
    bootbox.dialog({
        title: 'Update Domain',
        message: modalAddEditDomainRender(row_data.domain, row_data.tag, row_data.ttr, row_data.notes),
        size: 'large',
        buttons: {
            cancel: {
                label: "Cancel",
                className: 'btn-default'
            },
            ok: {
                label: "Add Domain(s)",
                className: 'btn-success',
                callback: modalAddEditSubmitCallback
            }
        }
    })
}