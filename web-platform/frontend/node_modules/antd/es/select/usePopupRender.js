"use client";

import React from 'react';
import ContextIsolator from '../_util/ContextIsolator';
function usePopupRender(renderFn) {
  return React.useMemo(() => {
    if (!renderFn) {
      return undefined;
    }
    return (...args) => /*#__PURE__*/React.createElement(ContextIsolator, {
      space: true
    }, renderFn.apply(void 0, args));
  }, [renderFn]);
}
export default usePopupRender;