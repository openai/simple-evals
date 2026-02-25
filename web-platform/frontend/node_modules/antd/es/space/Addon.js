"use client";

var __rest = this && this.__rest || function (s, e) {
  var t = {};
  for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0) t[p] = s[p];
  if (s != null && typeof Object.getOwnPropertySymbols === "function") for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
    if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i])) t[p[i]] = s[p[i]];
  }
  return t;
};
import React from 'react';
import classNames from 'classnames';
import { ConfigContext } from '../config-provider';
import { useCompactItemContext } from './Compact';
import useStyle from './style/addon';
const SpaceAddon = /*#__PURE__*/React.forwardRef((props, ref) => {
  const {
      className,
      children,
      style,
      prefixCls: customizePrefixCls
    } = props,
    restProps = __rest(props, ["className", "children", "style", "prefixCls"]);
  const {
    getPrefixCls,
    direction: directionConfig
  } = React.useContext(ConfigContext);
  const prefixCls = getPrefixCls('space-addon', customizePrefixCls);
  const [wrapCSSVar, hashId, cssVarCls] = useStyle(prefixCls);
  const {
    compactItemClassnames,
    compactSize
  } = useCompactItemContext(prefixCls, directionConfig);
  const classes = classNames(prefixCls, hashId, compactItemClassnames, cssVarCls, {
    [`${prefixCls}-${compactSize}`]: compactSize
  }, className);
  return wrapCSSVar(/*#__PURE__*/React.createElement("div", Object.assign({
    ref: ref,
    className: classes,
    style: style
  }, restProps), children));
});
export default SpaceAddon;