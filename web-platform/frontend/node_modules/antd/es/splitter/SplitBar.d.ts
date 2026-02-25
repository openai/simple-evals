import React from 'react';
export type ShowCollapsibleIconMode = boolean | 'auto';
export interface SplitBarProps {
    index: number;
    active: boolean;
    prefixCls: string;
    resizable: boolean;
    startCollapsible: boolean;
    endCollapsible: boolean;
    showStartCollapsibleIcon: ShowCollapsibleIconMode;
    showEndCollapsibleIcon: ShowCollapsibleIconMode;
    onOffsetStart: (index: number) => void;
    onOffsetUpdate: (index: number, offsetX: number, offsetY: number, lazyEnd?: boolean) => void;
    onOffsetEnd: (lazyEnd?: boolean) => void;
    onCollapse: (index: number, type: 'start' | 'end') => void;
    vertical: boolean;
    ariaNow: number;
    ariaMin: number;
    ariaMax: number;
    lazy?: boolean;
    containerSize: number;
}
declare const SplitBar: React.FC<SplitBarProps>;
export default SplitBar;
