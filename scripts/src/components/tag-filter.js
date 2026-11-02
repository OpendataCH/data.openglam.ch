import $ from 'jquery'
import {chain, pick, omit, filter, defaults} from 'lodash'

import TmplListGroupItem from '../templates/list-group-item'
import {setContent, slugify, createDatasetFilters, collapseListGroup} from '../util'

export default class {
  constructor (opts) {
    const tags = this._tagsWithCount(opts.datasets, opts.params)
    const tagsMarkup = tags.map(TmplListGroupItem)
    setContent(opts.el, tagsMarkup)
    collapseListGroup(opts.el)
  }

  // Given an array of datasets, returns an array of their tags with counts
  _tagsWithCount (datasets, params) {
    return chain(datasets)
      .filter('tag')
      .flatMap(function (value, index, collection) {
        // Explode objects where tag is an array into one object per tag
        if (typeof value.tag === 'string') return value
        const duplicates = []
        value.tag.forEach(function (tag) {
          duplicates.push(defaults({tag: tag}, value))
        })
        return duplicates
      })
      .groupBy('tag')
      .map(function (datasetsInTag, tag) {
        const filters = createDatasetFilters(omit(params, ['tag']))
        const filteredDatasets = filter(datasetsInTag, filters)
        const tagSlug = slugify(tag)
        const selected = params.tag && params.tag === tagSlug
        const itemParams = selected ? omit(params, 'tag') : defaults({tag: tagSlug}, params)
        return {
          title: tag,
          url: '?' + $.param(itemParams),
          count: filteredDatasets.length,
          unfilteredCount: datasetsInTag.length,
          selected: selected
        }
      })
      .orderBy('unfilteredCount', 'desc')
      .value()
  }
}
