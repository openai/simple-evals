import classNames from 'classnames';
import { isPresetColor } from '../_util/colors';
import { generateColor } from '../color-picker/util';
export function parseColor(prefixCls, color) {
  const isInternalColor = isPresetColor(color);
  const className = classNames({
    [`${prefixCls}-${color}`]: color && isInternalColor
  });
  const overlayStyle = {};
  const arrowStyle = {};
  const rgb = generateColor(color).toRgb();
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  const textColor = luminance < 0.5 ? '#FFF' : '#000';
  if (color && !isInternalColor) {
    overlayStyle.background = color;
    overlayStyle['--ant-tooltip-color'] = textColor;
    // @ts-ignore
    arrowStyle['--antd-arrow-background-color'] = color;
  }
  return {
    className,
    overlayStyle,
    arrowStyle
  };
}