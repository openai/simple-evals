import { genCompactItemStyle } from '../../style/compact-item';
import { genStyleHooks } from '../../theme/internal';
const genSpaceAddonStyle = token => {
  const {
    componentCls,
    borderRadius,
    paddingSM,
    colorBorder,
    paddingXS,
    fontSizeLG,
    fontSizeSM,
    borderRadiusLG,
    borderRadiusSM,
    colorBgContainerDisabled,
    lineWidth
  } = token;
  return {
    [componentCls]: [{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 0,
      paddingInline: paddingSM,
      margin: 0,
      background: colorBgContainerDisabled,
      borderWidth: lineWidth,
      borderStyle: 'solid',
      borderColor: colorBorder,
      borderRadius,
      '&-large': {
        fontSize: fontSizeLG,
        borderRadius: borderRadiusLG
      },
      '&-small': {
        paddingInline: paddingXS,
        borderRadius: borderRadiusSM,
        fontSize: fontSizeSM
      },
      '&-compact-last-item': {
        borderEndStartRadius: 0,
        borderStartStartRadius: 0
      },
      '&-compact-first-item': {
        borderEndEndRadius: 0,
        borderStartEndRadius: 0
      },
      '&-compact-item:not(:first-child):not(:last-child)': {
        borderRadius: 0
      },
      '&-compact-item:not(:last-child)': {
        borderInlineEndWidth: 0
      }
    }, genCompactItemStyle(token, {
      focus: false
    })]
  };
};
// ============================== Export ==============================
export default genStyleHooks(['Space', 'Addon'], token => [genSpaceAddonStyle(token)]);