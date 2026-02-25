import _defineProperty from "@babel/runtime/helpers/esm/defineProperty";
import _objectSpread from "@babel/runtime/helpers/esm/objectSpread2";
import _toConsumableArray from "@babel/runtime/helpers/esm/toConsumableArray";
import _objectWithoutProperties from "@babel/runtime/helpers/esm/objectWithoutProperties";
var _excluded = ["className", "noData", "columns", "flattenColumns", "colWidths", "colGroup", "columCount", "stickyOffsets", "direction", "fixHeader", "stickyTopOffset", "stickyBottomOffset", "stickyClassName", "scrollX", "tableLayout", "onScroll", "children"];
import { useContext } from '@rc-component/context';
import classNames from 'classnames';
import { fillRef } from "rc-util/es/ref";
import * as React from 'react';
import { useMemo } from 'react';
import ColGroup from "../ColGroup";
import TableContext from "../context/TableContext";
import devRenderTimes from "../hooks/useRenderTimes";
function useColumnWidth(colWidths, columCount) {
  return useMemo(function () {
    var cloneColumns = [];
    for (var i = 0; i < columCount; i += 1) {
      var val = colWidths[i];
      if (val !== undefined) {
        cloneColumns[i] = val;
      } else {
        return null;
      }
    }
    return cloneColumns;
  }, [colWidths.join('_'), columCount]);
}
var FixedHolder = /*#__PURE__*/React.forwardRef(function (props, ref) {
  if (process.env.NODE_ENV !== 'production') {
    devRenderTimes(props);
  }
  var className = props.className,
    noData = props.noData,
    columns = props.columns,
    flattenColumns = props.flattenColumns,
    colWidths = props.colWidths,
    colGroup = props.colGroup,
    columCount = props.columCount,
    stickyOffsets = props.stickyOffsets,
    direction = props.direction,
    fixHeader = props.fixHeader,
    stickyTopOffset = props.stickyTopOffset,
    stickyBottomOffset = props.stickyBottomOffset,
    stickyClassName = props.stickyClassName,
    scrollX = props.scrollX,
    _props$tableLayout = props.tableLayout,
    tableLayout = _props$tableLayout === void 0 ? 'fixed' : _props$tableLayout,
    onScroll = props.onScroll,
    children = props.children,
    restProps = _objectWithoutProperties(props, _excluded);
  var _useContext = useContext(TableContext, ['prefixCls', 'scrollbarSize', 'isSticky', 'getComponent']),
    prefixCls = _useContext.prefixCls,
    scrollbarSize = _useContext.scrollbarSize,
    isSticky = _useContext.isSticky,
    getComponent = _useContext.getComponent;
  var TableComponent = getComponent(['header', 'table'], 'table');
  var combinationScrollBarSize = isSticky && !fixHeader ? 0 : scrollbarSize;

  // Pass wheel to scroll event
  var scrollRef = React.useRef(null);
  var setScrollRef = React.useCallback(function (element) {
    fillRef(ref, element);
    fillRef(scrollRef, element);
  }, []);
  React.useEffect(function () {
    function onWheel(e) {
      var _ref = e,
        currentTarget = _ref.currentTarget,
        deltaX = _ref.deltaX;
      if (deltaX) {
        onScroll({
          currentTarget: currentTarget,
          scrollLeft: currentTarget.scrollLeft + deltaX
        });
        e.preventDefault();
      }
    }
    var scrollEle = scrollRef.current;
    scrollEle === null || scrollEle === void 0 || scrollEle.addEventListener('wheel', onWheel, {
      passive: false
    });
    return function () {
      scrollEle === null || scrollEle === void 0 || scrollEle.removeEventListener('wheel', onWheel);
    };
  }, []);

  // Add scrollbar column
  var lastColumn = flattenColumns[flattenColumns.length - 1];
  var ScrollBarColumn = {
    fixed: lastColumn ? lastColumn.fixed : null,
    scrollbar: true,
    onHeaderCell: function onHeaderCell() {
      return {
        className: "".concat(prefixCls, "-cell-scrollbar")
      };
    }
  };
  var columnsWithScrollbar = useMemo(function () {
    return combinationScrollBarSize ? [].concat(_toConsumableArray(columns), [ScrollBarColumn]) : columns;
  }, [combinationScrollBarSize, columns]);
  var flattenColumnsWithScrollbar = useMemo(function () {
    return combinationScrollBarSize ? [].concat(_toConsumableArray(flattenColumns), [ScrollBarColumn]) : flattenColumns;
  }, [combinationScrollBarSize, flattenColumns]);

  // Calculate the sticky offsets
  var headerStickyOffsets = useMemo(function () {
    var right = stickyOffsets.right,
      left = stickyOffsets.left;
    return _objectSpread(_objectSpread({}, stickyOffsets), {}, {
      left: direction === 'rtl' ? [].concat(_toConsumableArray(left.map(function (width) {
        return width + combinationScrollBarSize;
      })), [0]) : left,
      right: direction === 'rtl' ? right : [].concat(_toConsumableArray(right.map(function (width) {
        return width + combinationScrollBarSize;
      })), [0]),
      isSticky: isSticky
    });
  }, [combinationScrollBarSize, stickyOffsets, isSticky]);
  var mergedColumnWidth = useColumnWidth(colWidths, columCount);
  var isColGroupEmpty = useMemo(function () {
    // use original ColGroup if no data or no calculated column width, otherwise use calculated column width
    // Return original colGroup if no data, or mergedColumnWidth is empty, or all widths are falsy
    var noWidth = !mergedColumnWidth || !mergedColumnWidth.length || mergedColumnWidth.every(function (w) {
      return !w;
    });
    return noData || noWidth;
  }, [noData, mergedColumnWidth]);
  return /*#__PURE__*/React.createElement("div", {
    style: _objectSpread({
      overflow: 'hidden'
    }, isSticky ? {
      top: stickyTopOffset,
      bottom: stickyBottomOffset
    } : {}),
    ref: setScrollRef,
    className: classNames(className, _defineProperty({}, stickyClassName, !!stickyClassName))
  }, /*#__PURE__*/React.createElement(TableComponent, {
    style: {
      tableLayout: tableLayout,
      minWidth: '100%',
      // https://github.com/ant-design/ant-design/issues/54894
      width: scrollX
    }
  }, isColGroupEmpty ? colGroup : /*#__PURE__*/React.createElement(ColGroup, {
    colWidths: [].concat(_toConsumableArray(mergedColumnWidth), [combinationScrollBarSize]),
    columCount: columCount + 1,
    columns: flattenColumnsWithScrollbar
  }), children(_objectSpread(_objectSpread({}, restProps), {}, {
    stickyOffsets: headerStickyOffsets,
    columns: columnsWithScrollbar,
    flattenColumns: flattenColumnsWithScrollbar
  }))));
});
if (process.env.NODE_ENV !== 'production') {
  FixedHolder.displayName = 'FixedHolder';
}

/** Return a table in div as fixed element which contains sticky info */
// export default responseImmutable(FixedHolder);
export default /*#__PURE__*/React.memo(FixedHolder);