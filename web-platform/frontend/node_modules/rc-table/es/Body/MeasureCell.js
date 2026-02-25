import * as React from 'react';
import ResizeObserver from 'rc-resize-observer';
import useLayoutEffect from "rc-util/es/hooks/useLayoutEffect";
export default function MeasureCell(_ref) {
  var columnKey = _ref.columnKey,
    onColumnResize = _ref.onColumnResize,
    prefixCls = _ref.prefixCls,
    title = _ref.title;
  var cellRef = React.useRef();
  useLayoutEffect(function () {
    if (cellRef.current) {
      onColumnResize(columnKey, cellRef.current.offsetWidth);
    }
  }, []);
  return /*#__PURE__*/React.createElement(ResizeObserver, {
    data: columnKey
  }, /*#__PURE__*/React.createElement("th", {
    ref: cellRef,
    className: "".concat(prefixCls, "-measure-cell")
  }, /*#__PURE__*/React.createElement("div", {
    className: "".concat(prefixCls, "-measure-cell-content")
  }, title || '\xa0')));
}