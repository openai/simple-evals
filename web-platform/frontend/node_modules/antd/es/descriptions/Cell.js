"use client";

import * as React from 'react';
import classnames from 'classnames';
import DescriptionsContext from './DescriptionsContext';
const isNonNullable = val => {
  return val !== undefined && val !== null;
};
const Cell = props => {
  const {
    itemPrefixCls,
    component,
    span,
    className,
    style,
    labelStyle,
    contentStyle,
    bordered,
    label,
    content,
    colon,
    type,
    styles
  } = props;
  const Component = component;
  const {
    classNames: ctxClassNames
  } = React.useContext(DescriptionsContext);
  const mergedLabelStyle = Object.assign(Object.assign({}, labelStyle), styles === null || styles === void 0 ? void 0 : styles.label);
  const mergedContentStyle = Object.assign(Object.assign({}, contentStyle), styles === null || styles === void 0 ? void 0 : styles.content);
  if (bordered) {
    return /*#__PURE__*/React.createElement(Component, {
      colSpan: span,
      style: style,
      className: classnames(className, {
        [`${itemPrefixCls}-item-${type}`]: type === 'label' || type === 'content',
        [ctxClassNames === null || ctxClassNames === void 0 ? void 0 : ctxClassNames.label]: (ctxClassNames === null || ctxClassNames === void 0 ? void 0 : ctxClassNames.label) && type === 'label',
        [ctxClassNames === null || ctxClassNames === void 0 ? void 0 : ctxClassNames.content]: (ctxClassNames === null || ctxClassNames === void 0 ? void 0 : ctxClassNames.content) && type === 'content'
      })
    }, isNonNullable(label) && /*#__PURE__*/React.createElement("span", {
      style: mergedLabelStyle
    }, label), isNonNullable(content) && /*#__PURE__*/React.createElement("span", {
      style: mergedContentStyle
    }, content));
  }
  return /*#__PURE__*/React.createElement(Component, {
    colSpan: span,
    style: style,
    className: classnames(`${itemPrefixCls}-item`, className)
  }, /*#__PURE__*/React.createElement("div", {
    className: `${itemPrefixCls}-item-container`
  }, isNonNullable(label) && (/*#__PURE__*/React.createElement("span", {
    style: mergedLabelStyle,
    className: classnames(`${itemPrefixCls}-item-label`, ctxClassNames === null || ctxClassNames === void 0 ? void 0 : ctxClassNames.label, {
      [`${itemPrefixCls}-item-no-colon`]: !colon
    })
  }, label)), isNonNullable(content) && (/*#__PURE__*/React.createElement("span", {
    style: mergedContentStyle,
    className: classnames(`${itemPrefixCls}-item-content`, ctxClassNames === null || ctxClassNames === void 0 ? void 0 : ctxClassNames.content)
  }, content))));
};
export default Cell;