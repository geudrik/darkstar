var domainsTable = null;
$(document).ready(function() {

    domainsTable = $('table[name=domains-table]').dataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: "/api/stats",
            dataSrc: "items"
        }
    })
})