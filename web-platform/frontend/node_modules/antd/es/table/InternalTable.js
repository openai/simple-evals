"use client";

import * as React from 'react';
import classNames from 'classnames';
import { INTERNAL_HOOKS } from 'rc-table';
import { convertChildrenToColumns } from "rc-table/es/hooks/useColumns";
import omit from "rc-util/es/omit";
import { useProxyImperativeHandle } from '../_util/hooks';
import scrollTo from '../_util/scrollTo';
import { devUseWarning } from '../_util/warning';
import ConfigProvider from '../config-provider';
import { ConfigContext } from '../config-provider/context';
import DefaultRenderEmpty from '../config-provider/defaultRenderEmpty';
import useCSSVarCls from '../config-provider/hooks/useCSSVarCls';
import useSize from '../config-provider/hooks/useSize';
import useBreakpoint from '../grid/hooks/useBreakpoint';
import defaultLocale from '../locale/en_US';
import Pagination from '../pagination';
import Spin from '../spin';
import { useToken } from '../theme/internal';
import renderExpandIcon from './ExpandIcon';
import useContainerWidth from './hooks/useContainerWidth';
import useFilter, { getFilterData } from './hooks/useFilter';
import useLazyKVMap from './hooks/useLazyKVMap';
import usePagination, { DEFAULT_PAGE_SIZE, getPaginationParam } from './hooks/usePagination';
import useSelection from './hooks/useSelection';
import useSorter, { getSortData } from './hooks/useSorter';
import useTitleColumns from './hooks/useTitleColumns';
import RcTable from './RcTable';
import RcVirtualTable from './RcTable/VirtualTable';
import useStyle from './style';
const EMPTY_LIST = [];
const InternalTable = (props, ref) => {
  var _a, _b;
  const {
    prefixCls: customizePrefixCls,
    className,
    rootClassName,
    style,
    size: customizeSize,
    bordered,
    dropdownPrefixCls: customizeDropdownPrefixCls,
    dataSource,
    pagination,
    rowSelection,
    rowKey = 'key',
    rowClassName,
    columns,
    children,
    childrenColumnName: legacyChildrenColumnName,
    onChange,
    getPopupContainer,
    loading,
    expandIcon,
    expandable,
    expandedRowRender,
    expandIconColumnIndex,
    indentSize,
    scroll,
    sortDirections,
    locale,
    showSorterTooltip = {
      target: 'full-header'
    },
    virtual
  } = props;
  const warning = devUseWarning('Table');
  if (process.env.NODE_ENV !== 'production') {
    process.env.NODE_ENV !== "production" ? warning(!(typeof rowKey === 'function' && rowKey.length > 1), 'usage', '`index` parameter of `rowKey` function is deprecated. There is no guarantee that it will work as expected.') : void 0;
  }
  const baseColumns = React.useMemo(() => columns || convertChildrenToColumns(children), [columns, children]);
  const needResponsive = React.useMemo(() => baseColumns.some(col => col.responsive), [baseColumns]);
  const screens = useBreakpoint(needResponsive);
  const mergedColumns = React.useMemo(() => {
    const matched = new Set(Object.keys(screens).filter(m => screens[m]));
    return baseColumns.filter(c => !c.responsive || c.responsive.some(r => matched.has(r)));
  }, [baseColumns, screens]);
  const tableProps = omit(props, ['className', 'style', 'columns']);
  const {
    locale: contextLocale = defaultLocale,
    direction,
    table,
    renderEmpty,
    getPrefixCls,
    getPopupContainer: getContextPopupContainer
  } = React.useContext(ConfigContext);
  const mergedSize = useSize(customizeSize);
  const tableLocale = Object.assign(Object.assign({}, contextLocale.Table), locale);
  const rawData = dataSource || EMPTY_LIST;
  const prefixCls = getPrefixCls('table', customizePrefixCls);
  const dropdownPrefixCls = getPrefixCls('dropdown', customizeDropdownPrefixCls);
  const [, token] = useToken();
  const rootCls = useCSSVarCls(prefixCls);
  const [wrapCSSVar, hashId, cssVarCls] = useStyle(prefixCls, rootCls);
  const mergedExpandable = Object.assign(Object.assign({
    childrenColumnName: legacyChildrenColumnName,
    expandIconColumnIndex
  }, expandable), {
    expandIcon: (_a = expandable === null || expandable === void 0 ? void 0 : expandable.expandIcon) !== null && _a !== void 0 ? _a : (_b = table === null || table === void 0 ? void 0 : table.expandable) === null || _b === void 0 ? void 0 : _b.expandIcon
  });
  const {
    childrenColumnName = 'children'
  } = mergedExpandable;
  const expandType = React.useMemo(() => {
    if (rawData.some(item => item === null || item === void 0 ? void 0 : item[childrenColumnName])) {
      return 'nest';
    }
    if (expandedRowRender || (expandable === null || expandable === void 0 ? void 0 : expandable.expandedRowRender)) {
      return 'row';
    }
    return null;
  }, [rawData]);
  const internalRefs = {
    body: React.useRef(null)
  };
  // ============================ Width =============================
  const getContainerWidth = useContainerWidth(prefixCls);
  // ============================= Refs =============================
  const rootRef = React.useRef(null);
  const tblRef = React.useRef(null);
  useProxyImperativeHandle(ref, () => Object.assign(Object.assign({}, tblRef.current), {
    nativeElement: rootRef.current
  }));
  // ============================ RowKey ============================
  const getRowKey = React.useMemo(() => {
    if (typeof rowKey === 'function') {
      return rowKey;
    }
    return record => record === null || record === void 0 ? void 0 : record[rowKey];
  }, [rowKey]);
  const [getRecordByKey] = useLazyKVMap(rawData, childrenColumnName, getRowKey);
  // ============================ Events =============================
  const changeEventInfo = {};
  const triggerOnChange = (info, action, reset = false) => {
    var _a, _b, _c, _d;
    const changeInfo = Object.assign(Object.assign({}, changeEventInfo), info);
    if (reset) {
      (_a = changeEventInfo.resetPagination) === null || _a === void 0 ? void 0 : _a.call(changeEventInfo);
      // Reset event param
      if ((_b = changeInfo.pagination) === null || _b === void 0 ? void 0 : _b.current) {
        changeInfo.pagination.current = 1;
      }
      // Trigger pagination events
      if (pagination) {
        (_c = pagination.onChange) === null || _c === void 0 ? void 0 : _c.call(pagination, 1, (_d = changeInfo.pagination) === null || _d === void 0 ? void 0 : _d.pageSize);
      }
    }
    if (scroll && scroll.scrollToFirstRowOnChange !== false && internalRefs.body.current) {
      scrollTo(0, {
        getContainer: () => internalRefs.body.current
      });
    }
    onChange === null || onChange === void 0 ? void 0 : onChange(changeInfo.pagination, changeInfo.filters, changeInfo.sorter, {
      currentDataSource: getFilterData(getSortData(rawData, changeInfo.sorterStates, childrenColumnName), changeInfo.filterStates, childrenColumnName),
      action
    });
  };
  /**
   * Controlled state in `columns` is not a good idea that makes too many code (1000+ line?) to read
   * state out and then put it back to title render. Move these code into `hooks` but still too
   * complex. We should provides Table props like `sorter` & `filter` to handle control in next big
   * version.
   */
  // ============================ Sorter =============================
  const onSorterChange = (sorter, sorterStates) => {
    triggerOnChange({
      sorter,
      sorterStates
    }, 'sort', false);
  };
  const [transformSorterColumns, sortStates, sorterTitleProps, getSorters] = useSorter({
    prefixCls,
    mergedColumns,
    onSorterChange,
    sortDirections: sortDirections || ['ascend', 'descend'],
    tableLocale,
    showSorterTooltip
  });
  const sortedData = React.useMemo(() => getSortData(rawData, sortStates, childrenColumnName), [rawData, sortStates]);
  changeEventInfo.sorter = getSorters();
  changeEventInfo.sorterStates = sortStates;
  // ============================ Filter ============================
  const onFilterChange = (filters, filterStates) => {
    triggerOnChange({
      filters,
      filterStates
    }, 'filter', true);
  };
  const [transformFilterColumns, filterStates, filters] = useFilter({
    prefixCls,
    locale: tableLocale,
    dropdownPrefixCls,
    mergedColumns,
    onFilterChange,
    getPopupContainer: getPopupContainer || getContextPopupContainer,
    rootClassName: classNames(rootClassName, rootCls)
  });
  const mergedData = getFilterData(sortedData, filterStates, childrenColumnName);
  changeEventInfo.filters = filters;
  changeEventInfo.filterStates = filterStates;
  // ============================ Column ============================
  const columnTitleProps = React.useMemo(() => {
    const mergedFilters = {};
    Object.keys(filters).forEach(filterKey => {
      if (filters[filterKey] !== null) {
        mergedFilters[filterKey] = filters[filterKey];
      }
    });
    return Object.assign(Object.assign({}, sorterTitleProps), {
      filters: mergedFilters
    });
  }, [sorterTitleProps, filters]);
  const [transformTitleColumns] = useTitleColumns(columnTitleProps);
  // ========================== Pagination ==========================
  const onPaginationChange = (current, pageSize) => {
    triggerOnChange({
      pagination: Object.assign(Object.assign({}, changeEventInfo.pagination), {
        current,
        pageSize
      })
    }, 'paginate');
  };
  const [mergedPagination, resetPagination] = usePagination(mergedData.length, onPaginationChange, pagination);
  changeEventInfo.pagination = pagination === false ? {} : getPaginationParam(mergedPagination, pagination);
  changeEventInfo.resetPagination = resetPagination;
  // ============================= Data =============================
  const pageData = React.useMemo(() => {
    if (pagination === false || !mergedPagination.pageSize) {
      return mergedData;
    }
    const {
      current = 1,
      total,
      pageSize = DEFAULT_PAGE_SIZE
    } = mergedPagination;
    process.env.NODE_ENV !== "production" ? warning(current > 0, 'usage', '`current` should be positive number.') : void 0;
    // Dynamic table data
    if (mergedData.length < total) {
      if (mergedData.length > pageSize) {
        process.env.NODE_ENV !== "production" ? warning(false, 'usage', '`dataSource` length is less than `pagination.total` but large than `pagination.pageSize`. Please make sure your config correct data with async mode.') : void 0;
        return mergedData.slice((current - 1) * pageSize, current * pageSize);
      }
      return mergedData;
    }
    return mergedData.slice((current - 1) * pageSize, current * pageSize);
  }, [!!pagination, mergedData, mergedPagination === null || mergedPagination === void 0 ? void 0 : mergedPagination.current, mergedPagination === null || mergedPagination === void 0 ? void 0 : mergedPagination.pageSize, mergedPagination === null || mergedPagination === void 0 ? void 0 : mergedPagination.total]);
  // ========================== Selections ==========================
  const [transformSelectionColumns, selectedKeySet] = useSelection({
    prefixCls,
    data: mergedData,
    pageData,
    getRowKey,
    getRecordByKey,
    expandType,
    childrenColumnName,
    locale: tableLocale,
    getPopupContainer: getPopupContainer || getContextPopupContainer
  }, rowSelection);
  const internalRowClassName = (record, index, indent) => {
    let mergedRowClassName;
    if (typeof rowClassName === 'function') {
      mergedRowClassName = classNames(rowClassName(record, index, indent));
    } else {
      mergedRowClassName = classNames(rowClassName);
    }
    return classNames({
      [`${prefixCls}-row-selected`]: selectedKeySet.has(getRowKey(record, index))
    }, mergedRowClassName);
  };
  // ========================== Expandable ==========================
  // Pass origin render status into `rc-table`, this can be removed when refactor with `rc-table`
  mergedExpandable.__PARENT_RENDER_ICON__ = mergedExpandable.expandIcon;
  // Customize expandable icon
  mergedExpandable.expandIcon = mergedExpandable.expandIcon || expandIcon || renderExpandIcon(tableLocale);
  // Adjust expand icon index, no overwrite expandIconColumnIndex if set.
  if (expandType === 'nest' && mergedExpandable.expandIconColumnIndex === undefined) {
    mergedExpandable.expandIconColumnIndex = rowSelection ? 1 : 0;
  } else if (mergedExpandable.expandIconColumnIndex > 0 && rowSelection) {
    mergedExpandable.expandIconColumnIndex -= 1;
  }
  // Indent size
  if (typeof mergedExpandable.indentSize !== 'number') {
    mergedExpandable.indentSize = typeof indentSize === 'number' ? indentSize : 15;
  }
  // ============================ Render ============================
  const transformColumns = React.useCallback(innerColumns => transformTitleColumns(transformSelectionColumns(transformFilterColumns(transformSorterColumns(innerColumns)))), [transformSorterColumns, transformFilterColumns, transformSelectionColumns]);
  const getPaginationNodes = () => {
    if (pagination === false || !(mergedPagination === null || mergedPagination === void 0 ? void 0 : mergedPagination.total)) {
      return {};
    }
    const getPaginationSize = () => mergedPagination.size || (mergedSize === 'small' || mergedSize === 'middle' ? 'small' : undefined);
    const renderPagination = position => {
      const align = position === 'left' ? 'start' : position === 'right' ? 'end' : position;
      return /*#__PURE__*/React.createElement(Pagination, Object.assign({}, mergedPagination, {
        align: mergedPagination.align || align,
        className: classNames(`${prefixCls}-pagination`, mergedPagination.className),
        size: getPaginationSize()
      }));
    };
    const defaultPosition = direction === 'rtl' ? 'left' : 'right';
    const positions = mergedPagination.position;
    if (positions === null || !Array.isArray(positions)) {
      return {
        bottom: renderPagination(defaultPosition)
      };
    }
    const topPosition = positions.find(pos => typeof pos === 'string' && pos.toLowerCase().includes('top'));
    const bottomPosition = positions.find(pos => typeof pos === 'string' && pos.toLowerCase().includes('bottom'));
    const isNone = positions.every(pos => `${pos}` === 'none');
    const topAlign = topPosition ? topPosition.toLowerCase().replace('top', '') : '';
    const bottomAlign = bottomPosition ? bottomPosition.toLowerCase().replace('bottom', '') : '';
    const shouldDefaultBottom = !topPosition && !bottomPosition && !isNone;
    const renderTop = () => topAlign ? renderPagination(topAlign) : undefined;
    const renderBottom = () => {
      if (bottomAlign) {
        return renderPagination(bottomAlign);
      }
      if (shouldDefaultBottom) {
        return renderPagination(defaultPosition);
      }
      return undefined;
    };
    return {
      top: renderTop(),
      bottom: renderBottom()
    };
  };
  // >>>>>>>>> Spinning
  const spinProps = React.useMemo(() => {
    if (typeof loading === 'boolean') {
      return {
        spinning: loading
      };
    } else if (typeof loading === 'object' && loading !== null) {
      return Object.assign({
        spinning: true
      }, loading);
    } else {
      return undefined;
    }
  }, [loading]);
  const wrapperClassNames = classNames(cssVarCls, rootCls, `${prefixCls}-wrapper`, table === null || table === void 0 ? void 0 : table.className, {
    [`${prefixCls}-wrapper-rtl`]: direction === 'rtl'
  }, className, rootClassName, hashId);
  const mergedStyle = Object.assign(Object.assign({}, table === null || table === void 0 ? void 0 : table.style), style);
  // ========== empty ==========
  const mergedEmptyNode = React.useMemo(() => {
    // When dataSource is null/undefined (detected by reference equality with EMPTY_LIST),
    // and the table is in a loading state, we only show the loading spinner without the empty placeholder.
    // For empty arrays (datasource={[]}), both loading and empty states would normally be shown.
    // discussion https://github.com/ant-design/ant-design/issues/54601#issuecomment-3158091383
    if ((spinProps === null || spinProps === void 0 ? void 0 : spinProps.spinning) && rawData === EMPTY_LIST) {
      return null;
    }
    if (typeof (locale === null || locale === void 0 ? void 0 : locale.emptyText) !== 'undefined') {
      return locale.emptyText;
    }
    return (renderEmpty === null || renderEmpty === void 0 ? void 0 : renderEmpty('Table')) || /*#__PURE__*/React.createElement(DefaultRenderEmpty, {
      componentName: "Table"
    });
  }, [spinProps === null || spinProps === void 0 ? void 0 : spinProps.spinning, rawData, locale === null || locale === void 0 ? void 0 : locale.emptyText, renderEmpty]);
  // ========================== Render ==========================
  const TableComponent = virtual ? RcVirtualTable : RcTable;
  // >>> Virtual Table props. We set height here since it will affect height collection
  const virtualProps = {};
  const listItemHeight = React.useMemo(() => {
    const {
      fontSize,
      lineHeight,
      lineWidth,
      padding,
      paddingXS,
      paddingSM
    } = token;
    const fontHeight = Math.floor(fontSize * lineHeight);
    switch (mergedSize) {
      case 'middle':
        return paddingSM * 2 + fontHeight + lineWidth;
      case 'small':
        return paddingXS * 2 + fontHeight + lineWidth;
      default:
        return padding * 2 + fontHeight + lineWidth;
    }
  }, [token, mergedSize]);
  if (virtual) {
    virtualProps.listItemHeight = listItemHeight;
  }
  const {
    top: topPaginationNode,
    bottom: bottomPaginationNode
  } = getPaginationNodes();
  return wrapCSSVar(/*#__PURE__*/React.createElement("div", {
    ref: rootRef,
    className: wrapperClassNames,
    style: mergedStyle
  }, /*#__PURE__*/React.createElement(Spin, Object.assign({
    spinning: false
  }, spinProps), topPaginationNode, /*#__PURE__*/React.createElement(TableComponent, Object.assign({}, virtualProps, tableProps, {
    ref: tblRef,
    columns: mergedColumns,
    direction: direction,
    expandable: mergedExpandable,
    prefixCls: prefixCls,
    className: classNames({
      [`${prefixCls}-middle`]: mergedSize === 'middle',
      [`${prefixCls}-small`]: mergedSize === 'small',
      [`${prefixCls}-bordered`]: bordered,
      [`${prefixCls}-empty`]: rawData.length === 0
    }, cssVarCls, rootCls, hashId),
    data: pageData,
    rowKey: getRowKey,
    rowClassName: internalRowClassName,
    emptyText: mergedEmptyNode,
    // Internal
    internalHooks: INTERNAL_HOOKS,
    internalRefs: internalRefs,
    transformColumns: transformColumns,
    getContainerWidth: getContainerWidth,
    measureRowRender: measureRow => (/*#__PURE__*/React.createElement(ConfigProvider, {
      getPopupContainer: node => node
    }, measureRow))
  })), bottomPaginationNode)));
};
export default /*#__PURE__*/React.forwardRef(InternalTable);