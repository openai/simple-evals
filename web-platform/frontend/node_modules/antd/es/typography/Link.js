"use client";

var __rest = this && this.__rest || function (s, e) {
  var t = {};
  for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0) t[p] = s[p];
  if (s != null && typeof Object.getOwnPropertySymbols === "function") for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
    if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i])) t[p[i]] = s[p[i]];
  }
  return t;
};
import * as React from 'react';
import { devUseWarning } from '../_util/warning';
import Base from './Base';
const Link = /*#__PURE__*/React.forwardRef((props, ref) => {
  const {
      ellipsis,
      rel,
      children,
      // @ts-expect-error: https://github.com/ant-design/ant-design/issues/26622
      navigate: _navigate
    } = props,
    restProps = __rest(props, ["ellipsis", "rel", "children", "navigate"]);
  if (process.env.NODE_ENV !== 'production') {
    const warning = devUseWarning('Typography.Link');
    process.env.NODE_ENV !== "production" ? warning(typeof ellipsis !== 'object', 'usage', '`ellipsis` only supports boolean value.') : void 0;
  }
  const mergedProps = Object.assign(Object.assign({}, restProps), {
    rel: rel === undefined && restProps.target === '_blank' ? 'noopener noreferrer' : rel
  });
  return /*#__PURE__*/React.createElement(Base, Object.assign({}, mergedProps, {
    ref: ref,
    ellipsis: !!ellipsis,
    component: "a"
  }), children);
});
export default Link;