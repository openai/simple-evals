import * as React from 'react';
import type { ColumnType } from '../interface';
export interface MeasureRowProps {
    prefixCls: string;
    onColumnResize: (key: React.Key, width: number) => void;
    columnsKey: React.Key[];
    columns: readonly ColumnType<any>[];
}
export default function MeasureRow({ prefixCls, columnsKey, onColumnResize, columns, }: MeasureRowProps): string | number | boolean | Iterable<React.ReactNode> | React.JSX.Element;
