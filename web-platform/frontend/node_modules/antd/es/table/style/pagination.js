import { unit } from '@ant-design/cssinjs';
const genPaginationStyle = token => {
  const {
    componentCls,
    antCls,
    margin
  } = token;
  return {
    [`${componentCls}-wrapper ${componentCls}-pagination${antCls}-pagination`]: {
      margin: `${unit(margin)} 0`
    }
  };
};
export default genPaginationStyle;