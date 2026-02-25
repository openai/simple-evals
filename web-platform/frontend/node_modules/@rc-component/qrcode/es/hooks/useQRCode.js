import _toConsumableArray from "@babel/runtime/helpers/esm/toConsumableArray";
import { QrCode, QrSegment } from "../libs/qrcodegen";
import { ERROR_LEVEL_MAP, getImageSettings, getMarginSize } from "../utils";
import React from 'react';
export var useQRCode = function useQRCode(opt) {
  var value = opt.value,
    level = opt.level,
    minVersion = opt.minVersion,
    includeMargin = opt.includeMargin,
    marginSize = opt.marginSize,
    imageSettings = opt.imageSettings,
    size = opt.size,
    boostLevel = opt.boostLevel;
  var memoizedQrcode = React.useMemo(function () {
    var values = Array.isArray(value) ? value : [value];
    var segments = values.reduce(function (acc, val) {
      acc.push.apply(acc, _toConsumableArray(QrSegment.makeSegments(val)));
      return acc;
    }, []);
    return QrCode.encodeSegments(segments, ERROR_LEVEL_MAP[level], minVersion, undefined, undefined, boostLevel);
  }, [value, level, minVersion, boostLevel]);
  return React.useMemo(function () {
    var cs = memoizedQrcode.getModules();
    var mg = getMarginSize(includeMargin, marginSize);
    var ncs = cs.length + mg * 2;
    var cis = getImageSettings(cs, size, mg, imageSettings);
    return {
      cells: cs,
      margin: mg,
      numCells: ncs,
      calculatedImageSettings: cis,
      qrcode: memoizedQrcode
    };
  }, [memoizedQrcode, size, imageSettings, includeMargin, marginSize]);
};