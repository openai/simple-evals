import * as React from 'react';
import type { InputProps, InputRef } from './Input';
interface VisibilityToggle {
    visible?: boolean;
    onVisibleChange?: (visible: boolean) => void;
}
export interface PasswordProps extends InputProps {
    readonly inputPrefixCls?: string;
    readonly action?: 'click' | 'hover';
    visibilityToggle?: boolean | VisibilityToggle;
    /**
     * @since 5.27.0
     */
    suffix?: React.ReactNode;
    iconRender?: (visible: boolean) => React.ReactNode;
}
declare const Password: React.ForwardRefExoticComponent<PasswordProps & React.RefAttributes<InputRef>>;
export default Password;
