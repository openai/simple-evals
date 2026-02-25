"use client";

import React from 'react';
import CalendarOutlined from "@ant-design/icons/es/icons/CalendarOutlined";
import ClockCircleOutlined from "@ant-design/icons/es/icons/ClockCircleOutlined";
import { TIME } from '../generatePicker/constant';
const SuffixIcon = ({
  picker,
  hasFeedback,
  feedbackIcon,
  suffixIcon
}) => {
  if (suffixIcon === null || suffixIcon === false) {
    return null;
  }
  if (suffixIcon === true || suffixIcon === undefined) {
    return /*#__PURE__*/React.createElement(React.Fragment, null, picker === TIME ? /*#__PURE__*/React.createElement(ClockCircleOutlined, null) : /*#__PURE__*/React.createElement(CalendarOutlined, null), hasFeedback && feedbackIcon);
  }
  return suffixIcon;
};
export default SuffixIcon;