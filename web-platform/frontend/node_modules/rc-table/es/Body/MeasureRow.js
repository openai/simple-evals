import * as React from 'react';
import ResizeObserver from 'rc-resize-observer';
import MeasureCell from "./MeasureCell";
import isVisible from "rc-util/es/Dom/isVisible";
import { useContext } from '@rc-component/context';
import TableContext from "../context/TableContext";
export default function MeasureRow(_ref) {
  var prefixCls = _ref.prefixCls,
    columnsKey = _ref.columnsKey,
    onColumnResize = _ref.onColumnResize,
    columns = _ref.columns;
  var ref = React.useRef(null);
  var _useContext = useContext(TableContext, ['measureRowRender']),
    measureRowRender = _useContext.measureRowRender;
  var measureRow = /*#__PURE__*/React.createElement("tr", {
    "aria-hidden": "true",
    className: "".concat(prefixCls, "-measure-row"),
    ref: ref,
    tabIndex: -1
  }, /*#__PURE__*/React.createElement(ResizeObserver.Collection, {
    onBatchResize: function onBatchResize(infoList) {
      if (isVisible(ref.current)) {
        infoList.forEach(function (_ref2) {
          var columnKey = _ref2.data,
            size = _ref2.size;
          onColumnResize(columnKey, size.offsetWidth);
        });
      }
    }
  }, columnsKey.map(function (columnKey) {
    var column = columns.find(function (col) {
      return col.key === columnKey;
    });
    var rawTitle = column === null || column === void 0 ? void 0 : column.title;
    var titleForMeasure = /*#__PURE__*/React.isValidElement(rawTitle) ? /*#__PURE__*/React.cloneElement(rawTitle, {
      ref: null
    }) : rawTitle;
    return /*#__PURE__*/React.createElement(MeasureCell, {
      prefixCls: prefixCls,
      key: columnKey,
      columnKey: columnKey,
      onColumnResize: onColumnResize,
      title: titleForMeasure
    });
  })));
  return measureRowRender ? measureRowRender(measureRow) : measureRow;
}