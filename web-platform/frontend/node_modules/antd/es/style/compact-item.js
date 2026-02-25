// handle border collapse
function compactItemBorder(token, parentCls, options, prefixCls) {
  const {
    focusElCls,
    focus,
    borderElCls
  } = options;
  const childCombinator = borderElCls ? '> *' : '';
  const hoverEffects = ['hover', focus ? 'focus' : null, 'active'].filter(Boolean).map(n => `&:${n} ${childCombinator}`).join(',');
  return {
    [`&-item:not(${parentCls}-last-item)`]: {
      marginInlineEnd: token.calc(token.lineWidth).mul(-1).equal()
    },
    [`&-item:not(${prefixCls}-status-success)`]: {
      zIndex: 2
    },
    '&-item': Object.assign(Object.assign({
      [hoverEffects]: {
        zIndex: 3
      }
    }, focusElCls ? {
      [`&${focusElCls}`]: {
        zIndex: 3
      }
    } : {}), {
      [`&[disabled] ${childCombinator}`]: {
        zIndex: 0
      }
    })
  };
}
// handle border-radius
function compactItemBorderRadius(prefixCls, parentCls, options) {
  const {
    borderElCls
  } = options;
  const childCombinator = borderElCls ? `> ${borderElCls}` : '';
  return {
    [`&-item:not(${parentCls}-first-item):not(${parentCls}-last-item) ${childCombinator}`]: {
      borderRadius: 0
    },
    [`&-item:not(${parentCls}-last-item)${parentCls}-first-item`]: {
      [`& ${childCombinator}, &${prefixCls}-sm ${childCombinator}, &${prefixCls}-lg ${childCombinator}`]: {
        borderStartEndRadius: 0,
        borderEndEndRadius: 0
      }
    },
    [`&-item:not(${parentCls}-first-item)${parentCls}-last-item`]: {
      [`& ${childCombinator}, &${prefixCls}-sm ${childCombinator}, &${prefixCls}-lg ${childCombinator}`]: {
        borderStartStartRadius: 0,
        borderEndStartRadius: 0
      }
    }
  };
}
export function genCompactItemStyle(token, options = {
  focus: true
}) {
  const {
    componentCls
  } = token;
  const {
    componentCls: customizePrefixCls
  } = options;
  const mergedComponentCls = customizePrefixCls || componentCls;
  const compactCls = `${mergedComponentCls}-compact`;
  return {
    [compactCls]: Object.assign(Object.assign({}, compactItemBorder(token, compactCls, options, mergedComponentCls)), compactItemBorderRadius(mergedComponentCls, compactCls, options))
  };
}