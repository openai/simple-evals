"use client";

import * as React from 'react';
import classNames from 'classnames';
import { pickClosable, useClosable } from '../_util/hooks';
import { useComponentConfig } from '../config-provider/context';
import Skeleton from '../skeleton';
const DrawerPanel = props => {
  var _a, _b;
  const {
    prefixCls,
    ariaId,
    title,
    footer,
    extra,
    closable,
    loading,
    onClose,
    headerStyle,
    bodyStyle,
    footerStyle,
    children,
    classNames: drawerClassNames,
    styles: drawerStyles
  } = props;
  const drawerContext = useComponentConfig('drawer');
  let closablePlacement;
  if (closable === false) {
    closablePlacement = undefined;
  } else if (closable === undefined || closable === true) {
    closablePlacement = 'start';
  } else {
    closablePlacement = (closable === null || closable === void 0 ? void 0 : closable.placement) === 'end' ? 'end' : 'start';
  }
  const customCloseIconRender = React.useCallback(icon => (/*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onClose,
    className: classNames(`${prefixCls}-close`, {
      [`${prefixCls}-close-${closablePlacement}`]: closablePlacement === 'end'
    })
  }, icon)), [onClose, prefixCls, closablePlacement]);
  const [mergedClosable, mergedCloseIcon] = useClosable(pickClosable(props), pickClosable(drawerContext), {
    closable: true,
    closeIconRender: customCloseIconRender
  });
  const renderHeader = () => {
    var _a, _b;
    if (!title && !mergedClosable) {
      return null;
    }
    return /*#__PURE__*/React.createElement("div", {
      style: Object.assign(Object.assign(Object.assign({}, (_a = drawerContext.styles) === null || _a === void 0 ? void 0 : _a.header), headerStyle), drawerStyles === null || drawerStyles === void 0 ? void 0 : drawerStyles.header),
      className: classNames(`${prefixCls}-header`, {
        [`${prefixCls}-header-close-only`]: mergedClosable && !title && !extra
      }, (_b = drawerContext.classNames) === null || _b === void 0 ? void 0 : _b.header, drawerClassNames === null || drawerClassNames === void 0 ? void 0 : drawerClassNames.header)
    }, /*#__PURE__*/React.createElement("div", {
      className: `${prefixCls}-header-title`
    }, closablePlacement === 'start' && mergedCloseIcon, title && (/*#__PURE__*/React.createElement("div", {
      className: `${prefixCls}-title`,
      id: ariaId
    }, title))), extra && /*#__PURE__*/React.createElement("div", {
      className: `${prefixCls}-extra`
    }, extra), closablePlacement === 'end' && mergedCloseIcon);
  };
  const renderFooter = () => {
    var _a, _b;
    if (!footer) {
      return null;
    }
    const footerClassName = `${prefixCls}-footer`;
    return /*#__PURE__*/React.createElement("div", {
      className: classNames(footerClassName, (_a = drawerContext.classNames) === null || _a === void 0 ? void 0 : _a.footer, drawerClassNames === null || drawerClassNames === void 0 ? void 0 : drawerClassNames.footer),
      style: Object.assign(Object.assign(Object.assign({}, (_b = drawerContext.styles) === null || _b === void 0 ? void 0 : _b.footer), footerStyle), drawerStyles === null || drawerStyles === void 0 ? void 0 : drawerStyles.footer)
    }, footer);
  };
  return /*#__PURE__*/React.createElement(React.Fragment, null, renderHeader(), /*#__PURE__*/React.createElement("div", {
    className: classNames(`${prefixCls}-body`, drawerClassNames === null || drawerClassNames === void 0 ? void 0 : drawerClassNames.body, (_a = drawerContext.classNames) === null || _a === void 0 ? void 0 : _a.body),
    style: Object.assign(Object.assign(Object.assign({}, (_b = drawerContext.styles) === null || _b === void 0 ? void 0 : _b.body), bodyStyle), drawerStyles === null || drawerStyles === void 0 ? void 0 : drawerStyles.body)
  }, loading ? (/*#__PURE__*/React.createElement(Skeleton, {
    active: true,
    title: false,
    paragraph: {
      rows: 5
    },
    className: `${prefixCls}-body-skeleton`
  })) : children), renderFooter());
};
export default DrawerPanel;