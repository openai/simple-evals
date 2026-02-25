import type { SliderProps as RcSliderProps } from 'rc-slider';
import type { DirectionType } from '../config-provider';
export interface SliderInternalContextProps {
    handleRender?: RcSliderProps['handleRender'];
    direction?: DirectionType;
}
/** @private Internal context. Do not use in your production. */
declare const SliderInternalContext: import("react").Context<SliderInternalContextProps>;
export default SliderInternalContext;
