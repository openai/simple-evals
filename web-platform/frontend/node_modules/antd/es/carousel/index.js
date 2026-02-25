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
import SlickCarousel from '@ant-design/react-slick';
import classNames from 'classnames';
import { useComponentConfig } from '../config-provider/context';
import useStyle, { DotDuration } from './style';
const dotsClass = 'slick-dots';
const ArrowButton = _a => {
  var {
      currentSlide,
      slideCount
    } = _a,
    rest = __rest(_a, ["currentSlide", "slideCount"]);
  return /*#__PURE__*/React.createElement("button", Object.assign({
    type: "button"
  }, rest));
};
const Carousel = /*#__PURE__*/React.forwardRef((props, ref) => {
  const {
      dots = true,
      arrows = false,
      prevArrow,
      nextArrow,
      draggable = false,
      waitForAnimate = false,
      dotPosition = 'bottom',
      vertical = dotPosition === 'left' || dotPosition === 'right',
      rootClassName,
      className: customClassName,
      style,
      id,
      autoplay = false,
      autoplaySpeed = 3000,
      rtl
    } = props,
    otherProps = __rest(props, ["dots", "arrows", "prevArrow", "nextArrow", "draggable", "waitForAnimate", "dotPosition", "vertical", "rootClassName", "className", "style", "id", "autoplay", "autoplaySpeed", "rtl"]);
  const {
    getPrefixCls,
    direction,
    className: contextClassName,
    style: contextStyle
  } = useComponentConfig('carousel');
  const slickRef = React.useRef(null);
  const goTo = (slide, dontAnimate = false) => {
    slickRef.current.slickGoTo(slide, dontAnimate);
  };
  React.useImperativeHandle(ref, () => ({
    goTo,
    autoPlay: slickRef.current.innerSlider.autoPlay,
    innerSlider: slickRef.current.innerSlider,
    prev: slickRef.current.slickPrev,
    next: slickRef.current.slickNext
  }), [slickRef.current]);
  const {
    children,
    initialSlide = 0
  } = props;
  const count = React.Children.count(children);
  const isRTL = (rtl !== null && rtl !== void 0 ? rtl : direction === 'rtl') && !vertical;
  React.useEffect(() => {
    if (count > 0) {
      const newIndex = isRTL ? count - initialSlide - 1 : initialSlide;
      goTo(newIndex, false);
    }
  }, [count, initialSlide, isRTL]);
  const newProps = Object.assign({
    vertical,
    className: classNames(customClassName, contextClassName),
    style: Object.assign(Object.assign({}, contextStyle), style),
    autoplay: !!autoplay
  }, otherProps);
  if (newProps.effect === 'fade') {
    newProps.fade = true;
  }
  const prefixCls = getPrefixCls('carousel', newProps.prefixCls);
  const enableDots = !!dots;
  const dsClass = classNames(dotsClass, `${dotsClass}-${dotPosition}`, typeof dots === 'boolean' ? false : dots === null || dots === void 0 ? void 0 : dots.className);
  const [wrapCSSVar, hashId, cssVarCls] = useStyle(prefixCls);
  const className = classNames(prefixCls, {
    [`${prefixCls}-rtl`]: isRTL,
    [`${prefixCls}-vertical`]: newProps.vertical
  }, hashId, cssVarCls, rootClassName);
  const mergedShowDuration = autoplay && (typeof autoplay === 'object' ? autoplay.dotDuration : false);
  const dotDurationStyle = mergedShowDuration ? {
    [DotDuration]: `${autoplaySpeed}ms`
  } : {};
  return wrapCSSVar(/*#__PURE__*/React.createElement("div", {
    className: className,
    id: id,
    style: dotDurationStyle
  }, /*#__PURE__*/React.createElement(SlickCarousel, Object.assign({
    ref: slickRef
  }, newProps, {
    dots: enableDots,
    dotsClass: dsClass,
    arrows: arrows,
    prevArrow: prevArrow !== null && prevArrow !== void 0 ? prevArrow : /*#__PURE__*/React.createElement(ArrowButton, {
      "aria-label": isRTL ? 'next' : 'prev'
    }),
    nextArrow: nextArrow !== null && nextArrow !== void 0 ? nextArrow : /*#__PURE__*/React.createElement(ArrowButton, {
      "aria-label": isRTL ? 'prev' : 'next'
    }),
    draggable: draggable,
    verticalSwiping: vertical,
    autoplaySpeed: autoplaySpeed,
    waitForAnimate: waitForAnimate,
    rtl: isRTL
  }))));
});
if (process.env.NODE_ENV !== 'production') {
  Carousel.displayName = 'Carousel';
}
export default Carousel;