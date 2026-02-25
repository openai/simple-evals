import * as React from 'react';
import type { PanelProps } from '../interface';
export type ItemType = Omit<PanelProps, 'collapsible'> & {
    collapsible: {
        start?: boolean;
        end?: boolean;
        showCollapsibleIcon: 'auto' | boolean;
    };
};
/**
 * Convert `children` into `items`.
 */
declare function useItems(children: React.ReactNode): ItemType[];
export default useItems;
