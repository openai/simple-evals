import { genStyleHooks } from '../../theme/internal';
const genSpaceCompactStyle = token => {
  const {
    componentCls
  } = token;
  return {
    [componentCls]: {
      display: 'inline-flex',
      '&-block': {
        display: 'flex',
        width: '100%'
      },
      '&-vertical': {
        flexDirection: 'column'
      },
      '&-rtl': {
        direction: 'rtl'
      }
    }
  };
};
// ============================== Export ==============================
export default genStyleHooks(['Space', 'Compact'], token => [genSpaceCompactStyle(token)], () => ({}), {
  // Space component don't apply extra font style
  // https://github.com/ant-design/ant-design/issues/40315
  resetStyle: false
});