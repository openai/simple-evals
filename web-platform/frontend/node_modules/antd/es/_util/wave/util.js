export function isValidWaveColor(color) {
  return color && color !== '#fff' && color !== '#ffffff' && color !== 'rgb(255, 255, 255)' && color !== 'rgba(255, 255, 255, 1)' && !/rgba\((?:\d*, ){3}0\)/.test(color) &&
  // any transparent rgba color
  color !== 'transparent' && color !== 'canvastext';
}
export function getTargetWaveColor(node) {
  var _a;
  const {
    borderTopColor,
    borderColor,
    backgroundColor
  } = getComputedStyle(node);
  return (_a = [borderTopColor, borderColor, backgroundColor].find(isValidWaveColor)) !== null && _a !== void 0 ? _a : null;
}