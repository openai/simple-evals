import React from 'react';
import type { PickerMode } from 'rc-picker/lib/interface';
interface SuffixIconProps {
    picker?: PickerMode;
    hasFeedback?: boolean;
    feedbackIcon?: React.ReactNode;
    suffixIcon?: React.ReactNode;
}
declare const SuffixIcon: React.FC<SuffixIconProps>;
export default SuffixIcon;
