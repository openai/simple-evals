import * as React from 'react';
import type { InputNumberProps as RcInputNumberProps, InputNumberRef as RcInputNumberRef, ValueType } from 'rc-input-number';
import type { InputStatus } from '../_util/statusUtils';
import type { Variant } from '../config-provider';
import type { SizeType } from '../config-provider/SizeContext';
export interface InputNumberProps<T extends ValueType = ValueType> extends Omit<RcInputNumberProps<T>, 'prefix' | 'size' | 'controls'> {
    prefixCls?: string;
    rootClassName?: string;
    /**
     * @deprecated Use `Space.Compact` instead.
     *
     * @example
     * ```tsx
     * import { Space, InputNumber } from 'antd';
     *
     * <Space.Compact>
     *   {addon}
     *   <InputNumber defaultValue={1} />
     * </Space.Compact>
     * ```
     */
    addonBefore?: React.ReactNode;
    /**
     * @deprecated Use `Space.Compact` instead.
     *
     * @example
     * ```tsx
     * import { Space, InputNumber } from 'antd';
     *
     * <Space.Compact>
     *   <InputNumber defaultValue={1} />
     *   {addon}
     * </Space.Compact>
     * ```
     */
    addonAfter?: React.ReactNode;
    prefix?: React.ReactNode;
    suffix?: React.ReactNode;
    size?: SizeType;
    disabled?: boolean;
    /** @deprecated Use `variant` instead. */
    bordered?: boolean;
    status?: InputStatus;
    controls?: boolean | {
        upIcon?: React.ReactNode;
        downIcon?: React.ReactNode;
    };
    /**
     * @since 5.13.0
     * @default "outlined"
     */
    variant?: Variant;
}
declare const TypedInputNumber: (<T extends ValueType = ValueType>(props: React.PropsWithChildren<InputNumberProps<T>> & React.RefAttributes<RcInputNumberRef>) => React.ReactElement) & {
    displayName?: string;
    _InternalPanelDoNotUseOrYouWillBeFired: typeof PureInputNumber;
};
/** @private Internal Component. Do not use in your production. */
declare const PureInputNumber: React.FC<InputNumberProps>;
export default TypedInputNumber;
