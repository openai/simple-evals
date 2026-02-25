import * as React from 'react';
export interface MeasureCellProps {
    columnKey: React.Key;
    onColumnResize: (key: React.Key, width: number) => void;
    prefixCls: string;
    title?: React.ReactNode;
}
export default function MeasureCell({ columnKey, onColumnResize, prefixCls, title, }: MeasureCellProps): React.JSX.Element;
