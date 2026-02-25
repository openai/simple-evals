import * as React from 'react';
import type { Meta, NamePath } from 'rc-field-form/lib/interface';
import type { FeedbackIcons, ValidateStatus } from '.';
export interface StatusProviderProps {
    children?: React.ReactNode;
    validateStatus?: ValidateStatus;
    prefixCls: string;
    meta: Meta;
    errors: React.ReactNode[];
    warnings: React.ReactNode[];
    hasFeedback?: boolean | {
        icons?: FeedbackIcons;
    };
    noStyle?: boolean;
    name?: NamePath;
}
export default function StatusProvider({ children, errors, warnings, hasFeedback, validateStatus, prefixCls, meta, noStyle, name, }: StatusProviderProps): React.JSX.Element;
