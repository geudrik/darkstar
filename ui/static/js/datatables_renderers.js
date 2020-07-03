function renderDetailsExpanderColumn(data, type, row, meta) {

}

function renderToolsColumn(data, type, row, meta) {
    return `
    <div class="btn-group" role="group">
        <button type="button" class="btn btn-secondary btn-sm" title='Expand row details' name="rowExpander"><i class="fa fa-chevron-down"></i></button>

        <button type="button" class="btn btn-secondary dropdown-toggle btn-sm" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <i class="fa fa-bars"></i>
        </button>
        <div class="dropdown-menu">
            <a class="dropdown-item" href="javascript:;" id="rowClickEditDomain">
                <i class="fa fa-edit"></i>&nbsp;&nbsp;Edit Domain Details
            </a>
            <a class="dropdown-item" href="javascript:;" title=${row.enabled ? 'Disable resolving' : 'Enable resolving'} id="rowClickToggleDomainResolving">
                <i class="fa ${row.enabled ? 'fa-stop-circle' : 'fa-play-circle'}"></i>&nbsp;&nbsp;${row.enabled ? 'Disable' : 'Enable'} Resolving
            </a>
            <a class="dropdown-item" href="javascript:;" id="rowClickDeleteDomain">
                <i class="fa fa-minus"></i>&nbsp;&nbsp;Remove Domain
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
        return `<i class="fa fa-tag tag-icon-color"></i>&nbsp;&nbsp;${tag}`;
    }
    return '';
}