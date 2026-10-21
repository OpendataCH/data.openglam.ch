export default (data) => (
`<a href="${data.url}" class="list-group-item${data.selected ? ' active ' : ''} list-group-item-action d-flex justify-content-between align-items-center py-2">
  <span class="text-truncate me-2">${data.title}</span>
  <span class="d-flex align-items-center flex-shrink-0">
    ${data.selected ? '<span class="badge bg-light text-dark rounded-pill me-1"><i class="fa fa-times"></i></span>' : ''}
    <span class="badge ${data.selected ? 'bg-light text-dark' : 'bg-primary'} rounded-pill">${data.count}</span>
  </span>
</a>`
)
