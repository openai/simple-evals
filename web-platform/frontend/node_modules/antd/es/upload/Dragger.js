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
import Upload from './Upload';
const Dragger = /*#__PURE__*/React.forwardRef((props, ref) => {
  const {
      style,
      height,
      hasControlInside = false,
      children
    } = props,
    restProps = __rest(props, ["style", "height", "hasControlInside", "children"]);
  const mergedStyle = Object.assign(Object.assign({}, style), {
    height
  });
  return /*#__PURE__*/React.createElement(Upload, Object.assign({
    ref: ref,
    hasControlInside: hasControlInside
  }, restProps, {
    style: mergedStyle,
    type: "drag"
  }), children);
});
if (process.env.NODE_ENV !== 'production') {
  Dragger.displayName = 'Dragger';
}
export default Dragger;