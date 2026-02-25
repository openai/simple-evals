import React from 'react';
export interface SpaceCompactCellProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    prefixCls?: string;
}
declare const SpaceAddon: React.ForwardRefExoticComponent<SpaceCompactCellProps & React.RefAttributes<HTMLDivElement>>;
export default SpaceAddon;
