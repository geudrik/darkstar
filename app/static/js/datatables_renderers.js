function renderDetailsExpanderColumn(data, type, row, meta) {

}

function renderToolsColumn(data, type, row, meta) {
    return `
    <div class="btn-group" role="group">
        <button type="button" class="btn btn-secondary dropdown-toggle btn-sm" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            Actions
        </button>
        <div class="dropdown-menu">
            <a class="dropdown-item" href="javascript:;" name="domainEdit">
                Edit Details
            </a>
            <a class="dropdown-item" href="javascript:;">
                ${row.enabled ? 'Disable' : 'Enable'} Resolving
            </a>
            <a class="dropdown-item" href="javascript:;">
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