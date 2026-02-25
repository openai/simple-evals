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
import Base from './Base';
const Paragraph = /*#__PURE__*/React.forwardRef((props, ref) => {
  const {
      children
    } = props,
    restProps = __rest(props, ["children"]);
  return /*#__PURE__*/React.createElement(Base, Object.assign({
    ref: ref
  }, restProps, {
    component: "div"
  }), children);
});
export default Paragraph;