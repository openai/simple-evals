import React from 'react';
import type { InputRef, InputProps as RcInputProps } from 'rc-input';
import { triggerFocus } from 'rc-input/lib/utils/commonUtils';
import type { InputFocusOptions } from 'rc-input/lib/utils/commonUtils';
import type { InputStatus } from '../_util/statusUtils';
import type { Variant } from '../config-provider';
import type { SizeType } from '../config-provider/SizeContext';
export type { InputFocusOptions };
export type { InputRef };
export { triggerFocus };
type SemanticName = 'prefix' | 'suffix' | 'input' | 'count';
export interface InputProps extends Omit<RcInputProps, 'wrapperClassName' | 'groupClassName' | 'inputClassName' | 'affixWrapperClassName' | 'classes'> {
    rootClassName?: string;
    size?: SizeType;
    disabled?: boolean;
    status?: InputStatus;
    /**
     * @deprecated Use `Space.Compact` instead.
     *
     * @example
     * ```tsx
     * import { Space, Input } from 'antd';
     *
     * <Space.Compact>
     *   {addon}
     *   <Input defaultValue="name" />
     * </Space.Compact>
     * ```
     */
    addonBefore?: React.ReactNode;
    /**
     * @deprecated Use `Space.Compact` instead.
     *
     * @example
     * ```tsx
     * import { Space, Input } from 'antd';
     *
     * <Space.Compact>
     *   <Input defaultValue="name" />
     *   {addon}
     * </Space.Compact>
     * ```
     */
    addonAfter?: React.ReactNode;
    /** @deprecated Use `variant="borderless"` instead. */
    bordered?: boolean;
    /**
     * @since 5.13.0
     * @default "outlined"
     */
    variant?: Variant;
    classNames?: Partial<Record<SemanticName, string>>;
    styles?: Partial<Record<SemanticName, React.CSSProperties>>;
    [key: `data-${string}`]: string | undefined;
    /** @private Skip warning of addon. Only work in dev mode */
    _skipAddonWarning?: boolean;
}
declare const Input: React.ForwardRefExoticComponent<InputProps & React.RefAttributes<InputRef>>;
export default Input;
