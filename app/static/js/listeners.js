$(document).on('click', '#rowClickEditDomain', function(e) {
    let tr = $(this).closest('tr');
    let row = domainsTable.row(tr);
    modalEditDomain(row.data);
})