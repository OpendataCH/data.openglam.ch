import $ from 'jquery'
import {chain, pick, omit, filter, defaults} from 'lodash'

import TmplListGroupItem from '../templates/list-group-item'
import {setContent, slugify, createDatasetFilters, collapseListGroup} from '../util'

export default class {
  constructor (opts) {
    const dataHosts = this._dataHostsWithCount(opts.datasets, opts.params)
    const dataHostsMarkup = dataHosts.map(TmplListGroupItem)
    setContent(opts.el, dataHostsMarkup)
    collapseListGroup(opts.el)
  }

  // Given an array of datasets, returns an array of their data_hosts with counts
  _dataHostsWithCount (datasets, params) {
    return chain(datasets)
      .filter('data_host')
      .flatMap(function (value, index, collection) {
        // Explode objects where data_host is an array into one object per data_host
        if (typeof value.data_host === 'string') return value
        const duplicates = []
        value.data_host.forEach(function (dataHost) {
          duplicates.push(defaults({data_host: dataHost}, value))
        })
        return duplicates
      })
      .groupBy('data_host')
      .map(function (datasetsInHost, dataHost) {
        const filters = createDatasetFilters(omit(params, ['data_host']))
        const filteredDatasets = filter(datasetsInHost, filters)
        const dataHostSlug = slugify(dataHost)
        const selected = params.data_host && params.data_host === dataHostSlug
        const itemParams = selected ? omit(params, 'data_host') : defaults({data_host: dataHostSlug}, params)
        return {
          title: dataHost,
          url: '?' + $.param(itemParams),
          count: filteredDatasets.length,
          unfilteredCount: datasetsInHost.length,
          selected: selected
        }
      })
      .orderBy('unfilteredCount', 'desc')
      .value()
  }
}
