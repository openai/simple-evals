import type { ShowCollapsibleIconMode } from '../SplitBar';
import type { ItemType } from './useItems';
export type ResizableInfo = {
    resizable: boolean;
    startCollapsible: boolean;
    endCollapsible: boolean;
    showStartCollapsibleIcon: ShowCollapsibleIconMode;
    showEndCollapsibleIcon: ShowCollapsibleIconMode;
};
export default function useResizable(items: ItemType[], pxSizes: number[], isRTL: boolean): ResizableInfo[];
