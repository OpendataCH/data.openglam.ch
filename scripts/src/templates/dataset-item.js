export default (data) => {
  const orgHtml = data.organization
    ? `<div class="dataset-organization text-secondary mb-2"><i class="fa fa-university me-1 text-muted"></i>${data.organization}</div>`
    : ''

  const hosts = Array.isArray(data.data_host) ? data.data_host : (data.data_host ? [data.data_host] : [])
  const hostBadges = hosts
    .map(h => `<span class="badge bg-white text-dark border me-1 mb-2 shadow-sm"><i class="fa fa-external-link me-1 text-muted"></i>${h}</span>`)
    .join('')

  const cats = Array.isArray(data.category) ? data.category : (data.category ? [data.category] : [])
  const catBadges = cats
    .map(c => `<span class="badge bg-white text-secondary border me-1 mb-2 shadow-sm"><i class="fa fa-tag me-1 text-muted"></i>${c}</span>`)
    .join('')

  const tags = Array.isArray(data.tag) ? data.tag : (data.tag ? [data.tag] : [])
  const tagBadges = tags
    .map(t => `<span class="badge bg-primary text-white border me-1 mb-2 shadow-sm"><i class="fa fa-tags me-1"></i>${t}</span>`)
    .join('')

  const badges = (hostBadges || catBadges || tagBadges)
    ? `<div class="dataset-meta d-flex flex-wrap align-items-center mb-2">${hostBadges}${catBadges}${tagBadges}</div>`
    : ''

  const notes = data.notes
    ? `<div class="dataset-notes text-secondary mb-0 small">${data.notes}</div>`
    : ''

  const url = data.url || '#'
  const isExternal = url.startsWith('http://') || url.startsWith('https://')
  const targetAttr = isExternal ? ' target="_blank" rel="noopener noreferrer"' : ''
  const externalIcon = isExternal ? ' <i class="fa fa-external-link text-muted ms-1" style="font-size: 0.75rem;"></i>' : ''

  return `<div class="card dataset-card border-0 bg-light shadow-sm rounded-3 mb-3">
  <div class="card-body p-4">
    <h3 class="h5 fw-bold mb-2">
      <a href="${url}"${targetAttr} class="text-dark text-decoration-none dataset-title-link">${data.title}${externalIcon}</a>
    </h3>
    ${orgHtml}
    ${badges}
    ${notes}
  </div>
</div>`
}
